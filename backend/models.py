"""
Data models for the University Timetable Generator.
Mirrors the ITC 2019 XML schema: rooms, timeslots, classes, constraints, students.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Room:
    """A physical room with a capacity and optional travel times to other rooms."""
    id: str
    capacity: int
    travel_times: dict[str, int] = field(default_factory=dict)  # room_id → minutes


@dataclass
class TimeSlot:
    """
    A possible meeting time for a class.
    days: bitmask (Mon=1, Tue=2, Wed=4, Thu=8, Fri=16)
    start: start slot (0-based, each slot = 5 minutes from midnight)
    length: duration in slots
    weeks: bitmask of active weeks
    penalty: non-negative cost if this timeslot is selected
    """
    id: str
    days: int
    start: int
    length: int
    weeks: int = 0xFFFFFFFF
    penalty: int = 0

    @property
    def day_list(self) -> list[int]:
        """Return list of day indices (0=Mon .. 4=Fri) from bitmask."""
        return [i for i in range(7) if self.days & (1 << i)]

    @property
    def end(self) -> int:
        return self.start + self.length

    def overlaps(self, other: "TimeSlot") -> bool:
        """Check if two timeslots overlap in both days and time."""
        if not (self.days & other.days):
            return False
        if not (self.weeks & other.weeks):
            return False
        return self.start < other.end and other.start < self.end


@dataclass
class RoomAssignment:
    """A possible room for a class, with penalty."""
    room_id: str
    penalty: int = 0


@dataclass
class ClassEvent:
    """
    A class (event) that must be scheduled.
    Each class belongs to a course and has a set of possible times and rooms.
    """
    id: str
    course_id: str
    config_id: str = ""
    subpart_id: str = ""
    max_enrollment: int = 0
    parent_id: Optional[str] = None
    possible_times: list[TimeSlot] = field(default_factory=list)
    possible_rooms: list[RoomAssignment] = field(default_factory=list)


@dataclass
class DistributionConstraint:
    """
    A constraint relating multiple classes.
    type: constraint kind (e.g., 'SameTime', 'DifferentTime', 'SameRoom', 'DifferentRoom',
          'SameDays', 'DifferentDays', 'Precedence', 'NotOverlap', etc.)
    required: if True → hard constraint; if False → soft with penalty
    penalty: cost incurred if soft constraint is violated
    class_ids: IDs of classes involved
    """
    type: str
    required: bool
    penalty: int
    class_ids: list[str] = field(default_factory=list)


@dataclass
class Student:
    """A student demanding a set of courses."""
    id: str
    course_ids: list[str] = field(default_factory=list)


@dataclass
class Problem:
    """Complete timetabling problem instance."""
    name: str
    num_days: int
    slots_per_day: int
    num_weeks: int
    rooms: dict[str, Room] = field(default_factory=dict)
    classes: dict[str, ClassEvent] = field(default_factory=dict)
    constraints: list[DistributionConstraint] = field(default_factory=list)
    students: list[Student] = field(default_factory=list)

    # Derived index: course_id → list of class IDs
    course_classes: dict[str, list[str]] = field(default_factory=dict)

    def build_index(self):
        """Build derived look-up indices after parsing."""
        self.course_classes.clear()
        for cls in self.classes.values():
            self.course_classes.setdefault(cls.course_id, []).append(cls.id)


@dataclass
class Assignment:
    """An assignment of a class to a room and timeslot."""
    class_id: str
    room_id: str
    timeslot_id: str  # index into class's possible_times


@dataclass
class SolutionResult:
    """Complete solution output."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    assignments: list[Assignment] = field(default_factory=list)
    hard_violations: int = 0
    soft_penalty: int = 0
    score: int = 0
    elapsed_ms: float = 0.0
    algorithm: str = ""
    optimization_curve: list[dict] = field(default_factory=list)  # [{iteration, score}]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assignments": [
                {"class_id": a.class_id, "room_id": a.room_id, "timeslot_id": a.timeslot_id}
                for a in self.assignments
            ],
            "hard_violations": self.hard_violations,
            "soft_penalty": self.soft_penalty,
            "score": self.score,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "algorithm": self.algorithm,
            "optimization_curve": self.optimization_curve,
        }
