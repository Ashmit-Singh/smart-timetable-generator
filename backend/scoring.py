"""
Scoring Function for Timetable Solutions.
Evaluates assignments against hard and soft constraints.

Score formula:
    score = hard_violations × 1000 + soft_penalty

Hard constraints (violation = each occurrence counts):
    1. Room conflict: two classes in same room at overlapping times
    2. Professor conflict: (via hard distribution constraints)
    3. Student overlap: student's classes overlap in time
    4. Capacity overflow: room capacity < class enrollment

Soft constraints (penalty = sum of penalties):
    1. Time preference penalty (from class's timeslot)
    2. Room preference penalty (from class's room assignment)
    3. Soft distribution constraint violations
"""
from __future__ import annotations
from collections import defaultdict
from models import Problem, Assignment


def evaluate(
    problem: Problem,
    assignments: list[Assignment],
) -> tuple[int, int, int]:
    """
    Evaluate a set of assignments against the problem.

    Returns:
        (hard_violations, soft_penalty, total_score)
    """
    hard = 0
    soft = 0

    # Build lookup: class_id → assignment
    assign_map: dict[str, Assignment] = {a.class_id: a for a in assignments}

    # Build reverse lookups for conflict detection
    # (room_id, timeslot_key) → list of class_ids
    room_time_map: dict[tuple[str, str], list[str]] = defaultdict(list)

    # class_id → resolved TimeSlot object
    class_timeslot = {}

    for a in assignments:
        cls = problem.classes.get(a.class_id)
        if not cls:
            continue

        # Find the actual TimeSlot object
        ts = None
        for t in cls.possible_times:
            if t.id == a.timeslot_id:
                ts = t
                break
        if ts is None and cls.possible_times:
            # Fallback: use timeslot_id as index
            try:
                idx = int(a.timeslot_id)
                ts = cls.possible_times[idx]
            except (ValueError, IndexError):
                ts = cls.possible_times[0]

        class_timeslot[a.class_id] = ts

        # Track room-time usage for conflict detection
        if ts:
            # Create a time key from the timeslot
            time_key = f"{ts.days}_{ts.start}_{ts.length}"
            room_time_map[(a.room_id, time_key)].append(a.class_id)

    # ── Hard Constraint 1: Room conflicts ──
    # Two classes in the same room at overlapping times
    room_classes: dict[str, list[str]] = defaultdict(list)
    for a in assignments:
        room_classes[a.room_id].append(a.class_id)

    for room_id, cls_ids in room_classes.items():
        for i in range(len(cls_ids)):
            for j in range(i + 1, len(cls_ids)):
                ts_i = class_timeslot.get(cls_ids[i])
                ts_j = class_timeslot.get(cls_ids[j])
                if ts_i and ts_j and ts_i.overlaps(ts_j):
                    hard += 1

    # ── Hard Constraint 2: Capacity overflow ──
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        room = problem.rooms.get(a.room_id)
        if cls and room and cls.max_enrollment > room.capacity:
            hard += 1

    # ── Hard Constraint 3: Student overlap ──
    # For each student, check if any two of their classes overlap in time
    # First, map course → assigned classes
    course_assigned: dict[str, list[str]] = defaultdict(list)
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        if cls:
            course_assigned[cls.course_id].append(a.class_id)

    for student in problem.students:
        student_class_ids = []
        for cid in student.course_ids:
            # Student takes one class from each course
            assigned = course_assigned.get(cid, [])
            if assigned:
                student_class_ids.append(assigned[0])

        for i in range(len(student_class_ids)):
            for j in range(i + 1, len(student_class_ids)):
                ts_i = class_timeslot.get(student_class_ids[i])
                ts_j = class_timeslot.get(student_class_ids[j])
                if ts_i and ts_j and ts_i.overlaps(ts_j):
                    hard += 1

    # ── Hard Constraint 4: Hard distribution constraints ──
    for dc in problem.constraints:
        if not dc.required:
            continue
        violated = _check_distribution(dc, assign_map, class_timeslot, problem)
        if violated:
            hard += 1

    # ── Soft: Time and room preference penalties ──
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        if not cls:
            continue
        # Time penalty
        ts = class_timeslot.get(a.class_id)
        if ts:
            soft += ts.penalty

        # Room penalty
        for ra in cls.possible_rooms:
            if ra.room_id == a.room_id:
                soft += ra.penalty
                break

    # ── Soft: Soft distribution constraints ──
    for dc in problem.constraints:
        if dc.required:
            continue
        violated = _check_distribution(dc, assign_map, class_timeslot, problem)
        if violated:
            soft += dc.penalty

    score = hard * 1000 + soft
    return hard, soft, score


