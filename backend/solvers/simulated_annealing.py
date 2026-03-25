"""
Solver 3: Simulated Annealing.

A metaheuristic optimizer that starts from an initial solution (seeded from
Min-Conflicts) and explores the search space by accepting worse solutions
with decreasing probability.

Algorithm:
    1. Get initial solution (greedy or from Min-Conflicts).
    2. At each iteration:
       a. Generate neighbor: randomly reassign one class.
       b. Compute Δscore = new_score - current_score.
       c. If Δscore < 0 (improvement): always accept.
       d. If Δscore ≥ 0 (worsening): accept with probability e^(-Δscore / T).
    3. Cool temperature: T *= alpha (geometric cooling).
    4. Return the best solution found across all iterations.

Properties:
    - Escapes local minima via probabilistic acceptance of worse solutions
    - Converges to near-optimal as T → 0
    - Tracks full optimization curve for visualization
    - Best for final solution quality
"""
from __future__ import annotations
import time
import math
import random
from models import Problem, Assignment, SolutionResult
from conflict_graph import ConflictGraph
from scoring import evaluate


def solve(
    problem: Problem,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.995,
    min_temp: float = 0.01,
    max_iterations: int = 10000,
    timeout_ms: float = 10000,
    seed: int = 42,
) -> SolutionResult:
    """
    Solve using Simulated Annealing.

    Args:
        problem: The timetabling problem
        initial_temp: Starting temperature
        cooling_rate: Geometric cooling factor (T *= alpha)
        min_temp: Stop when T < min_temp
        max_iterations: Maximum iterations
        timeout_ms: Time limit in milliseconds
        seed: Random seed

    Returns:
        SolutionResult with best assignments found
    """
    start = time.perf_counter()
    rng = random.Random(seed)
    graph = ConflictGraph(problem)
    deadline = start + timeout_ms / 1000.0

    class_ids = list(problem.classes.keys())

    # ── Step 1: Initial solution (greedy) ──
    current: dict[str, tuple[str, str]] = {}
    for cls_id in class_ids:
        cls = problem.classes[cls_id]
        best_val = None
        best_c = float("inf")
        for ra in cls.possible_rooms:
            for ts in cls.possible_times:
                c = _count_conflicts(cls_id, ra.room_id, ts.id, current, problem, graph)
                if c < best_c:
                    best_c = c
                    best_val = (ra.room_id, ts.id)
        if best_val:
            current[cls_id] = best_val
        elif cls.possible_rooms and cls.possible_times:
            current[cls_id] = (cls.possible_rooms[0].room_id, cls.possible_times[0].id)

    current_score = _full_score(current, problem)
    best = dict(current)
    best_score = current_score

    # ── Step 2: Simulated Annealing loop ──
    T = initial_temp
    curve = [{"iteration": 0, "score": current_score, "temperature": T}]

    for iteration in range(1, max_iterations + 1):
        if time.perf_counter() > deadline or T < min_temp:
            break

        # ── Generate neighbor: randomly reassign one class ──
        var = rng.choice(class_ids)
        cls = problem.classes[var]

        if not cls.possible_rooms or not cls.possible_times:
            continue

        # Pick random new (room, timeslot)
        new_room = rng.choice(cls.possible_rooms).room_id
        new_ts = rng.choice(cls.possible_times).id

        old_val = current.get(var)

        # Apply move
        current[var] = (new_room, new_ts)
        new_score = _full_score(current, problem)

        delta = new_score - current_score

        # ── Acceptance criterion ──
        if delta < 0:
            # Improvement: always accept
            current_score = new_score
        elif T > 0 and rng.random() < math.exp(-delta / T):
            # Worsening: accept with probability e^(-Δ/T)
            current_score = new_score
        else:
            # Reject: revert
            if old_val:
                current[var] = old_val
            else:
                del current[var]

        # Track best solution
        if current_score < best_score:
            best_score = current_score
            best = dict(current)

        # Cool down
        T *= cooling_rate

        # Record curve point periodically
        if iteration % 25 == 0:
            curve.append({
                "iteration": iteration,
                "score": current_score,
                "temperature": round(T, 4),
            })

    elapsed = (time.perf_counter() - start) * 1000

    # Final curve point
    curve.append({
        "iteration": max_iterations,
        "score": best_score,
        "temperature": round(T, 4),
    })

    # Convert best solution
    assignments = [
        Assignment(class_id=cid, room_id=rid, timeslot_id=tid)
        for cid, (rid, tid) in best.items()
    ]
    hard, soft, score = evaluate(problem, assignments)

    return SolutionResult(
        assignments=assignments,
        hard_violations=hard,
        soft_penalty=soft,
        score=score,
        elapsed_ms=elapsed,
        algorithm="simulated_annealing",
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
    """Count conflicts for greedy initialization."""
    cls = problem.classes.get(cls_id)
    if not cls:
        return 0

    ts = None
    for t in cls.possible_times:
        if t.id == ts_id:
            ts = t
            break
    if ts is None:
        return 999

    conflicts = 0
    room = problem.rooms.get(room_id)
    if room and cls.max_enrollment > room.capacity:
        conflicts += 1

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
        if room_id == n_room and ts.overlaps(n_ts):
            conflicts += 1
        if ts.overlaps(n_ts):
            conflicts += 1

    return conflicts


def _full_score(
    assignment: dict[str, tuple[str, str]],
    problem: Problem,
) -> int:
    """Compute full score using the scoring module."""
    from scoring import evaluate as eval_fn
    assigns = [
        Assignment(class_id=cid, room_id=rid, timeslot_id=tid)
        for cid, (rid, tid) in assignment.items()
    ]
    _, _, score = eval_fn(problem, assigns)
    return score
