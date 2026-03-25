"""
ITC 2019 XML Parser + Demo problem generator.
Parses the official ITC-2019 XML format into the internal Problem model.
Also provides a synthetic demo dataset for immediate out-of-the-box testing.
"""
from __future__ import annotations
import random
from typing import Optional
from models import (
    Room, TimeSlot, RoomAssignment, ClassEvent,
    DistributionConstraint, Student, Problem,
)

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree  # fallback


# ─────────────────────────────────────────────────────────────
# ITC 2019 XML Parser
# ─────────────────────────────────────────────────────────────

def parse_itc2019_xml(xml_content: str | bytes) -> Problem:
    """
    Parse an ITC-2019 format XML string into a Problem instance.

    The XML schema:
        <problem name="..." nrDays="5" slotsPerDay="288" nrWeeks="13">
          <rooms> <room id="" capacity=""> <travel room="" value=""/> </room> </rooms>
          <courses>
            <course id="">
              <config id="">
                <subpart id="">
                  <class id="" limit="" parent="">
                    <time days="" start="" length="" weeks="" penalty=""/>
                    <room id="" penalty=""/>
                  </class>
                </subpart>
              </config>
            </course>
          </courses>
          <distributions>
            <distribution type="" required="" penalty="">
              <class id=""/>
            </distribution>
          </distributions>
          <students>
            <student id="">
              <course id=""/>
            </student>
          </students>
        </problem>
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    problem = Problem(
        name=root.get("name", "unknown"),
        num_days=int(root.get("nrDays", "5")),
        slots_per_day=int(root.get("slotsPerDay", "288")),
        num_weeks=int(root.get("nrWeeks", "13")),
    )

    # ── Parse rooms ──
    rooms_el = root.find("rooms")
    if rooms_el is not None:
        for room_el in rooms_el.findall("room"):
            rid = room_el.get("id")
            cap = int(room_el.get("capacity", "0"))
            travel = {}
            for t in room_el.findall("travel"):
                travel[t.get("room")] = int(t.get("value", "0"))
            problem.rooms[rid] = Room(id=rid, capacity=cap, travel_times=travel)

    # ── Parse courses → classes ──
    courses_el = root.find("courses")
    if courses_el is not None:
        for course_el in courses_el.findall("course"):
            course_id = course_el.get("id")
            for config_el in course_el.findall("config"):
                config_id = config_el.get("id", "")
                for subpart_el in config_el.findall("subpart"):
                    subpart_id = subpart_el.get("id", "")
                    for class_el in subpart_el.findall("class"):
                        cls_id = class_el.get("id")
                        limit = int(class_el.get("limit", "0"))
                        parent = class_el.get("parent", None)

                        possible_times = []
                        for t in class_el.findall("time"):
                            days_str = t.get("days", "0" * problem.num_days)
                            days_bitmask = int(days_str, 2) if len(days_str) > 1 else int(days_str)
                            weeks_str = t.get("weeks", "1" * problem.num_weeks)
                            weeks_bitmask = int(weeks_str, 2) if len(weeks_str) > 1 else int(weeks_str)
                            ts = TimeSlot(
                                id=f"{cls_id}_t{len(possible_times)}",
                                days=days_bitmask,
                                start=int(t.get("start", "0")),
                                length=int(t.get("length", "1")),
                                weeks=weeks_bitmask,
                                penalty=int(t.get("penalty", "0")),
                            )
                            possible_times.append(ts)

                        possible_rooms = []
                        for r in class_el.findall("room"):
                            possible_rooms.append(RoomAssignment(
                                room_id=r.get("id"),
                                penalty=int(r.get("penalty", "0")),
                            ))

                        ce = ClassEvent(
                            id=cls_id,
                            course_id=course_id,
                            config_id=config_id,
                            subpart_id=subpart_id,
                            max_enrollment=limit,
                            parent_id=parent,
                            possible_times=possible_times,
                            possible_rooms=possible_rooms,
                        )
                        problem.classes[cls_id] = ce

    # ── Parse distribution constraints ──
    dist_el = root.find("distributions")
    if dist_el is not None:
        for d in dist_el.findall("distribution"):
            dtype = d.get("type", "")
            req = d.get("required", "false").lower() == "true"
            pen = int(d.get("penalty", "0"))
            cids = [c.get("id") for c in d.findall("class")]
            problem.constraints.append(DistributionConstraint(
                type=dtype, required=req, penalty=pen, class_ids=cids,
            ))

    # ── Parse students ──
    students_el = root.find("students")
    if students_el is not None:
        for s in students_el.findall("student"):
            sid = s.get("id")
            courses = [c.get("id") for c in s.findall("course")]
            problem.students.append(Student(id=sid, course_ids=courses))

    problem.build_index()
    return problem


# ─────────────────────────────────────────────────────────────
# Demo Problem Generator
# ─────────────────────────────────────────────────────────────

COURSE_NAMES = [
    "CS101", "CS201", "CS301", "MATH101", "MATH201",
    "PHY101", "PHY201", "ENG101", "ENG201", "BIO101",
    "CHEM101", "HIST101", "ECO101", "PSY101", "ART101",
]

ROOM_NAMES = [
    "Hall-A", "Hall-B", "Lab-1", "Lab-2",
    "Room-101", "Room-102", "Room-201", "Room-202",
]

ROOM_CAPACITIES = [120, 100, 40, 40, 60, 60, 35, 35]

# 12 one-hour slots per day (8:00 AM to 8:00 PM, each 60 minutes = 12 five-min slots)
SLOT_STARTS = [96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228]
SLOT_LABELS = [
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
]


def generate_demo_problem(
    num_classes: int = 30,
    num_students: int = 60,
    seed: int = 42,
) -> Problem:
    """
    Generate a realistic synthetic timetabling problem in ITC-2019 style.
    This allows the app to work immediately without downloading external datasets.

    Args:
        num_classes: number of class events to generate (default 30)
        num_students: number of students (default 60)
        seed: random seed for reproducibility
    """
    rng = random.Random(seed)

    problem = Problem(
        name="demo-university",
        num_days=5,
        slots_per_day=288,
        num_weeks=13,
    )

    # ── Create rooms ──
    for i, (name, cap) in enumerate(zip(ROOM_NAMES, ROOM_CAPACITIES)):
        rid = f"r{i}"
        travel = {}
        for j in range(len(ROOM_NAMES)):
            if j != i:
                travel[f"r{j}"] = rng.choice([0, 5, 10])
        problem.rooms[rid] = Room(id=rid, capacity=cap, travel_times=travel)

    # ── Create classes ──
    classes_per_course = max(1, num_classes // len(COURSE_NAMES))
    class_idx = 0
    for ci, course_name in enumerate(COURSE_NAMES):
        course_id = f"c{ci}"
        n = classes_per_course if class_idx + classes_per_course <= num_classes else num_classes - class_idx
        if n <= 0:
            break
        for sec in range(n):
            cls_id = f"cl{class_idx}"
            enrollment = rng.randint(20, 80)

            # Generate possible timeslots (3-6 options per class)
            num_options = rng.randint(3, 6)
            chosen_slots = rng.sample(range(len(SLOT_STARTS)), min(num_options, len(SLOT_STARTS)))
            chosen_days = rng.sample(range(5), rng.randint(1, 3))
            day_bitmask = sum(1 << d for d in chosen_days)

            possible_times = []
            for si, slot_idx in enumerate(chosen_slots):
                ts = TimeSlot(
                    id=f"{cls_id}_t{si}",
                    days=day_bitmask,
                    start=SLOT_STARTS[slot_idx],
                    length=12,  # 60 minutes
                    penalty=rng.choice([0, 0, 0, 1, 2, 3]),  # prefer some slots
                )
                possible_times.append(ts)

            # Possible rooms: subset of rooms with sufficient capacity
            possible_rooms = []
            for rid, room in problem.rooms.items():
                if room.capacity >= enrollment:
                    possible_rooms.append(RoomAssignment(
                        room_id=rid,
                        penalty=rng.choice([0, 0, 1, 2]),
                    ))
            if not possible_rooms:
                # Fallback: allow largest rooms
                possible_rooms = [
                    RoomAssignment(room_id="r0", penalty=0),
                    RoomAssignment(room_id="r1", penalty=0),
                ]

            ce = ClassEvent(
                id=cls_id,
                course_id=course_id,
                config_id=f"cfg{ci}",
                subpart_id=f"sub{ci}_{sec}",
                max_enrollment=enrollment,
                possible_times=possible_times,
                possible_rooms=possible_rooms,
            )
            problem.classes[cls_id] = ce
            class_idx += 1

    # ── Distribution constraints ──
    class_ids = list(problem.classes.keys())

    # Same-course classes should not overlap (hard)
    for course_id, cids in problem.course_classes.items():
        if len(cids) > 1:
            problem.constraints.append(DistributionConstraint(
                type="NotOverlap", required=True, penalty=0, class_ids=cids,
            ))

    # Some random soft constraints
    for _ in range(8):
        pair = rng.sample(class_ids, 2)
        ctype = rng.choice(["SameTime", "DifferentTime", "SameDays", "DifferentDays"])
        problem.constraints.append(DistributionConstraint(
            type=ctype, required=False, penalty=rng.randint(1, 5), class_ids=pair,
        ))

    # ── Students ──
    for si in range(num_students):
        num_courses = rng.randint(3, 6)
        all_courses = list({cls.course_id for cls in problem.classes.values()})
        chosen = rng.sample(all_courses, min(num_courses, len(all_courses)))
        problem.students.append(Student(id=f"s{si}", course_ids=chosen))

    problem.build_index()
    return problem


def generate_demo_xml() -> str:
    """Generate an ITC-2019 format XML string for the demo problem."""
    problem = generate_demo_problem()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<problem name="{problem.name}" nrDays="{problem.num_days}" '
        f'slotsPerDay="{problem.slots_per_day}" nrWeeks="{problem.num_weeks}">',
        '  <rooms>',
    ]

    for room in problem.rooms.values():
        travel_attrs = "".join(
            f'    <travel room="{rid}" value="{val}"/>\n'
            for rid, val in room.travel_times.items()
        )
        if travel_attrs:
            lines.append(f'    <room id="{room.id}" capacity="{room.capacity}">')
            lines.append(travel_attrs.rstrip())
            lines.append('    </room>')
        else:
            lines.append(f'    <room id="{room.id}" capacity="{room.capacity}"/>')

    lines.append('  </rooms>')
    lines.append('  <courses>')

    # Group classes by course
    for course_id, cls_ids in problem.course_classes.items():
        lines.append(f'    <course id="{course_id}">')
        for cls_id in cls_ids:
            cls = problem.classes[cls_id]
            lines.append(f'      <config id="{cls.config_id}">')
            lines.append(f'        <subpart id="{cls.subpart_id}">')
            parent = f' parent="{cls.parent_id}"' if cls.parent_id else ""
            lines.append(f'          <class id="{cls.id}" limit="{cls.max_enrollment}"{parent}>')
            for ts in cls.possible_times:
                days_str = format(ts.days, f"0{problem.num_days}b")
                lines.append(
                    f'            <time days="{days_str}" start="{ts.start}" '
                    f'length="{ts.length}" penalty="{ts.penalty}"/>'
                )
            for ra in cls.possible_rooms:
                lines.append(f'            <room id="{ra.room_id}" penalty="{ra.penalty}"/>')
            lines.append('          </class>')
            lines.append('        </subpart>')
            lines.append('      </config>')
        lines.append('    </course>')

    lines.append('  </courses>')
    lines.append('  <distributions>')

    for dc in problem.constraints:
        req = "true" if dc.required else "false"
        class_els = "".join(f'      <class id="{cid}"/>\n' for cid in dc.class_ids)
        lines.append(f'    <distribution type="{dc.type}" required="{req}" penalty="{dc.penalty}">')
        lines.append(class_els.rstrip())
        lines.append('    </distribution>')

    lines.append('  </distributions>')
    lines.append('  <students>')

    for student in problem.students:
        course_els = "".join(f'      <course id="{cid}"/>\n' for cid in student.course_ids)
        lines.append(f'    <student id="{student.id}">')
        lines.append(course_els.rstrip())
        lines.append('    </student>')

    lines.append('  </students>')
    lines.append('</problem>')

    return "\n".join(lines)
