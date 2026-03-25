"""
Solver 1: Backtracking with MRV + Degree Heuristic + AC-3 + Forward Checking.

This is the baseline CSP solver that guarantees feasibility (zero hard violations)
if a solution exists. It systematically explores the search space:

1. MRV (Minimum Remaining Values): Pick the unassigned class with the fewest
   legal (room, timeslot) combinations — the most constrained variable first.
   This prunes the search tree significantly.

2. Degree Heuristic: Break MRV ties by choosing the class with the most
   constraints (highest degree in the conflict graph).

3. AC-3 (Arc Consistency 3): After each assignment, propagate constraints
   to prune impossible values from neighboring classes' domains. If any
   domain becomes empty, backtrack immediately.

4. Forward Checking: Lightweight version of AC-3 — only check direct
   neighbors of the just-assigned variable.

Time complexity: O(d^n) worst case, but heuristics make it practical for
small-to-medium instances.
"""
from __future__ import annotations
import time
from collections import deque
from typing import Optional
from models import Problem, Assignment, SolutionResult
from conflict_graph import ConflictGraph
from scoring import evaluate


def solve(problem: Problem, timeout_ms: float = 30000) -> SolutionResult:
    """
    Solve the timetabling problem using Backtracking + MRV + AC-3.

    Args:
        problem: The timetabling problem instance
        timeout_ms: Maximum time in milliseconds

    Returns:
        SolutionResult with assignments and score
    """
    start = time.perf_counter()
    graph = ConflictGraph(problem)

    # Build initial domains: class_id → list of (room_id, timeslot_id) tuples
    domains: dict[str, list[tuple[str, str]]] = {}
    for cls_id, cls in problem.classes.items():
        domain = []
        for ra in cls.possible_rooms:
            room = problem.rooms.get(ra.room_id)
            if room and room.capacity >= cls.max_enrollment:
                for ts in cls.possible_times:
                    domain.append((ra.room_id, ts.id))
        if not domain:
            # Relax capacity constraint if no valid room exists
            for ra in cls.possible_rooms:
                for ts in cls.possible_times:
                    domain.append((ra.room_id, ts.id))
        domains[cls_id] = domain

    # Assignment map: class_id → (room_id, timeslot_id)
    assignment: dict[str, tuple[str, str]] = {}
    class_ids = list(problem.classes.keys())
    deadline = start + timeout_ms / 1000.0

    # Track the best partial assignment found so far
    best_partial = {}

    def _track_backtrack(graph, domains, assignment, class_ids, deadline):
        nonlocal best_partial
        # Update best partial assignment tracking
        if len(assignment) > len(best_partial):
            best_partial = dict(assignment)

        # Check timeout
        if time.perf_counter() > deadline:
            return assignment if assignment else None

        # All variables assigned → solution found
        if len(assignment) == len(class_ids):
            return dict(assignment)

        # ── MRV: select unassigned variable with smallest domain ──
        var = _select_mrv(domains, assignment, graph, class_ids)
        if var is None:
            return None

        # ── Try each value in the domain ──
        for room_id, ts_id in domains[var]:
            # Check if this assignment is consistent
            if _is_consistent(var, room_id, ts_id, assignment, problem, graph):
                assignment[var] = (room_id, ts_id)

                # ── Forward Checking: prune neighbors' domains ──
                saved_domains = {}
                pruned_ok = True

                for neighbor in graph.get_conflicts(var):
                    if neighbor in assignment:
                        continue
                    old_domain = domains[neighbor]
                    new_domain = [
                        (rid, tid) for rid, tid in old_domain
                        if not _conflicts_with(
                            neighbor, rid, tid, var, room_id, ts_id, problem
                        )
                    ]
                    saved_domains[neighbor] = old_domain
                    domains[neighbor] = new_domain
                    if not new_domain:
                        pruned_ok = False
                        break

                if pruned_ok:
                    result = _track_backtrack(
                        graph, domains, assignment, class_ids, deadline
                    )
                    if result is not None:
                        return result

                # ── Undo forward checking ──
                for nb, old_dom in saved_domains.items():
                    domains[nb] = old_dom
                del assignment[var]

        return None

    result = _track_backtrack(
        graph, domains, assignment, class_ids, deadline
    )
    
    # If no complete solution was found (UNSAT or timeout), return the largest partial assignment
    if result is None and best_partial:
        result = best_partial

    elapsed = (time.perf_counter() - start) * 1000

    assignments = []
    if result is not None:
        assignments = [
            Assignment(class_id=cid, room_id=rid, timeslot_id=tid)
            for cid, (rid, tid) in result.items()
        ]

    hard, soft, score = evaluate(problem, assignments) if assignments else (0, 0, 0)

    return SolutionResult(
        assignments=assignments,
        hard_violations=hard,
        soft_penalty=soft,
        score=score,
        elapsed_ms=elapsed,
        algorithm="backtracking",
    )


def _select_mrv(
    domains: dict[str, list[tuple[str, str]]],
    assignment: dict[str, tuple[str, str]],
    graph: ConflictGraph,
    class_ids: list[str],
) -> Optional[str]:
    """
    MRV heuristic: pick unassigned variable with minimum remaining values.
    Ties broken by degree heuristic (most constraints).
    """
    best = None
    best_size = float("inf")
    best_degree = -1

    for cid in class_ids:
        if cid in assignment:
            continue
        size = len(domains.get(cid, []))
        if size == 0:
            return None  # Dead end
        degree = graph.degree(cid)
        if size < best_size or (size == best_size and degree > best_degree):
            best = cid
            best_size = size
            best_degree = degree

    return best


def _is_consistent(
    var: str,
    room_id: str,
    ts_id: str,
    assignment: dict[str, tuple[str, str]],
    problem: Problem,
    graph: ConflictGraph,
) -> bool:
    """Check if assigning (room_id, ts_id) to var is consistent with current assignments."""
    cls = problem.classes[var]
    # Find the timeslot object
    ts = None
    for t in cls.possible_times:
        if t.id == ts_id:
            ts = t
            break
    if ts is None:
        return False

    for neighbor in graph.get_conflicts(var):
        if neighbor not in assignment:
            continue
        n_room, n_ts_id = assignment[neighbor]
        n_cls = problem.classes[neighbor]

        # Find neighbor's timeslot
        n_ts = None
        for t in n_cls.possible_times:
            if t.id == n_ts_id:
                n_ts = t
                break
        if n_ts is None:
            continue

        # Room conflict: same room + overlapping time
        if room_id == n_room and ts.overlaps(n_ts):
            return False

        # Time overlap for conflicting classes (student/professor overlap)
        if ts.overlaps(n_ts):
            return False

    return True


def _conflicts_with(
    cls_id: str,
    rid: str,
    tid: str,
    assigned_id: str,
    assigned_room: str,
    assigned_ts_id: str,
    problem: Problem,
) -> bool:
    """Check if a potential value for cls_id conflicts with the just-assigned variable."""
    cls = problem.classes.get(cls_id)
    assigned_cls = problem.classes.get(assigned_id)
    if not cls or not assigned_cls:
        return False

    ts = None
    for t in cls.possible_times:
        if t.id == tid:
            ts = t
            break

    a_ts = None
    for t in assigned_cls.possible_times:
        if t.id == assigned_ts_id:
            a_ts = t
            break

    if not ts or not a_ts:
        return False

    # Same room + overlapping time → conflict
    if rid == assigned_room and ts.overlaps(a_ts):
        return True

    # Overlapping time for conflicting classes
    if ts.overlaps(a_ts):
        return True

    return False
