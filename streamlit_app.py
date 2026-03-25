import streamlit as st
import os
import sys
import time
import pandas as pd
import altair as alt

# Add backend directory to path so we can cleanly import the existing CSP engine
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

try:
    from backend import parser
    from backend.solvers import backtracking, min_conflicts, simulated_annealing
    from backend.models import Problem, Assignment
    from backend.scoring import evaluate
except ImportError:
    # If starting directly inside the backend directory
    import parser
    from solvers import backtracking, min_conflicts, simulated_annealing
    from models import Problem, Assignment
    from scoring import evaluate

# --- Setup & Config ---
st.set_page_config(
    page_title="ChronoGrid Timetable AI",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📅 ChronoGrid: Smart University Timetable Generator")
st.markdown("""
Welcome to the Streamlit deployment of **ChronoGrid Elite**!  
This tool solves the NP-Hard university timetabling problem using complex constraint satisfaction algorithms against authentic ITC-2019 dataset instances from universities around the world.
""")

# --- Sidebar Data Controls ---
st.sidebar.header("Control Panel")

@st.cache_data
def get_datasets():
    datasets_dir = os.path.join(os.path.dirname(__file__), "backend", "datasets")
    if not os.path.exists(datasets_dir):
        datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
    if not os.path.exists(datasets_dir):
        return ["demo"] # fallback
    files = [f.replace(".xml", "") for f in os.listdir(datasets_dir) if f.endswith(".xml")]
    return sorted(files)

dataset_name = st.sidebar.selectbox("1. Select Dataset Instances", get_datasets())

algo_map = {
    "Backtracking + MRV": "backtracking",
    "Min-Conflicts": "min_conflicts",
    "Simulated Annealing": "simulated_annealing"
}
algo_choice = st.sidebar.selectbox("2. Select AI Solver", list(algo_map.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("Solver Parameters")
max_iters = st.sidebar.slider("Max Iterations", 100, 10000, 3000, step=100)
timeout = st.sidebar.slider("Timeout (seconds)", 1, 30, 5)

# --- Backend Processing ---
@st.cache_resource
def load_problem(name):
    # Depending on where Streamlit is run from
    datasets_dir = os.path.join(os.path.dirname(__file__), "backend", "datasets")
    if not os.path.exists(datasets_dir):
        datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
        
    path = os.path.join(datasets_dir, f"{name}.xml")
    if not os.path.exists(path):
        from backend.parser import generate_demo_problem
        return generate_demo_problem()
    
    with open(path, "r", encoding="utf-8") as f:
        return parser.parse_itc2019_xml(f.read())

problem = load_problem(dataset_name)

# Problem Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Classes to Schedule", len(problem.classes))
col2.metric("Available Rooms", len(problem.rooms))
col3.metric("Registered Students", len(problem.students))
col4.metric("Constraints", len(problem.constraints))

st.markdown("---")

if st.sidebar.button("🚀 Run Solver", type="primary"):
    st.info(f"Running **{algo_choice}** on dataset **{dataset_name}**...")
    
    start_time = time.time()
    result = None
    
    with st.spinner("Crunching Constraints..."):
        if algo_map[algo_choice] == "backtracking":
            result = backtracking.solve(problem, timeout_ms=timeout * 1000)
        elif algo_map[algo_choice] == "min_conflicts":
            result = min_conflicts.solve(problem, max_iterations=max_iters, timeout_ms=timeout * 1000)
        elif algo_map[algo_choice] == "simulated_annealing":
            result = simulated_annealing.solve(problem, max_iterations=max_iters, timeout_ms=timeout * 1000)
            
    elapsed = time.time() - start_time
    
    if not result.assignments:
        st.error("❌ The solver could not find any valid assignment within the timeout period.")
    else:
        st.success(f"✅ Solver Finished in {elapsed:.2f} seconds!")
        
        # Results Dashboard
        r1, r2, r3 = st.columns(3)
        r1.metric("Hard Violations", result.hard_violations, delta="Conflicts causing invalid schedule", delta_color="inverse" if result.hard_violations > 0 else "normal")
        r2.metric("Soft Score Penalty", result.soft_penalty, delta="Lower is better", delta_color="inverse")
        r3.metric("Scheduled Classes", f"{len(result.assignments)} / {len(problem.classes)}")

        # Optimization Curve Chart
        if result.optimization_curve:
            st.subheader("📈 Optimization Progress over Time")
            df = pd.DataFrame([{"Iteration": p.iteration, "Hard Conflicts": p.hard_violations, "Soft Penalty": p.soft_penalty} for p in result.optimization_curve])
            
            base = alt.Chart(df).encode(x="Iteration")
            line1 = base.mark_line(color="#F0455A").encode(y="Hard Conflicts")
            line2 = base.mark_line(color="#4F6EF7").encode(y="Soft Penalty")
            
            st.altair_chart(alt.layer(line1, line2).resolve_scale(y='independent'), use_container_width=True)

        # Timetable DataFrame
        st.subheader("📋 Master Master Schedule")
        
        # Process assignments into human-readable DataFrame
        schedule = []
        for a in result.assignments:
            cls = problem.classes.get(a.class_id)
            course_name = cls.course_id if cls else a.class_id
            
            # Extract time string 
            time_str = a.timeslot_id
            if cls and cls.possible_times:
                for t in cls.possible_times:
                    if t.id == a.timeslot_id:
                        time_str = f"Days: {t.days}, Start: {t.start}, Len: {t.length}"
                        break
            
            schedule.append({
                "Course": course_name,
                "Class Instance": a.class_id,
                "Assigned Room": a.room_id,
                "Timeslot": time_str
            })
            
        st.dataframe(pd.DataFrame(schedule), use_container_width=True)
else:
    st.info("👈 Click **Run Solver** in the sidebar to generate a timetable.")
