"""
Solver 2: Min-Conflicts Local Search.

A fast heuristic solver that starts from an initial (possibly invalid) assignment
and iteratively repairs violations by reassigning the most conflicted variables.

Algorithm:
    1. Generate initial assignment (greedy: for each class, pick the
       (room, timeslot) that causes fewest conflicts with already-assigned classes).
    2. While violations exist and iteration < max_iter:
       a. Pick a random class with violations.
       b. Reassign it to the (room, timeslot) that minimizes total conflicts.
    3. Return the best assignment found.

Properties:
    - Very fast: O(max_iter × n) per iteration, n = num classes
    - No guarantee of optimality or even feasibility
    - Excellent for soft constraint optimization after a feasible solution is found
    - Target: <100ms on medium datasets (~100 classes)
"""
from __future__ import annotations
import time
import random
from models import Problem, Assignment, SolutionResult
from conflict_graph import ConflictGraph
from scoring import evaluate


def solve(
    problem: Problem,
    max_iterations: int = 5000,
    timeout_ms: float = 5000,
    seed: int = 42,
) -> SolutionResult:
    """
    Solve using Min-Conflicts local search.

    Args:
        problem: The timetabling problem
        max_iterations: Maximum repair iterations
        timeout_ms: Time limit in milliseconds
        seed: Random seed for reproducibility

    Returns:
        SolutionResult with best assignments found
    """
    start = time.perf_counter()
    rng = random.Random(seed)
    graph = ConflictGraph(problem)
    deadline = start + timeout_ms / 1000.0

    class_ids = list(problem.classes.keys())

    # ── Step 1: Greedy initial assignment ──
    assignment: dict[str, tuple[str, str]] = {}
    for cls_id in class_ids:
        cls = problem.classes[cls_id]
        best_val = None
        best_conflicts = float("inf")

        for ra in cls.possible_rooms:
            for ts in cls.possible_times:
                conflicts = _count_conflicts(
                    cls_id, ra.room_id, ts.id, assignment, problem, graph
                )
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_val = (ra.room_id, ts.id)

        if best_val:
            assignment[cls_id] = best_val
        elif cls.possible_rooms and cls.possible_times:
            assignment[cls_id] = (
                cls.possible_rooms[0].room_id,
                cls.possible_times[0].id,
            )

    # ── Step 2: Iterative repair ──
    best_assignment = dict(assignment)
    best_score = _quick_score(assignment, problem, graph)
    curve = [{"iteration": 0, "score": best_score}]

    for iteration in range(1, max_iterations + 1):
        if time.perf_counter() > deadline:
            break

        # Find all classes with conflicts
        conflicted = []
        for cls_id in class_ids:
            if cls_id not in assignment:
                continue
            rid, tid = assignment[cls_id]
            if _count_conflicts(cls_id, rid, tid, assignment, problem, graph) > 0:
                conflicted.append(cls_id)

        if not conflicted:
            break  # No violations → done

        # Pick a random conflicted class
        var = rng.choice(conflicted)
        cls = problem.classes[var]

        # Find the value that minimizes conflicts
        best_val = assignment[var]
        best_c = _count_conflicts(var, best_val[0], best_val[1], assignment, problem, graph)

        candidates = []
        for ra in cls.possible_rooms:
            for ts in cls.possible_times:
                c = _count_conflicts(var, ra.room_id, ts.id, assignment, problem, graph)
                if c < best_c:
                    best_c = c
                    candidates = [(ra.room_id, ts.id)]
                elif c == best_c:
                    candidates.append((ra.room_id, ts.id))

        if candidates:
            assignment[var] = rng.choice(candidates)

        # Track best
        current_score = _quick_score(assignment, problem, graph)
        if current_score < best_score:
            best_score = current_score
            best_assignment = dict(assignment)

        if iteration % 50 == 0:
            curve.append({"iteration": iteration, "score": current_score})

    elapsed = (time.perf_counter() - start) * 1000

    # Convert to Assignment objects
    assignments = [
        Assignment(class_id=cid, room_id=rid, timeslot_id=tid)
        for cid, (rid, tid) in best_assignment.items()
    ]
    hard, soft, score = evaluate(problem, assignments)

    return SolutionResult(
        assignments=assignments,
        hard_violations=hard,
        soft_penalty=soft,
        score=score,
        elapsed_ms=elapsed,
        algorithm="min_conflicts",
        optimization_curve=curve,
    )


def _count_conflicts(
    cls_id: str,
    room_id: str,
    ts_id: str,
    assignment: dict[str, tuple[str, str]],
    problem: Problem,
    graph: ConflictGraph,
) -> int:
    """Count how many conflicts assigning (room_id, ts_id) to cls_id would cause."""
    cls = problem.classes.get(cls_id)
    if not cls:
        return 0

    # Find timeslot object
    ts = None
    for t in cls.possible_times:
        if t.id == ts_id:
            ts = t
            break
    if ts is None:
        return 999

    conflicts = 0

    # Capacity check
    room = problem.rooms.get(room_id)
    if room and cls.max_enrollment > room.capacity:
        conflicts += 1

    # Check all neighbors in conflict graph
    for neighbor in graph.get_conflicts(cls_id):
        if neighbor not in assignment or neighbor == cls_id:
            continue
        n_room, n_ts_id = assignment[neighbor]
        n_cls = problem.classes.get(neighbor)
        if not n_cls:
            continue

        n_ts = None
        for t in n_cls.possible_times:
            if t.id == n_ts_id:
                n_ts = t
                break
        if n_ts is None:
            continue

        # Same room + overlapping time
        if room_id == n_room and ts.overlaps(n_ts):
            conflicts += 1

        # Conflicting classes with overlapping time (student/professor)
        if ts.overlaps(n_ts):
            conflicts += 1

    return conflicts


def _quick_score(
    assignment: dict[str, tuple[str, str]],
    problem: Problem,
    graph: ConflictGraph,
) -> int:
    """Fast approximate score based on conflict counts."""
    total = 0
    for cls_id, (rid, tid) in assignment.items():
        total += _count_conflicts(cls_id, rid, tid, assignment, problem, graph)
    return total
