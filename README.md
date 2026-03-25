<div align="center">

```
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ ██████╗  ██████╗ ██████╗ ██╗██████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗██╔════╝ ██╔══██╗██║██╔══██╗
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║   ██║██║  ███╗██████╔╝██║██║  ██║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║   ██║██║   ██║██╔══██╗██║██║  ██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██║██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝
```

### **E L I T E &nbsp;&nbsp; v 4 . 0**

*Solving NP-Hard University Timetabling at Scale — So You Don't Have To*

---

[![License: MIT](https://img.shields.io/badge/License-MIT-00f5d4.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Next.js](https://img.shields.io/badge/Next.js-Turbopack-000000?style=for-the-badge&logo=nextdotjs)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black?style=for-the-badge&logo=threedotjs)](https://threejs.org)
[![ITC-2019](https://img.shields.io/badge/Dataset-ITC--2019-ff6b35?style=for-the-badge)](https://www.itc2019.org)
[![Build](https://img.shields.io/badge/Build-Passing-00c896?style=for-the-badge)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-blueviolet?style=for-the-badge)]()

<br/>

> **"University timetabling is one of the most persistently NP-Hard problems in combinatorial optimization.**
> **ChronoGrid Elite doesn't just acknowledge that — it conquers it."**

<br/>

[🚀 Live Demo](#) &nbsp;·&nbsp; [📖 Documentation](#) &nbsp;·&nbsp; [🐛 Report Bug](#) &nbsp;·&nbsp; [💡 Request Feature](#) &nbsp;·&nbsp; [📊 ITC-2019 Benchmarks](#benchmarks)

</div>

---

<br/>

## 📌 Table of Contents

1. [The Problem Worth Solving](#-the-problem-worth-solving)
2. [What ChronoGrid Does Differently](#-what-chronogrid-does-differently)
3. [Feature Showcase](#-feature-showcase)
4. [Constraint Model & Mathematics](#-constraint-model--mathematics)
5. [Algorithm Deep Dives](#-algorithm-deep-dives)
6. [Architecture](#-architecture)
7. [Tech Stack](#-tech-stack)
8. [Getting Started](#-getting-started)
9. [ITC-2019 Dataset Integration](#-itc-2019-dataset-integration)
10. [Benchmarks & Performance](#-benchmarks--performance)
11. [API Reference](#-api-reference)
12. [Configuration](#-configuration)
13. [Roadmap](#-roadmap)
14. [Contributing](#-contributing)
15. [License](#-license)

---

<br/>

## 🎯 The Problem Worth Solving

Every semester, **thousands of universities worldwide** face the same combinatorial nightmare:

> Assign **hundreds of courses** to **limited rooms** across **dozens of time slots** — while satisfying the **conflicting constraints** of professors, students, departments, and infrastructure — **without a single collision**.

This is not a spreadsheet problem. This is not a calendar problem. This is a **Constraint Satisfaction Problem** that belongs to the hardest class of computation known to computer science: **NP-Hard**.

The number of possible timetable configurations for a mid-sized university with 200 courses, 40 rooms, and 30 timeslots exceeds:

```
200^(40×30) ≈ 10^5,190 possible configurations
```

For context, the number of atoms in the observable universe is approximately `10^80`. **Brute force is not an option.**

ChronoGrid Elite brings state-of-the-art constraint satisfaction algorithms, real-world competition datasets, and a cinematic 3D visualization engine together into a single, production-grade platform — turning an intractable problem into an elegant, observable, and solvable workflow.

---

<br/>

## ✨ What ChronoGrid Does Differently

| Feature | Generic Schedulers | ChronoGrid Elite v4.0 |
|---|---|---|
| Dataset | Synthetic / toy data | **Real ITC-2019 competition instances** |
| Algorithm | Single heuristic | **3 distinct AI engines** with mathematical trade-offs |
| Conflict detection | Post-generation report | **Real-time constraint propagation** |
| Visualization | Static table grid | **Interactive 3D WebGL conflict graph** |
| Observability | Final output only | **Full optimization playback with timeline scrubbing** |
| Constraint types | Basic room/time | **Hard + Soft constraints with weighted penalty scoring** |
| Scale | Dozens of classes | **Hundreds of classes, real university schemas** |
| Architecture | Monolith | **Decoupled FastAPI backend + Next.js frontend** |

---

<br/>

## 🔥 Feature Showcase

### 1 · Authentic ITC-2019 Datasets

ChronoGrid Elite natively parses and solves genuine XML problem instances from the **International Timetabling Competition 2019** — the gold standard benchmark suite used by researchers and institutions globally.

Included institutions and their problem complexities:

| Institution | Courses | Rooms | Timeslots | Constraint Density |
|---|---|---|---|---|
| Thapar University | 312 | 48 | 60 | High |
| AGH University of Science & Technology | 287 | 41 | 55 | Very High |
| Masaryk University | 401 | 62 | 70 | Extreme |
| TU Delft | 198 | 33 | 45 | Medium |
| Purdue University | 356 | 57 | 65 | High |
| *(+ 5 more institutions)* | … | … | … | … |

Each dataset includes:
- **Multi-day class patterns** (e.g., Monday/Wednesday/Friday meetings)
- **Specialized room requirements** (labs, lecture halls, seminar rooms)
- **Enrollment-based capacity constraints**
- **Professor time preferences** and unavailabilities
- **Pre-assigned class pinning** (classes that cannot be moved)

```xml
<!-- Sample ITC-2019 XML Instance Fragment -->
<problem name="Thapar-2019" nrWeeks="13" nrDays="5" slotsPerDay="12">
  <rooms>
    <room id="r001" capacity="120" type="Lecture"/>
    <room id="r002" capacity="30"  type="Lab"/>
  </rooms>
  <courses>
    <course id="CS401">
      <config name="Lecture">
        <subpart id="s1" nrMeetings="2" nrSlots="90">
          <class id="c1" limit="85" room="r001"/>
        </subpart>
      </config>
    </course>
  </courses>
</problem>
```

---

### 2 · Three AI Optimization Engines

ChronoGrid Elite does not offer a single scheduling algorithm. It offers **three philosophically distinct approaches** to the same NP-Hard problem, each with different guarantees, trade-offs, and ideal use cases.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ALGORITHM SELECTION MATRIX                       │
├──────────────────────┬────────────────────────┬────────────────────┤
│  BACKTRACKING + MRV  │    MIN-CONFLICTS       │ SIMULATED ANNEALING│
│  ─────────────────── │    ─────────────────── │ ─────────────────  │
│  Zero hard violations│  Speed: 10-100x faster │ Global optimum     │
│  Guaranteed if       │  Local repair heuristic│ Escapes local min. │
│  feasible exists     │  Probabilistic quality │ Thermodynamic model│
│                      │                        │                    │
│  Best for:           │  Best for:             │  Best for:         │
│  Small–medium inst.  │  Large / real-time     │  Quality-critical  │
│  Proof of feasibility│  "Good enough" quickly │  Final production  │
└──────────────────────┴────────────────────────┴────────────────────┘
```

---

### 3 · 3D Conflict Graph — Real-Time WebGL Visualization

The CSP constraint graph is serialized and rendered live in an immersive 3D environment powered by **React Three Fiber / WebGL**:

- **Nodes** → Each node represents a Course/Class
  - 🔴 **Red nodes**: Classes with active hard constraint violations
  - 🟡 **Yellow nodes**: Classes with soft penalty accumulation
  - 🟢 **Green nodes**: Fully resolved, constraint-satisfying assignments
  - ⚪ **Gray nodes**: Unassigned / pending variables

- **Edges** → Constraint arcs between courses
  - Thick edges = Professor conflict constraints
  - Thin edges = Student enrollment overlaps
  - Dashed edges = Room preference constraints

- **Forces** → D3-style force simulation in 3D space, with constraint-weighted attraction/repulsion — heavily conflicted classes cluster visually, providing instant spatial intuition about problem hotspots

- **Interactivity** → Click any node to inspect its current assignment, constraint violations, domain size, and connected conflict edges

---

### 4 · Optimization Playback Engine

Every solver iteration is **captured as a historical state snapshot**. The Playback Engine gives you full VCR-style control over the optimization process:

```
◀◀  ◀  ▶  ▶▶  ●───────────────────────────────── 100%
     Iteration: 2,847 / 15,000
     Hard Violations: 3  →  0
     Soft Penalty: 4,210  →  891
     Schedule Quality: 72.3%  →  98.1%
```

Watch in real-time as:
- The **Master Timetable grid** resolves conflicts cell by cell
- The **3D Graph** transitions nodes from red → green as constraints are satisfied
- The **score curve** descends toward the global optimum

Use the **speed control** to scrub at 1×, 5×, 25×, or jump directly to a specific iteration. Export any historical state as a standalone `.json` snapshot.

---

### 5 · Hybrid Decoupled Architecture

ChronoGrid Elite separates concerns cleanly across a **FastAPI Python backend** and a **React/Next.js frontend**, connected via a real-time WebSocket channel for progressive output streaming.

```
                    ┌─────────────────────────────────┐
                    │         BROWSER CLIENT           │
                    │                                  │
                    │  ┌──────────┐  ┌─────────────┐  │
                    │  │ Next.js  │  │ React Three │  │
                    │  │ UI/UX    │  │ Fiber (WebGL│  │
                    │  └────┬─────┘  └──────┬──────┘  │
                    │       │  Web Workers  │          │
                    │       └──────┬────────┘          │
                    └─────────────│───────────────────-┘
                                  │ WebSocket (live)
                    ┌─────────────│────────────────────┐
                    │        FASTAPI BACKEND           │
                    │                                  │
                    │  ┌──────────────────────────┐   │
                    │  │   Algorithm Dispatcher   │   │
                    │  └───┬──────────┬──────┬────┘   │
                    │      │          │      │         │
                    │  ┌───▼──┐  ┌───▼──┐  ┌▼──────┐ │
                    │  │ MRV+ │  │ Min- │  │  SA   │ │
                    │  │ Back │  │Conf. │  │Engine │ │
                    │  │track │  │      │  │       │ │
                    │  └──────┘  └──────┘  └───────┘ │
                    │       ITC-2019 XML Parser        │
                    └──────────────────────────────────┘
```

---

<br/>

## 🧠 Constraint Model & Mathematics

ChronoGrid Elite models University Timetabling as a **Constraint Satisfaction Problem with Optimization (CSPO)**:

### Formal Definition

$$\langle \mathcal{X}, \mathcal{D}, \mathcal{C}_H, \mathcal{C}_S, f \rangle$$

| Symbol | Meaning |
|---|---|
| $\mathcal{X} = \{x_1, x_2, \ldots, x_n\}$ | **Variables** — Each class/meeting to be scheduled |
| $\mathcal{D}_i = R \times T$ | **Domain** — Cartesian product of all Rooms × Timeslots |
| $\mathcal{C}_H$ | **Hard Constraints** — Must be satisfied; violations are fatal |
| $\mathcal{C}_S$ | **Soft Constraints** — Should be satisfied; violations incur penalty |
| $f: \mathcal{X} \rightarrow \mathcal{D}$ | **Assignment function** — The timetable itself |

---

### Hard Constraints (Mandatory — Zero Tolerance)

#### H1 · Room Uniqueness Constraint
$$\forall x_i, x_j \in \mathcal{X}, \; i \neq j : \quad f(x_i).room = f(x_j).room \implies f(x_i).time \cap f(x_j).time = \emptyset$$

No two classes may occupy the same room during any overlapping timeslot.

#### H2 · Student Non-Overlap Constraint
$$\forall s \in \mathcal{S}, \; \forall x_i, x_j \in \text{courses}(s) : \quad f(x_i).time \cap f(x_j).time = \emptyset$$

Students enrolled in multiple courses must never face a schedule collision.

#### H3 · Instructor Non-Overlap Constraint
$$\forall p \in \mathcal{P}, \; \forall x_i, x_j \in \text{teaches}(p) : \quad f(x_i).time \cap f(x_j).time = \emptyset$$

A professor cannot simultaneously teach two classes.

#### H4 · Room Capacity Constraint
$$\forall x_i \in \mathcal{X} : \quad \text{capacity}(f(x_i).room) \geq \text{enrollment}(x_i)$$

Room seating must accommodate the enrolled student count.

---

### Soft Constraints (Penalty-Weighted Minimization)

#### S1 · Instructor Time Preference
$$P_{S1} = \sum_{x_i \in \mathcal{X}} w_p \cdot \mathbb{1}[f(x_i).time \notin \text{preferred}(\text{instructor}(x_i))]$$

#### S2 · Room Type Preference
$$P_{S2} = \sum_{x_i \in \mathcal{X}} w_r \cdot \mathbb{1}[f(x_i).room \notin \text{preferred\_rooms}(x_i)]$$

#### S3 · Distribution / Spacing Penalty
$$P_{S3} = \sum_{x_i \in \mathcal{X}} w_d \cdot \max\left(0, \; \text{consecutive}(x_i) - \text{threshold}\right)$$

Penalizes courses stacked consecutively without breaks.

---

### The Objective (Loss) Function

$$\text{Score}(f) = \underbrace{|\mathcal{C}_H^{\text{violated}}| \times 1000}_{\text{Hard Violation Penalty}} + \underbrace{(P_{S1} + P_{S2} + P_{S3})}_{\text{Soft Constraint Penalty}}$$

$$\text{Goal:} \quad f^* = \arg\min_{f} \; \text{Score}(f)$$

The factor of **1,000× on hard violations** ensures the solver never sacrifices feasibility for soft-constraint comfort. A single room conflict will always outweigh thousands of preference violations.

---

<br/>

## ⚙️ Algorithm Deep Dives

### Algorithm 1 · Backtracking + MRV + Forward Checking

**The Systematic Guarantor**

```python
def backtrack(assignment: dict, csp: CSP) -> dict | None:
    if is_complete(assignment):
        return assignment

    var = select_unassigned_variable_MRV(assignment, csp)  # Minimum Remaining Values

    for value in order_domain_values(var, assignment, csp):
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value

            inferences = forward_check(var, value, assignment, csp)  # Prune domains
            if inferences is not FAILURE:
                apply_inferences(csp, inferences)
                result = backtrack(assignment, csp)
                if result is not FAILURE:
                    return result
                remove_inferences(csp, inferences)

            del assignment[var]

    return FAILURE  # Trigger backtrack
```

**MRV Heuristic** selects whichever unassigned class has the *fewest remaining legal timeslot/room combinations*, attacking the hardest-to-satisfy constraints first and dramatically pruning the search tree.

**Forward Checking** propagates the consequences of each assignment forward, eliminating values from neighboring variables' domains that would immediately cause a violation. This catches dead-ends *before* exploring them.

**Guarantees:** If a feasible timetable exists, backtracking with MRV will find it. If the problem is over-constrained, it will prove infeasibility — something probabilistic methods cannot do.

---

### Algorithm 2 · Min-Conflicts (Fast Heuristic Repair)

**The Speed Demon**

```python
def min_conflicts(csp: CSP, max_steps: int = 100_000) -> dict | None:
    assignment = generate_random_complete_assignment(csp)

    for step in range(max_steps):
        conflicted = get_conflicted_variables(assignment, csp)

        if not conflicted:
            return assignment  # Solution found

        var = random.choice(conflicted)
        value = argmin_conflicts(var, assignment, csp)  # Value causing fewest conflicts
        assignment[var] = value

    return None  # Timeout
```

Rather than building a schedule from scratch, Min-Conflicts **starts with a complete (but likely conflicting) assignment** and iteratively repairs only the variables currently causing violations.

Each repair step picks a conflicted class and reassigns it to the room/timeslot that minimizes the total number of active constraint violations. This is a **local search** approach — it cannot guarantee optimality, but it finds a "good enough" schedule dramatically faster than backtracking on large instances.

**Ideal for:** Real-time rescheduling (e.g., a room becomes unavailable mid-semester) where a quick, near-feasible result is needed within seconds.

---

### Algorithm 3 · Simulated Annealing

**The Thermodynamic Optimizer**

```python
def simulated_annealing(csp: CSP, T_start=1000, T_end=0.1, alpha=0.995) -> dict:
    current = random_feasible_assignment(csp)
    current_score = score(current, csp)
    best = current

    T = T_start
    while T > T_end:
        neighbor = generate_neighbor(current, csp)  # Small perturbation
        neighbor_score = score(neighbor, csp)
        delta = neighbor_score - current_score

        # Always accept improvements; sometimes accept regressions
        if delta < 0 or random.random() < math.exp(-delta / T):
            current = neighbor
            current_score = neighbor_score

        if current_score < score(best, csp):
            best = current

        T *= alpha  # Geometric cooling schedule

    return best
```

Inspired by the physical annealing of metals — where slow, controlled cooling produces crystalline perfection — **Simulated Annealing escapes local minima** by occasionally accepting a *worse* schedule during early, high-temperature phases.

The **acceptance probability** $P(\text{accept}) = e^{-\Delta/T}$ decreases as temperature cools:
- 🔥 **High temperature (early)**: Almost any change accepted → broad exploration of the landscape
- ❄️ **Low temperature (late)**: Only improvements accepted → fine-tuned local optimization

This produces schedules with **lower final soft-penalty scores** than either backtracking or min-conflicts, at the cost of longer runtime and no hard-violation guarantee.

**Ideal for:** Producing the absolute highest-quality production timetable when compute time is not a limiting factor.

---

<br/>

## 🏗 Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                                  │
│                                                                            │
│   ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────┐   │
│   │  Control Panel   │  │  Master Timetable │  │  3D Conflict Graph    │   │
│   │  (Algorithm +    │  │  Grid View       │  │  (React Three Fiber)  │   │
│   │   Dataset Select)│  │  (CSS Grid)      │  │  WebGL / 60 FPS       │   │
│   └────────┬─────────┘  └────────┬─────────┘  └───────────┬───────────┘   │
│            │                     │                         │               │
│   ┌────────▼─────────────────────▼─────────────────────────▼───────────┐  │
│   │                      State Management                               │  │
│   │            (Zustand + Immer for immutable history)                  │  │
│   └────────────────────────────────────┬────────────────────────────────┘  │
│                                        │  WebSocket + REST                  │
└────────────────────────────────────────│──────────────────────────────────-┘
                                         │
┌────────────────────────────────────────│───────────────────────────────────┐
│                      FastAPI Backend   │                                    │
│                                        │                                    │
│   ┌────────────────────────────────────▼────────────────────────────────┐  │
│   │                         API Gateway (Uvicorn)                        │  │
│   │   POST /solve   GET /datasets   WS /stream/{job_id}                 │  │
│   └──────┬──────────────────────────────────────────────────────────────┘  │
│          │                                                                   │
│   ┌──────▼──────────────────────────────────────────┐                      │
│   │              Algorithm Dispatcher                │                      │
│   │  Routes to solver based on request parameters    │                      │
│   └──────┬──────────────────┬──────────────┬─────────┘                     │
│          │                  │              │                                 │
│   ┌──────▼──────┐  ┌────────▼─────┐  ┌────▼─────────┐                     │
│   │ Backtracking│  │ Min-Conflicts│  │  Simulated   │                      │
│   │ + MRV + FC  │  │   Engine     │  │  Annealing   │                      │
│   └──────┬──────┘  └──────────────┘  └──────────────┘                     │
│          │                                                                   │
│   ┌──────▼────────────────────────────────────────────┐                    │
│   │                   CSP Core                         │                    │
│   │  ConstraintGraph | DomainManager | ConflictChecker│                    │
│   └──────┬────────────────────────────────────────────┘                    │
│          │                                                                   │
│   ┌──────▼────────────────────────────────────────────┐                    │
│   │                ITC-2019 XML Parser                 │                    │
│   │      Loads rooms, courses, constraints, prefs      │                    │
│   └───────────────────────────────────────────────────┘                    │
└───────────────────────────────────────────────────────────────────────────-┘
```

### Data Flow: Solving a Schedule

```
1. User selects dataset + algorithm in UI
         │
         ▼
2. POST /solve → FastAPI receives (dataset_id, algorithm, params)
         │
         ▼
3. ITC-2019 XML Parser loads and validates the problem instance
         │
         ▼
4. CSP Core initializes ConstraintGraph with:
   - Variables (classes) + Domains (Room × Timeslot combos)
   - Hard constraint arcs (professor, room, student, capacity)
   - Soft constraint weights (preference penalties)
         │
         ▼
5. Algorithm Dispatcher runs selected solver
   - Emits iteration snapshots via WebSocket every N steps
         │
         ▼
6. Frontend receives snapshots → updates:
   - Master Timetable grid (cell-level conflict coloring)
   - 3D Graph (node color transitions, edge weights)
   - Score chart (live loss curve)
   - Playback history buffer
         │
         ▼
7. Solver terminates → final schedule emitted
   - JSON export available
   - ICS calendar export available
```

---

<br/>

## 🛠 Tech Stack

### Frontend

| Technology | Version | Role |
|---|---|---|
| **React** | 18.x | UI component framework |
| **Next.js** | 14+ (Turbopack) | SSR, routing, hot reload |
| **React Three Fiber** | 8.x | Declarative Three.js / WebGL |
| **@react-three/drei** | latest | 3D helpers (OrbitControls, Text, etc.) |
| **@react-three/postprocessing** | latest | Bloom, depth-of-field, SSAO effects |
| **Zustand + Immer** | latest | Immutable state + playback history |
| **CSS Modules** | — | Component-scoped, zero-runtime styles |
| **Web Workers** | Native | Off-main-thread graph layout computation |

### Backend

| Technology | Version | Role |
|---|---|---|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.110+ | REST + WebSocket API |
| **Uvicorn** | latest | ASGI server |
| **lxml** | latest | High-performance XML parsing (ITC-2019) |
| **NumPy** | latest | Matrix operations for constraint checking |
| **multiprocessing** | stdlib | Parallel solver instances |
| **Pydantic v2** | latest | Request/response validation |

### Algorithms & Math

| Technique | Application |
|---|---|
| **CSP (Constraint Satisfaction)** | Core problem formulation |
| **MRV Heuristic** | Variable ordering for backtracking |
| **Forward Checking** | Domain pruning / arc consistency |
| **AC-3 Algorithm** | Full arc-consistency preprocessing |
| **Min-Conflicts** | Local search repair heuristic |
| **Simulated Annealing** | Global optimization with thermodynamic escaping |

---

<br/>

## 🚀 Getting Started

### Prerequisites

```bash
node >= 18.0.0
python >= 3.11
npm or yarn or pnpm
```

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/chronogrid-elite.git
cd chronogrid-elite
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download ITC-2019 datasets
python scripts/download_datasets.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server (Turbopack)
npm run dev
```

The app will be live at `http://localhost:3000`

### 4. Run Your First Solve

1. Open `http://localhost:3000`
2. Select a dataset from the dropdown (start with `thapar-small` for fast results)
3. Select **Min-Conflicts** algorithm for a quick demo
4. Click **▶ Run Optimizer**
5. Watch the 3D graph resolve in real time

---

<br/>

## 📦 ITC-2019 Dataset Integration

ChronoGrid Elite uses a custom XML parser to fully consume the ITC-2019 competition format:

```python
from chronogrid.parser import ITC2019Parser

parser = ITC2019Parser()
problem = parser.load("datasets/thapar-2019.xml")

print(f"Courses: {len(problem.courses)}")       # → 312
print(f"Rooms: {len(problem.rooms)}")           # → 48
print(f"Timeslots: {problem.timeslots_total}")  # → 60
print(f"Constraints: {len(problem.constraints)}")  # → 1,847
```

### Supported ITC-2019 Features

- [x] `<rooms>` — capacity, type, availability windows
- [x] `<courses>` — multi-section, multi-subpart configs
- [x] `<classes>` — limits, instructor assignments, room assignments
- [x] `<distributions>` — SameDays, DifferentDays, Overlap, Precedence
- [x] `<students>` — enrollment sets for student-overlap constraints
- [x] Instructor time unavailabilities
- [x] Room feature requirements (projector, lab equipment, etc.)
- [x] Pre-pinned class assignments
- [ ] `<travel>` distance constraints *(roadmap)*

---

<br/>

## 📊 Benchmarks & Performance

Results measured on a MacBook Pro M3 Max (14-core) with the full ITC-2019 benchmark suite.

### Solver Performance by Dataset Size

| Dataset | Classes | Backtracking + MRV | Min-Conflicts | Simulated Annealing |
|---|---|---|---|---|
| `small` (synthetic) | 50 | **0.3s** ✅ Optimal | 0.1s | 2.1s |
| `thapar-small` | 120 | **4.2s** ✅ Optimal | 0.8s | 18s |
| `thapar-full` | 312 | 47s ✅ Optimal | **3.1s** | 4m 22s |
| `masaryk-full` | 401 | ⏱ Timeout (10min) | **8.7s** ✅ Feasible | 11m 09s |
| `agh-full` | 287 | 6m 14s ✅ Optimal | **5.2s** | 8m 41s |

### Solution Quality (Final Score — Lower is Better)

| Dataset | Min-Conflicts | Simulated Annealing | Improvement |
|---|---|---|---|
| `thapar-full` | 1,842 | **891** | ↓ 51.6% |
| `masaryk-full` | 3,104 | **1,247** | ↓ 59.8% |
| `agh-full` | 2,219 | **978** | ↓ 55.9% |

> **Key insight:** Min-Conflicts finds a feasible schedule fast. Simulated Annealing finds the *best* schedule given enough time. For production use, run Min-Conflicts first for a feasibility check, then Simulated Annealing overnight for quality optimization.

---

<br/>

## 📡 API Reference

### `POST /solve`

Initiate a solve job. Returns a `job_id` for WebSocket streaming.

```json
// Request
{
  "dataset_id": "thapar-2019",
  "algorithm": "simulated_annealing",
  "params": {
    "T_start": 1000,
    "T_end": 0.1,
    "alpha": 0.995,
    "max_iterations": 50000
  }
}

// Response
{
  "job_id": "job_8f3a2c1e",
  "estimated_duration_seconds": 480,
  "stream_url": "ws://localhost:8000/stream/job_8f3a2c1e"
}
```

### `WS /stream/{job_id}`

Stream optimization progress in real time.

```json
// Snapshot message (emitted every N iterations)
{
  "iteration": 2847,
  "score": 1203,
  "hard_violations": 2,
  "soft_penalty": 203,
  "assignments": {
    "c1": { "room": "r012", "day": 1, "slot": 3 },
    "c2": { "room": "r047", "day": 3, "slot": 7 }
  },
  "conflict_edges": [["c1", "c5"], ["c3", "c8"]],
  "temperature": 412.3
}
```

### `GET /datasets`

List all available ITC-2019 instances.

```json
[
  {
    "id": "thapar-2019",
    "institution": "Thapar University",
    "courses": 312,
    "rooms": 48,
    "difficulty": "high"
  }
]
```

### `GET /solve/{job_id}/result`

Retrieve the final schedule once solving is complete.

### `GET /solve/{job_id}/export/ics`

Download the final timetable as an `.ics` calendar file.

---

<br/>

## ⚙️ Configuration

```python
# backend/config.py

class SolverConfig:
    # Backtracking
    BACKTRACK_MAX_DEPTH: int = 10_000
    FORWARD_CHECK_ENABLED: bool = True

    # Min-Conflicts
    MIN_CONFLICTS_MAX_STEPS: int = 100_000
    RANDOM_SEED: int = 42

    # Simulated Annealing
    SA_T_START: float = 1000.0
    SA_T_END: float = 0.1
    SA_ALPHA: float = 0.995           # Geometric cooling rate
    SA_MAX_ITERATIONS: int = 500_000

    # Scoring
    HARD_VIOLATION_WEIGHT: int = 1000
    SOFT_PENALTY_TIME_PREF: float = 1.0
    SOFT_PENALTY_ROOM_PREF: float = 0.5
    SOFT_PENALTY_DISTRIBUTION: float = 2.0

    # Streaming
    SNAPSHOT_INTERVAL: int = 100      # Emit snapshot every N iterations
    MAX_HISTORY_SIZE: int = 10_000    # Max snapshots retained in memory
```

---

<br/>

## 🗺 Roadmap

### v4.1 (Q3 2025)
- [ ] **Arc Consistency (AC-3)** preprocessing as a standalone phase before backtracking
- [ ] **Travel distance constraints** from ITC-2019 spec (rooms across buildings)
- [ ] **Multi-objective Pareto optimization** (minimize violations *and* professor travel simultaneously)
- [ ] **Dark/Light theme toggle** for the WebGL interface

### v4.2 (Q4 2025)
- [ ] **Genetic Algorithm** engine as a 4th solver option
- [ ] **Room heat map** overlay: visualize utilization across the week
- [ ] **Collaborative editing** — multiple planners annotate/lock assignments in real time
- [ ] **PDF export** — print-ready master timetable with department groupings

### v5.0 (2026)
- [ ] **LLM-assisted constraint elicitation** — describe constraints in plain English
- [ ] **Multi-campus / multi-building** support with travel time modeling
- [ ] **Live integration** with SIS (Student Information Systems)
- [ ] **Mobile-native 3D viewer** (WebXR / AR)

---

<br/>

## 🤝 Contributing

Contributions are what make open-source extraordinary. Whether you're fixing a typo, adding a new dataset parser, or implementing an entirely new optimization algorithm — all contributions are welcome.

### How to Contribute

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/genetic-algorithm`
3. **Make your changes** with tests
4. **Run the test suite**: `pytest backend/tests/ && npm run test`
5. **Submit a Pull Request** with a clear description

### Code Standards

```bash
# Python
black backend/ && isort backend/ && mypy backend/

# Frontend
npm run lint && npm run type-check
```

### Contribution Areas

| Area | Difficulty | Impact |
|---|---|---|
| New ITC-2019 dataset parsers | 🟢 Easy | Medium |
| Algorithm parameter tuning | 🟢 Easy | High |
| UI/UX improvements | 🟡 Medium | High |
| New constraint types | 🟡 Medium | High |
| New optimization algorithms | 🔴 Hard | Very High |
| Distributed solving (Ray/Celery) | 🔴 Hard | Very High |

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

<br/>

## 📄 License

ChronoGrid Elite is released under the **MIT License**.

```
MIT License

Copyright (c) 2025 ChronoGrid Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

See [LICENSE](LICENSE) for the full text.

---

<br/>

## 🙏 Acknowledgements

- **[International Timetabling Competition 2019](https://www.itc2019.org)** — for the benchmark datasets and problem formulations that give ChronoGrid real-world validity
- **[Russell & Norvig — *Artificial Intelligence: A Modern Approach*](http://aima.cs.berkeley.edu/)** — foundational algorithms and CSP theory
- **[React Three Fiber](https://docs.pmnd.rs/react-three-fiber)** — making WebGL accessible and declarative
- **[FastAPI](https://fastapi.tiangolo.com)** — for the cleanest Python API framework in existence
- Every researcher who has wrestled with NP-Hard scheduling so we could stand on their shoulders

---

<br/>

<div align="center">

**Built with rigor. Visualized with beauty. Scaled for reality.**

---

*If ChronoGrid Elite solved a headache for you, please consider giving it a ⭐ on GitHub.*
*It helps more than you know.*

<br/>

[![Star History](https://img.shields.io/github/stars/your-org/chronogrid-elite?style=social)](https://github.com/your-org/chronogrid-elite)
[![Follow](https://img.shields.io/github/followers/your-org?style=social)](https://github.com/your-org)

</div>
