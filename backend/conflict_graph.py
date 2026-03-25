"""
Conflict Graph Builder.
Constructs an adjacency list where an edge between two classes means
they cannot be assigned to the same (room, timeslot) without causing a hard violation.

Conflict sources:
  1. Same course / same subpart → must not overlap
  2. Hard distribution constraints (NotOverlap, etc.)
  3. Shared students → would cause student overlap
  4. Shared professor (implicit via constraints)
"""
from __future__ import annotations
from collections import defaultdict
from models import Problem


class ConflictGraph:
    """
    Graph G = (V, E) where:
      V = set of class IDs
      E = {(c1, c2) : c1 and c2 conflict}

    Used for:
      - MRV heuristic (degree = neighbors count)
      - Fast constraint checking during search
      - Visualization in the frontend
    """

    def __init__(self, problem: Problem):
        self.adj: dict[str, set[str]] = defaultdict(set)
        self._build(problem)

    def _build(self, problem: Problem):
        class_ids = list(problem.classes.keys())

        # 1. Same-course classes conflict (they share the subpart → must not overlap)
        for course_id, cids in problem.course_classes.items():
            for i in range(len(cids)):
                for j in range(i + 1, len(cids)):
                    self._add_edge(cids[i], cids[j])

        # 2. Hard distribution constraints → mark as conflicts
        for dc in problem.constraints:
            if dc.required and dc.type in ("NotOverlap", "DifferentTime", "DifferentRoom", "DifferentDays"):
                for i in range(len(dc.class_ids)):
                    for j in range(i + 1, len(dc.class_ids)):
                        self._add_edge(dc.class_ids[i], dc.class_ids[j])

        # 3. Student overlap: if two classes belong to courses demanded by the same student
        #    Map: course_id → set of class_ids
        course_to_classes = problem.course_classes

        for student in problem.students:
            # Collect all classes from student's demanded courses
            student_classes: list[str] = []
            for cid in student.course_ids:
                student_classes.extend(course_to_classes.get(cid, []))
            # All pairs conflict
            for i in range(len(student_classes)):
                for j in range(i + 1, len(student_classes)):
                    if student_classes[i] != student_classes[j]:
                        self._add_edge(student_classes[i], student_classes[j])

    def _add_edge(self, c1: str, c2: str):
        self.adj[c1].add(c2)
        self.adj[c2].add(c1)

    def get_conflicts(self, class_id: str) -> set[str]:
        """Return set of class IDs that conflict with the given class."""
        return self.adj.get(class_id, set())

    def degree(self, class_id: str) -> int:
        """Return the number of conflicting classes (degree in conflict graph)."""
        return len(self.adj.get(class_id, set()))

    def edges(self) -> list[tuple[str, str]]:
        """Return all edges as a list of (c1, c2) tuples (each edge once)."""
        seen = set()
        result = []
        for c1, neighbors in self.adj.items():
            for c2 in neighbors:
                key = (min(c1, c2), max(c1, c2))
                if key not in seen:
                    seen.add(key)
                    result.append(key)
        return result

    def to_dict(self) -> dict:
        """Serialize for API response."""
        return {
            "nodes": list(self.adj.keys()),
            "edges": [{"source": e[0], "target": e[1]} for e in self.edges()],
            "node_degrees": {k: len(v) for k, v in self.adj.items()},
        }
