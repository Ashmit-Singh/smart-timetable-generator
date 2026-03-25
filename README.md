# ChronoGrid Elite v4.0 — Smart University Timetable Generator

ChronoGrid Elite is a production-grade Constraint Satisfaction Problem (CSP) solver and 3D visualization platform designed specifically for the NP-Hard challenge of University Timetabling. 

It generates optimal master schedules and resolves spatial/temporal scheduling conflicts using real-world data structures derived from the **ITC-2019 (International Timetabling Competition)** format.

## 🚀 Key Features

### 1. **Authentic Datasets (ITC-2019)**
Unlike simple synthetic datasets, the system natively parses and solves genuine XML problem instances from 10 real universities worldwide (e.g., Thapar University, AGH University of Science & Technology, Masaryk University). It handles complex constraints like multi-day classes (e.g., MWF classes) and specialized room capacities.

### 2. **Three AI Optimization Engines**
We approach the NP-Hard Timetabling problem using 3 distinct algorithms, each with their own mathematical trade-offs:
- **Backtracking + MRV (Minimum Remaining Values) + Forward Checking**: Explores the entire decision tree systematically. Guarantees 0 hard violations by aggressively pruning impossible branches, but fails fast if a perfect schedule is mathematically impossible on highly constrained datasets.
- **Min-Conflicts (Fast Heuristic Repair)**: A local search algorithm that starts with a random schedule and iteratively repairs only the conflicting variables. Extremely fast at finding a "good enough" schedule on massive datasets.
- **Simulated Annealing**: A probabilistic optimization engine inspired by thermodynamics. It escapes "local minima" by occasionally accepting worse schedules early in the search, progressively "cooling down" to find the absolute maximum overall schedule quality (minimal soft penalty).

### 3. **3D Conflict Graph Serialization**
- Real-time serialization of the CSP graph.
- **Nodes** = Classes/Courses.
- **Edges** = Shared Constraints (e.g., two classes share the same professor, or a student is enrolled in both, meaning they cannot overlap in time).
- Visualized in a beautiful, interactive 3D space using **React Three Fiber / WebGL**. 

### 4. **Progressive Output & Playback**
- An **Optimization Playback Engine** stores the history states of the solver at various iterations.
- Users can scrub the timeline to watch the AI progressively resolve conflicts in the Master Timetable and 3D Graph simultaneously.

### 5. **Hybrid Architecture**
- **FastAPI Python Backend**: Runs the intensive backtracking and constraint evaluations efficiently using local multi-processing optimizations and Python's deep math libraries.
- **React/Next.js Frontend**: A high-performance WebGL glassmorphic UI utilizing Web Workers and `useFrame` request loops to maintain 60 FPS while visualizing thousands of nodes.

---

## 🧠 Constraint Model

The application models University Timetabling as a **Constraint Satisfaction Problem (CSP) with Optimization**:

**Variables:** Course Meetings / Classes
**Domains:** Combinations of (Room) x (Timeslot)

### Hard Constraints (Must not be violated)
1. **Room Conflict**: No two classes can occupy the same room at the same time.
2. **Student Overlap**: Students enrolled in multiple courses cannot have overlapping class times.
3. **Professor Conflict**: A professor cannot teach two different classes at the same time.
4. **Capacity Limits**: A room's seating capacity must be strictly $\ge$ the class enrollment size.

### Soft Constraints (+ Penalty points = Minimization Goal)
1. **Time Preferences**: Professors prefer teaching at specific slots.
2. **Room Preferences**: Classes might prefer specific buildings or lab types.
3. **Distribution Overlaps**: Ideal spacing across days (not putting 4 lectures consecutively).

The **Loss Function** scoring is defined as:
`Score = (Hard Violations × 1000) + Soft Penalty`
_(The goal of the solver is to minimize the score, ideally bringing Hard Violations to 0)._

---

## 🛠 Tech Stack 
- **Frontend**: React 18, Next.js (Turbopack), React Three Fiber (Three.js), CSS Modules
- **Backend**: Python 3, FastAPI, Uvicorn 
- **Algorithms**: CSP Heuristics, Simulated Annealing, Min-Conflicts, Arc Consistency