def _check_distribution(
    dc,
    assign_map: dict[str, Assignment],
    class_timeslot: dict,
    problem: Problem,
) -> bool:
    """
    Check if a distribution constraint is violated.
    Returns True if violated.
    """
    # Get assigned info for all classes in the constraint
    infos = []
    for cid in dc.class_ids:
        a = assign_map.get(cid)
        ts = class_timeslot.get(cid)
        if a and ts:
            infos.append((cid, a, ts))

    if len(infos) < 2:
        return False

    dtype = dc.type

    if dtype == "NotOverlap":
        for i in range(len(infos)):
            for j in range(i + 1, len(infos)):
                if infos[i][2].overlaps(infos[j][2]):
                    return True

    elif dtype == "SameTime":
        base_start = infos[0][2].start
        for _, _, ts in infos[1:]:
            if ts.start != base_start:
                return True

    elif dtype == "DifferentTime":
        starts = [ts.start for _, _, ts in infos]
        if len(starts) != len(set(starts)):
            return True

    elif dtype == "SameRoom":
        base_room = infos[0][1].room_id
        for _, a, _ in infos[1:]:
            if a.room_id != base_room:
                return True

    elif dtype == "DifferentRoom":
        rooms = [a.room_id for _, a, _ in infos]
        if len(rooms) != len(set(rooms)):
            return True

    elif dtype == "SameDays":
        base_days = infos[0][2].days
        for _, _, ts in infos[1:]:
            if ts.days != base_days:
                return True

    elif dtype == "DifferentDays":
        days = [ts.days for _, _, ts in infos]
        if len(days) != len(set(days)):
            return True

    elif dtype == "Precedence":
        for i in range(len(infos) - 1):
            if infos[i][2].start >= infos[i + 1][2].start:
                return True

    return False


def get_violation_details(
    problem: Problem,
    assignments: list[Assignment],
) -> dict:
    """
    Get detailed breakdown of violations for the frontend heatmap.
    Returns per-class and per-timeslot violation info.
    """
    hard, soft, score = evaluate(problem, assignments)

    assign_map = {a.class_id: a for a in assignments}
    class_violations: dict[str, list[str]] = defaultdict(list)

    # Check each class for issues
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        room = problem.rooms.get(a.room_id)

        if cls and room and cls.max_enrollment > room.capacity:
            class_violations[a.class_id].append(
                f"Capacity overflow: {cls.max_enrollment} > {room.capacity}"
            )

    # Room conflicts
    room_classes: dict[str, list[Assignment]] = defaultdict(list)
    for a in assignments:
        room_classes[a.room_id].append(a)

    class_timeslot = {}
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        if cls:
            for t in cls.possible_times:
                if t.id == a.timeslot_id:
                    class_timeslot[a.class_id] = t
                    break
            if a.class_id not in class_timeslot and cls.possible_times:
                try:
                    idx = int(a.timeslot_id)
                    class_timeslot[a.class_id] = cls.possible_times[idx]
                except (ValueError, IndexError):
                    class_timeslot[a.class_id] = cls.possible_times[0]

    for room_id, room_assigns in room_classes.items():
        for i in range(len(room_assigns)):
            for j in range(i + 1, len(room_assigns)):
                ts_i = class_timeslot.get(room_assigns[i].class_id)
                ts_j = class_timeslot.get(room_assigns[j].class_id)
                if ts_i and ts_j and ts_i.overlaps(ts_j):
                    class_violations[room_assigns[i].class_id].append(
                        f"Room conflict with {room_assigns[j].class_id}"
                    )
                    class_violations[room_assigns[j].class_id].append(
                        f"Room conflict with {room_assigns[i].class_id}"
                    )

    return {
        "hard_violations": hard,
        "soft_penalty": soft,
        "score": score,
        "class_violations": dict(class_violations),
    }
