"""
University Timetable Generator — FastAPI Backend.

Provides REST API for timetable generation using CSP solvers:
  POST /generate-timetable  — Run solver on demo or uploaded dataset
  GET  /timetable/{id}      — Retrieve stored result
  POST /compare-algorithms  — Run all 3 solvers and compare
  GET  /problem-info        — Get active problem metadata
  GET  /datasets            — List available ITC-2019 datasets
  POST /load-dataset/{name} — Load a specific dataset
"""
from __future__ import annotations
import sys
import os
import glob
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure backend dir is on path
sys.path.insert(0, os.path.dirname(__file__))

from models import Assignment, SolutionResult
from parser import generate_demo_problem, parse_itc2019_xml
from conflict_graph import ConflictGraph
from scoring import evaluate, get_violation_details
from solvers import backtracking, min_conflicts, simulated_annealing

app = FastAPI(
    title="University Timetable Generator",
    description="CSP-based timetable optimization engine with ITC-2019 support",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory storage ──
_solutions: dict[str, dict] = {}
_active_problem = None
_active_dataset_name = "demo"

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")


def _get_active_problem():
    global _active_problem
    if _active_problem is None:
        _active_problem = generate_demo_problem()
    return _active_problem


def _list_datasets():
    """List all available XML datasets in the datasets/ directory."""
    datasets = [{"name": "demo", "full_name": "Demo University (Synthetic)", "file": None}]
    if os.path.isdir(DATASETS_DIR):
        for f in sorted(os.listdir(DATASETS_DIR)):
            if f.endswith(".xml"):
                name = f.replace(".xml", "")
                # Generate a readable name from the filename
                full_name = _dataset_display_name(name)
                path = os.path.join(DATASETS_DIR, f)
                size_kb = os.path.getsize(path) // 1024
                datasets.append({"name": name, "full_name": full_name, "file": f, "size_kb": size_kb})
    return datasets


def _dataset_display_name(name: str) -> str:
    """Convert dataset filename to display name."""
    mapping = {
        "agh-fis-spr": "AGH University — Faculty of Computer Science",
        "agh-ggis-spr": "AGH University — Faculty of Geology",
        "bet-fal-spr": "Bethlehem University",
        "iku-fal-spr": "Istanbul Kültür University",
        "mary-fal-spr": "Mary University",
        "muni-fi-spr": "Masaryk University — Faculty of Informatics",
        "muni-fsps-spr": "Masaryk University — Faculty of Sports",
        "muni-pdf-spr": "Masaryk University — Faculty of Education",
        "pu-llr-spr": "Purdue University",
        "tg-fal-spr": "Thapar University",
    }
    return mapping.get(name, name.replace("-", " ").title())


# ── Request/Response schemas ──

class GenerateRequest(BaseModel):
    algorithm: str = "min_conflicts"  # backtracking | min_conflicts | simulated_annealing
    timeout_ms: float = 10000
    max_iterations: int = 5000


class TimetableResponse(BaseModel):
    id: str
    algorithm: str
    elapsed_ms: float
    hard_violations: int
    soft_penalty: int
    score: int
    assignments: list[dict]
    optimization_curve: list[dict]
    problem_info: dict
    violation_details: dict


class CompareResponse(BaseModel):
    results: list[dict]
    problem_info: dict


# ── Slot label helpers ──

SLOT_LABELS = [
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
]
SLOT_STARTS = [96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

COURSE_NAMES = [
    "CS101", "CS201", "CS301", "MATH101", "MATH201",
    "PHY101", "PHY201", "ENG101", "ENG201", "BIO101",
    "CHEM101", "HIST101", "ECO101", "PSY101", "ART101",
]

ROOM_NAMES = [
    "Hall-A", "Hall-B", "Lab-1", "Lab-2",
    "Room-101", "Room-102", "Room-201", "Room-202",
]


def _get_day_names(problem):
    """Get day names for the active problem (supports 5 or 6 day weeks)."""
    return DAY_NAMES[:problem.num_days]


def _enrich_assignments(problem, assignments):
    """Add human-readable info to assignments for the frontend."""
    enriched = []
    for a in assignments:
        cls = problem.classes.get(a.class_id)
        if not cls:
            continue

        # Find timeslot
        ts = None
        for t in cls.possible_times:
            if t.id == a.timeslot_id:
                ts = t
                break
        if ts is None and cls.possible_times:
            try:
                idx = int(a.timeslot_id)
                ts = cls.possible_times[idx]
            except (ValueError, IndexError):
                ts = cls.possible_times[0]

        room = problem.rooms.get(a.room_id)

        # Get day names
        days = []
        day_indices = []
        if ts:
            for i in range(5):
                if ts.days & (1 << i):
                    days.append(DAY_NAMES[i])
                    day_indices.append(i)

        # Get time label
        time_label = "?"
        slot_index = -1
        if ts:
            for si, ss in enumerate(SLOT_STARTS):
                if ts.start == ss:
                    time_label = SLOT_LABELS[si]
                    slot_index = si
                    break
            if slot_index == -1:
                # Approximate
                hour = ts.start * 5 // 60
                minute = (ts.start * 5) % 60
                time_label = f"{hour:02d}:{minute:02d}"
                slot_index = max(0, (hour - 8))

        # Course name — use course_id directly for real datasets
        course_name = cls.course_id

        # Room name — use actual room id for real datasets
        room_name = a.room_id

        enriched.append({
            "class_id": a.class_id,
            "course_id": cls.course_id,
            "course_name": course_name,
            "room_id": a.room_id,
            "room_name": room_name,
            "room_capacity": room.capacity if room else 0,
            "enrollment": cls.max_enrollment,
            "timeslot_id": a.timeslot_id,
            "time_label": time_label,
            "slot_index": slot_index,
            "days": days,
            "day_indices": day_indices,
        })

    return enriched


def _get_problem_info(problem):
    """Return serializable problem metadata."""
    return {
        "name": problem.name,
        "dataset": _active_dataset_name,
        "num_days": problem.num_days,
        "num_weeks": problem.num_weeks,
        "slots_per_day": problem.slots_per_day,
        "num_classes": len(problem.classes),
        "num_rooms": len(problem.rooms),
        "num_students": len(problem.students),
        "num_constraints": len(problem.constraints),
        "num_courses": len(problem.course_classes),
        "rooms": [
            {"id": r.id, "name": r.id, "capacity": r.capacity}
            for r in problem.rooms.values()
        ],
        "days": _get_day_names(problem),
        "time_slots": SLOT_LABELS,
        "courses": [
            {"id": cid, "num_classes": len(cids)}
            for cid, cids in problem.course_classes.items()
        ],
    }


# ── API Endpoints ──

@app.get("/")
async def root():
    return {"message": "University Timetable Generator API", "version": "1.0.0"}


@app.get("/datasets")
async def list_datasets():
    """List all available ITC-2019 XML datasets."""
    return {"datasets": _list_datasets(), "active": _active_dataset_name}


@app.post("/load-dataset/{name}")
async def load_dataset(name: str):
    """Load a specific dataset by name."""
    global _active_problem, _active_dataset_name
    if name == "demo":
        _active_problem = generate_demo_problem()
        _active_dataset_name = "demo"
    else:
        path = os.path.join(DATASETS_DIR, f"{name}.xml")
        if not os.path.isfile(path):
            raise HTTPException(404, f"Dataset '{name}' not found")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        _active_problem = parse_itc2019_xml(content)
        _active_dataset_name = name

    problem = _active_problem
    return {
        "message": f"Loaded dataset: {name}",
        **_get_problem_info(problem),
    }


@app.get("/problem-info")
async def get_problem_info():
    """Get metadata about the active problem."""
    problem = _get_active_problem()
    graph = ConflictGraph(problem)
    return {
        **_get_problem_info(problem),
        "conflict_graph": graph.to_dict(),
    }


@app.post("/generate-timetable", response_model=TimetableResponse)
async def generate_timetable(request: GenerateRequest):
    """
    Generate a timetable using the specified algorithm.
    Runs on the demo dataset by default.
    """
    problem = _get_active_problem()

    # Select solver
    if request.algorithm == "backtracking":
        result = backtracking.solve(problem, timeout_ms=request.timeout_ms)
    elif request.algorithm == "min_conflicts":
        result = min_conflicts.solve(
            problem,
            max_iterations=request.max_iterations,
            timeout_ms=request.timeout_ms,
        )
    elif request.algorithm == "simulated_annealing":
        result = simulated_annealing.solve(
            problem,
            max_iterations=request.max_iterations,
            timeout_ms=request.timeout_ms,
        )
    else:
        raise HTTPException(400, f"Unknown algorithm: {request.algorithm}")

    # Enrich assignments with human-readable data
    enriched = _enrich_assignments(problem, result.assignments)
    violations = get_violation_details(problem, result.assignments)

    response_data = {
        "id": result.id,
        "algorithm": result.algorithm,
        "elapsed_ms": round(result.elapsed_ms, 2),
        "hard_violations": result.hard_violations,
        "soft_penalty": result.soft_penalty,
        "score": result.score,
        "assignments": enriched,
        "optimization_curve": result.optimization_curve,
        "problem_info": _get_problem_info(problem),
        "violation_details": violations,
    }

    # Store for retrieval
    _solutions[result.id] = response_data

    return response_data


@app.get("/timetable/{timetable_id}")
async def get_timetable(timetable_id: str):
    """Retrieve a previously generated timetable by ID."""
    if timetable_id not in _solutions:
        raise HTTPException(404, "Timetable not found")
    return _solutions[timetable_id]


@app.post("/compare-algorithms", response_model=CompareResponse)
async def compare_algorithms():
    """Run all 3 algorithms on the demo dataset and compare results."""
    problem = _get_active_problem()

    results = []
    for algo_name, solver in [
        ("backtracking", backtracking),
        ("min_conflicts", min_conflicts),
        ("simulated_annealing", simulated_annealing),
    ]:
        result = solver.solve(problem)
        enriched = _enrich_assignments(problem, result.assignments)
        violations = get_violation_details(problem, result.assignments)
        data = {
            "id": result.id,
            "algorithm": algo_name,
            "elapsed_ms": round(result.elapsed_ms, 2),
            "hard_violations": result.hard_violations,
            "soft_penalty": result.soft_penalty,
            "score": result.score,
            "assignments": enriched,
            "optimization_curve": result.optimization_curve,
            "violation_details": violations,
        }
        results.append(data)
        _solutions[result.id] = data

    return {
        "results": results,
        "problem_info": _get_problem_info(problem),
    }


@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a custom ITC-2019 XML dataset."""
    global _active_problem, _active_dataset_name
    content = await file.read()
    try:
        _active_problem = parse_itc2019_xml(content)
        _active_dataset_name = file.filename or "uploaded"
        return {
            "message": "Dataset loaded successfully",
            **_get_problem_info(_active_problem),
        }
    except Exception as e:
        raise HTTPException(400, f"Failed to parse XML: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
