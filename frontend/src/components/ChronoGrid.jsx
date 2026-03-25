"use client";
// ChronoGrid Elite v4.0 — Main App Component
import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { T, DATASET, COURSE_PALETTE } from "./constants";
import { GraphScene } from "./GraphComponents";
import { Btn, TimetableGrid, usePlayback, PlaybackPanel, EnergyCurve, WebGLBg } from "./UIComponents";
import { createSolverWorker, buildConflictGraphLocal } from "./solverWorker";

const API_BASE = "http://localhost:8000";

export default function ChronoGridApp() {
  const [tab, setTab] = useState("graph");
  const [algo, setAlgo] = useState("minconflicts");
  const [solveResult, setSolveResult] = useState(null);
  const [allResults, setAllResults] = useState({});
  const [solving, setSolving] = useState(false);
  const [solveProgress, setSolveProgress] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState("demo");
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [loadingDataset, setLoadingDataset] = useState(false);
  const workerRef = useRef(null);

  const playback = usePlayback(solveResult?.history || []);
  const currentFrame = playback.currentFrame;
  const displayAssignment = currentFrame?.assignment || solveResult?.assignment || null;
  const displayConflictPairs = currentFrame?.conflictPairs || [];

  const targetNodePosition = useMemo(() => {
    if (!selectedNode || !graphData) return null;
    const node = graphData.nodes.find(n => n.id === selectedNode);
    return node ? node.position : null;
  }, [selectedNode, graphData]);

  // Fetch available datasets from backend
  useEffect(() => {
    setTimeout(() => setMounted(true), 80);
    setGraphData(buildConflictGraphLocal(DATASET));
    fetch(`${API_BASE}/datasets`).then(r => r.json()).then(data => {
      setDatasets(data.datasets || []);
      setActiveDataset(data.active || "demo");
    }).catch(() => {});
    // Also fetch current problem info
    fetch(`${API_BASE}/problem-info`).then(r => r.json()).then(info => {
      setDatasetInfo(info);
    }).catch(() => {});
  }, []);

  // Normalize backend graph data (flat node strings) → frontend shape (objects with position/color/label)
  const normalizeGraphData = useCallback((raw) => {
    if (!raw) return null;
    // If nodes are already objects with position, return as-is
    if (raw.nodes?.length > 0 && typeof raw.nodes[0] === "object" && raw.nodes[0].position) {
      return raw;
    }
    // Backend returns nodes as flat strings ["cl0","cl1",...] — convert to objects
    const nodeList = (raw.nodes || []).map((n, i) => {
      const id = typeof n === "string" ? n : n.id || `node_${i}`;
      // Distribute nodes in a circle layout
      const angle = (2 * Math.PI * i) / (raw.nodes.length || 1);
      const radius = 3 + Math.random() * 1.5;
      return {
        id,
        label: id,
        position: [Math.cos(angle) * radius, (Math.random() - 0.5) * 2, Math.sin(angle) * radius],
        color: COURSE_PALETTE[i % COURSE_PALETTE.length],
      };
    });
    const edgeList = (raw.edges || []).map(e => ({
      ...e,
      color: e.color || "#ffffff33",
    }));
    return { nodes: nodeList, edges: edgeList };
  }, []);

  // Handles switching datasets
  const handleDatasetChange = useCallback(async (name) => {
    if (name === activeDataset) return;
    setLoadingDataset(true);
    setSolveResult(null); setAllResults({});
    try {
      const res = await fetch(`${API_BASE}/load-dataset/${name}`, { method: "POST" });
      const info = await res.json();
      setDatasetInfo(info);
      setActiveDataset(name);
      // Rebuild local graph from the embedded DATASET for demo, or fetch from backend
      if (name === "demo") {
        setGraphData(buildConflictGraphLocal(DATASET));
      } else {
        // Fetch conflict graph from backend
        const pgRes = await fetch(`${API_BASE}/problem-info`);
        const pgInfo = await pgRes.json();
        setDatasetInfo(pgInfo);
        if (pgInfo.conflict_graph) {
          setGraphData(normalizeGraphData(pgInfo.conflict_graph));
        } else {
          setGraphData(buildConflictGraphLocal(DATASET));
        }
      }
    } catch (e) { console.error("Failed to load dataset:", e); }
    setLoadingDataset(false);
  }, [activeDataset, normalizeGraphData]);

  const solveWithBackend = async (a) => {
    const payload = {
      algorithm: a === "minconflicts" ? "min_conflicts" : a === "annealing" ? "simulated_annealing" : "backtracking",
      max_iterations: a === "annealing" ? 5000 : 800,
      timeout_ms: 10000
    };
    const res = await fetch(`${API_BASE}/generate-timetable`, {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to solve");
    
    const assignment = {};
    const conflictPairs = [];
    if (data.violation_details && data.violation_details.hard) {
      data.violation_details.hard.forEach(v => {
        if (v.involved_classes && v.involved_classes.length >= 2) {
          conflictPairs.push([v.involved_classes[0], v.involved_classes[1]]);
        }
      });
    }

    data.assignments.forEach((ba, i) => {
      // Create a stable deterministic color index based on class string length to keep colors consistent
      const colorIdx = ba.class_id ? ba.class_id.charCodeAt(ba.class_id.length - 1) : i;
      assignment[ba.class_id] = {
        days: ba.day_indices, 
        day: ba.day_indices.length > 0 ? ba.day_indices[0] : 0,
        slot: ba.slot_index,
        roomId: ba.room_id,
        course: { id: ba.class_id, name: ba.course_name || ba.class_id },
        room: { id: ba.room_id, name: ba.room_name || ba.room_id },
        prof: { name: "Faculty" },
        color: COURSE_PALETTE[colorIdx % COURSE_PALETTE.length]
      };
    });

    const history = data.optimization_curve?.length > 0 
      ? data.optimization_curve.map(pt => ({ iteration: pt.iteration, conflicts: pt.hard_violations, soft: pt.soft_penalty, assignment, conflictPairs })) 
      : [{ iteration: 1, conflicts: data.hard_violations, soft: data.soft_penalty, assignment, conflictPairs }];

    return {
      algo: a, assignment, time: data.elapsed_ms, conflicts: data.hard_violations, soft: data.soft_penalty, history, conflictPairs
    };
  };

  const handleSolve = useCallback(async (targetAlgo) => {
    const a = targetAlgo || algo;
    if (workerRef.current) { workerRef.current.terminate(); workerRef.current = null; }
    setSolving(true); setSolveProgress(null);

    if (activeDataset === "demo") {
      const worker = createSolverWorker();
      workerRef.current = worker;
      const accumulated = [];
      worker.onmessage = (e) => {
        const { type, frame, result, graphData: gd } = e.data;
        if (type === "frame") { accumulated.push(frame); if (accumulated.length % 10 === 0) setSolveProgress({ ...frame }); }
        else if (type === "done") {
          const fullResult = { ...result, history: accumulated };
          setSolveResult(fullResult);
          setAllResults(prev => ({ ...prev, [a]: fullResult }));
          if (gd) setGraphData(normalizeGraphData(gd));
          setSolving(false); setSolveProgress(null);
          worker.terminate(); workerRef.current = null;
        }
      };
      worker.onerror = () => setSolving(false);
      worker.postMessage({ algo: a, dataset: DATASET });
    } else {
      try {
        const fullResult = await solveWithBackend(a);
        setSolveResult(fullResult);
        setAllResults(prev => ({ ...prev, [a]: fullResult }));
      } catch (err) {
        console.error("Backend solve failed:", err);
      } finally {
        setSolving(false); setSolveProgress(null);
      }
    }
  }, [algo, activeDataset, normalizeGraphData]);

  const handleBenchmarkAll = useCallback(async () => {
    setSolving(true);
    const algos = ["backtracking", "minconflicts", "annealing"];
    const results = {};
    
    if (activeDataset === "demo") {
      let idx = 0;
      const runNext = () => {
        if (idx >= algos.length) { setAllResults(results); setSolveResult(results[algo] || results["minconflicts"]); setSolving(false); return; }
        const a = algos[idx++];
        const worker = createSolverWorker();
        const acc = [];
        worker.onmessage = (e) => {
          if (e.data.type === "frame") acc.push(e.data.frame);
          else if (e.data.type === "done") { results[a] = { ...e.data.result, history: acc }; if (e.data.graphData) setGraphData(normalizeGraphData(e.data.graphData)); worker.terminate(); runNext(); }
        };
        worker.postMessage({ algo: a, dataset: DATASET });
      };
      runNext();
    } else {
      try {
        for (const a of algos) {
          setSolveProgress({ algosDone: Object.keys(results).length, target: 3 }); // minor signal to UI
          const r = await solveWithBackend(a);
          results[a] = r;
        }
        setAllResults(results); 
        setSolveResult(results[algo] || results["minconflicts"]);
      } catch (err) {
        console.error("Benchmark failed:", err);
      } finally {
        setSolving(false); setSolveProgress(null);
      }
    }
  }, [algo, activeDataset, normalizeGraphData]);

  const handleAI = async () => {
    if (!aiPrompt.trim()) return;
    setAiLoading(true); setAiResponse(""); setAiSuggestions([]);
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST", headers: { "Content-Type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514", max_tokens: 900, stream: true,
          system: `University timetabling expert. Dataset: ${JSON.stringify(DATASET)}. Current conflicts: ${solveResult?.conflicts ?? "none"}, soft: ${solveResult?.soft ?? "N/A"}%, algo: ${algo}.\nRespond ONLY as JSON: {"analysis":"2-3 sentences","suggestions":[{"title":"...","description":"...","impact":"high|medium|low"}],"recommendation":"one sentence"}`,
          messages: [{ role: "user", content: aiPrompt }],
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      if (!res.body) throw new Error("No stream body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let rawAccum = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split("\n")) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6).trim();
          if (data === "[DONE]") continue;
          try { const parsed = JSON.parse(data); const delta = parsed?.delta?.text || parsed?.content_block?.text || ""; if (delta) { rawAccum += delta; setAiResponse(rawAccum.replace(/[{}"]/g, "").trim().slice(0, 120) + "…"); } } catch {}
        }
      }
      try { const clean = rawAccum.replace(/```json|```/g, "").trim(); const p = JSON.parse(clean); setAiResponse(p.analysis || rawAccum); setAiSuggestions(p.suggestions || []); } catch { setAiResponse(rawAccum); }
    } catch (e) { setAiResponse("Error: " + e.message); }
    setAiLoading(false);
  };

  const tabs = [
    { id: "graph", icon: "◈", label: "3D Graph" },
    { id: "playback", icon: "▶", label: "Playback" },
    { id: "schedule", icon: "⊞", label: "Timetable" },
    { id: "analytics", icon: "▦", label: "Analytics" },
    { id: "ai", icon: "⬡", label: "AI Assist" },
  ];

  const algoConfig = {
    backtracking: { label: "BT+MRV", color: T.accent },
    minconflicts: { label: "Min-Conflicts", color: T.green },
    annealing: { label: "SA", color: T.amber },
  };

  const liveConflictPairs = solveProgress?.conflictPairs || displayConflictPairs;

  return (
    <div style={{ minHeight: "100vh", background: T.bg, color: T.text, fontFamily: "'DM Sans', 'Sora', system-ui, sans-serif", overflow: "hidden", position: "relative" }}>
      <WebGLBg />
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Sora:wght@600;700;800&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        ::-webkit-scrollbar{width:3px;height:3px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:#1F2937;border-radius:3px;}
        @keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
        @keyframes spin{to{transform:rotate(360deg);}}
        @keyframes glowPulse{0%,100%{box-shadow:0 0 10px rgba(79,110,247,0.3);}50%{box-shadow:0 0 22px rgba(79,110,247,0.6);}}
        @keyframes slideIn{from{opacity:0;transform:translateX(-8px);}to{opacity:1;transform:translateX(0);}}
        @keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
        .anim-up{animation:fadeUp 0.4s cubic-bezier(0.4,0,0.2,1) forwards;}
        .cursor-blink{animation:blink 1s step-end infinite;}
        select option{background:#0C0C15;}
        input[type=range]{accent-color:#4F6EF7;}
      `}</style>

      {/* SIDEBAR */}
      <div style={{ position:"fixed", left:0, top:0, bottom:0, width:60, background:"rgba(12,12,21,0.96)", borderRight:`1px solid ${T.border}`, display:"flex", flexDirection:"column", alignItems:"center", paddingTop:18, gap:4, zIndex:200, backdropFilter:"blur(24px)" }}>
        <div style={{ width:34, height:34, borderRadius:9, background:"linear-gradient(135deg, #4F6EF7, #9B6EF7)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:17, marginBottom:22, animation:"glowPulse 3s ease-in-out infinite" }}>◈</div>
        {tabs.map(t2 => (
          <button key={t2.id} onClick={() => setTab(t2.id)} title={t2.label}
            style={{ width:42, height:42, borderRadius:9, fontSize:16, background: tab===t2.id ? "rgba(79,110,247,0.18)" : "transparent", color: tab===t2.id ? T.accent : T.dim, border: tab===t2.id ? `1px solid rgba(79,110,247,0.35)` : "1px solid transparent", cursor:"pointer", transition:"all 0.2s" }}>
            {t2.icon}
          </button>
        ))}
      </div>

      <div style={{ marginLeft:60, display:"flex", flexDirection:"column", minHeight:"100vh", position:"relative", zIndex:1 }}>
        {/* HEADER */}
        <header style={{ height:54, display:"flex", alignItems:"center", justifyContent:"space-between", padding:"0 24px", borderBottom:`1px solid ${T.border}`, background:"rgba(4,4,10,0.85)", backdropFilter:"blur(20px)", position:"sticky", top:0, zIndex:100 }}>
          <div style={{ display:"flex", alignItems:"center", gap:14 }}>
            <div><span style={{ fontFamily:"'Sora',sans-serif", fontWeight:800, fontSize:14, letterSpacing:"0.07em" }}>CHRONO</span><span style={{ fontFamily:"'Sora',sans-serif", fontWeight:800, fontSize:14, letterSpacing:"0.07em", color:T.accent }}>GRID</span></div>
            <span style={{ fontSize:9, padding:"2px 7px", borderRadius:4, background:"rgba(79,110,247,0.1)", color:T.accent, fontFamily:"monospace", letterSpacing:"0.12em", border:`1px solid rgba(79,110,247,0.2)` }}>R3F · v4.0</span>
            {datasets.length > 0 && (
              <select value={activeDataset} onChange={e => handleDatasetChange(e.target.value)} disabled={loadingDataset || solving}
                style={{ background:T.surface2, border:`1px solid ${T.border}`, color:T.cyan, borderRadius:6, padding:"5px 10px", fontSize:10, fontFamily:"monospace", cursor:"pointer", maxWidth:200 }}>
                {datasets.map(d => <option key={d.name} value={d.name}>{d.full_name || d.name}</option>)}
              </select>
            )}
            <div style={{ display:"flex", gap:3, marginLeft:4 }}>
              {Object.entries(algoConfig).map(([key, cfg]) => (
                <button key={key} onClick={() => setAlgo(key)}
                  style={{ padding:"5px 12px", borderRadius:6, fontSize:11, cursor:"pointer", fontFamily:"monospace", fontWeight:600, border:`1px solid ${algo===key ? cfg.color + "55" : T.border}`, background: algo===key ? cfg.color+"18" : "transparent", color: algo===key ? cfg.color : T.muted, transition:"all 0.2s" }}>
                  {cfg.label}
                </button>
              ))}
            </div>
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            {solveResult && (
              <div style={{ display:"flex", gap:10, fontSize:10, fontFamily:"monospace", marginRight:6 }}>
                <span style={{ color: solveResult.conflicts === 0 ? T.green : T.red }}>{solveResult.conflicts === 0 ? "✓" : "✗"} {solveResult.conflicts} conflicts</span>
                <span style={{ color:T.cyan }}>{solveResult.soft}% soft</span>
                <span style={{ color:T.amber }}>{solveResult.time}ms</span>
              </div>
            )}
            {solving && solveProgress && (
              <span style={{ fontSize:10, fontFamily:"monospace", color:T.amber, padding:"3px 8px", background:"rgba(245,165,36,0.1)", borderRadius:5, border:"1px solid rgba(245,165,36,0.25)" }}>⚡ {solveProgress.conflicts} conflicts live</span>
            )}
            <Btn onClick={handleBenchmarkAll} style={{ background:"rgba(79,110,247,0.1)", border:`1px solid rgba(79,110,247,0.3)`, color:T.accent }}>
              {solving ? <span style={{ display:"inline-block", animation:"spin 0.7s linear infinite" }}>◌</span> : "⊞ Benchmark All"}
            </Btn>
            <button onClick={() => handleSolve()} disabled={solving}
              style={{ padding:"7px 16px", borderRadius:7, fontSize:11, fontWeight:700, fontFamily:"inherit", cursor: solving ? "not-allowed" : "pointer", border:"none", background: solving ? "#1a1a2e" : `linear-gradient(135deg, ${T.accent}, ${T.purple})`, color: solving ? T.muted : "#fff", boxShadow: solving ? "none" : `0 3px 14px rgba(79,110,247,0.3)`, transition:"all 0.2s" }}>
              {solving ? <span style={{ display:"inline-block", animation:"spin 0.7s linear infinite" }}>◌</span> : `▶ Run ${algoConfig[algo].label}`}
            </button>
          </div>
        </header>

        {/* MAIN CONTENT */}
        <main style={{ flex:1, padding:"24px", opacity: mounted ? 1 : 0, transition:"opacity 0.4s" }}>

          {/* 3D GRAPH TAB */}
          {tab === "graph" && (
            <div className="anim-up">
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:16 }}>
                <div>
                  <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:20, fontWeight:800, marginBottom:4 }}>3D Conflict Graph</h2>
                  <p style={{ fontSize:12, color:T.muted }}>{datasetInfo ? `${datasetInfo.name} · ${datasetInfo.num_classes} classes · ${datasetInfo.num_rooms} rooms · ${datasetInfo.num_students} students` : "Nodes = courses · Edges = shared professor constraint · Click node → fly-to"}</p>
                </div>
                <div style={{ display:"flex", gap:10, fontSize:11, fontFamily:"monospace" }}>
                  {graphData && <><span style={{ color:T.muted }}>Nodes: <span style={{ color:T.text }}>{graphData.nodes.length}</span></span><span style={{ color:T.muted }}>Edges: <span style={{ color:T.red }}>{graphData.edges.length}</span></span></>}
                </div>
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 280px", gap:16 }}>
                <div style={{ height:520, background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, overflow:"hidden", position:"relative" }}>
                  {graphData && (
                    <Canvas camera={{ position:[0,2,9], fov:55 }} gl={{ antialias:true, alpha:true }} style={{ background:"transparent" }}>
                      <GraphScene graphData={graphData} conflictPairs={liveConflictPairs} selectedNode={selectedNode} onSelectNode={setSelectedNode} targetNodePosition={targetNodePosition} />
                    </Canvas>
                  )}
                  <div style={{ position:"absolute", bottom:14, left:14, fontSize:10, color:T.dim, fontFamily:"monospace", lineHeight:1.7 }}><div>Drag → orbit · Scroll → zoom</div><div>Click node → camera flies to it</div></div>
                  {selectedNode && (
                    <div style={{ position:"absolute", top:14, left:14, fontSize:10, fontFamily:"monospace", color:T.accent, background:"rgba(79,110,247,0.12)", border:"1px solid rgba(79,110,247,0.3)", borderRadius:6, padding:"4px 10px" }}>
                      ● {selectedNode} — <span style={{ color:T.muted, cursor:"pointer" }} onClick={() => setSelectedNode(null)}>deselect ×</span>
                    </div>
                  )}
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
                  <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:12, padding:16 }}>
                    <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:12 }}>LEGEND</div>
                    <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                      {[{ color:T.accent, label:"Neutral node (no conflict)" }, { color:T.red, label:"Conflicted node" }, { color:"#F0455A66", label:"Conflict edge" }, { color:"#FFFFFF22", label:"Constraint edge" }].map((l,i) => (
                        <div key={i} style={{ display:"flex", alignItems:"center", gap:8, fontSize:11, color:T.muted }}><div style={{ width:10, height:10, borderRadius:"50%", background:l.color, flexShrink:0 }} />{l.label}</div>
                      ))}
                    </div>
                  </div>
                  <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:12, padding:16 }}>
                    <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:12 }}>NODES ({graphData?.nodes?.length || 0})</div>
                    <div style={{ display:"flex", flexDirection:"column", gap:5, maxHeight:220, overflowY:"auto" }}>
                      {(graphData?.nodes || []).map((n,i) => (
                        <div key={n.id} onClick={() => setSelectedNode(selectedNode===n.id ? null : n.id)}
                          style={{ display:"flex", alignItems:"center", gap:8, padding:"6px 8px", borderRadius:6, cursor:"pointer", background: selectedNode===n.id ? "rgba(79,110,247,0.12)" : "rgba(255,255,255,0.02)", border:`1px solid ${selectedNode===n.id ? "rgba(79,110,247,0.3)" : "transparent"}` }}>
                          <div style={{ width:7, height:7, borderRadius:"50%", background:(n.color?.hex || COURSE_PALETTE[i%COURSE_PALETTE.length].hex), flexShrink:0 }} />
                          <span style={{ fontSize:10, fontFamily:"monospace", color:T.muted }}>{n.id}</span>
                          <span style={{ fontSize:10, color:T.dim }}>{n.label || ""}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {liveConflictPairs.length > 0 && (
                    <div style={{ background:"rgba(240,69,90,0.06)", border:`1px solid rgba(240,69,90,0.2)`, borderRadius:12, padding:16 }}>
                      <div style={{ fontSize:10, color:T.red, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:10 }}>ACTIVE CONFLICTS</div>
                      {liveConflictPairs.map(([a,b],i) => (<div key={i} style={{ fontSize:10, color:T.muted, fontFamily:"monospace", padding:"3px 0" }}><span style={{ color:T.red }}>{a}</span> ↔ <span style={{ color:T.red }}>{b}</span></div>))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* PLAYBACK TAB */}
          {tab === "playback" && (
            <div className="anim-up">
              <div style={{ marginBottom:20 }}><h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:20, fontWeight:800, marginBottom:4 }}>Optimization Playback</h2><p style={{ fontSize:12, color:T.muted }}>Scrub through solver states — conflicts resolve in real time · 3D graph synced inline</p></div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 380px", gap:16 }}>
                <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
                  <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:18 }}>
                    <TimetableGrid assignment={displayAssignment} conflictPairs={displayConflictPairs} changedId={currentFrame?.changed} title="LIVE SCHEDULE STATE" />
                  </div>
                  {solveResult?.history && solveResult.history.length > 1 && (
                    <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:18 }}>
                      <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:10 }}>ENERGY CURVE — OBJECTIVE FUNCTION</div>
                      <div style={{ height:120 }}><EnergyCurve history={solveResult.history} frameIndex={playback.frameIndex} /></div>
                    </div>
                  )}
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
                  <PlaybackPanel playback={playback} currentFrame={currentFrame} totalFrames={playback.totalFrames} solveResult={solveResult} />
                  <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:12, padding:18 }}>
                    <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:14 }}>CONFLICT GRAPH SYNC</div>
                    <div style={{ height:200, background:T.surface2, borderRadius:10, overflow:"hidden" }}>
                      {graphData && (
                        <Canvas camera={{ position:[0,2,9], fov:55 }} gl={{ antialias:true, alpha:true }} style={{ background:"transparent" }}>
                          <GraphScene graphData={graphData} conflictPairs={displayConflictPairs} selectedNode={selectedNode} onSelectNode={setSelectedNode} targetNodePosition={targetNodePosition} compact />
                        </Canvas>
                      )}
                    </div>
                    <div style={{ fontSize:10, color:T.dim, marginTop:10 }}>Red nodes = conflicts at current playback state</div>
                  </div>
                  {currentFrame && (
                    <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:12, padding:16 }}>
                      <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:10 }}>FRAME DETAIL</div>
                      <div style={{ display:"flex", flexDirection:"column", gap:6, fontSize:11, fontFamily:"monospace" }}>
                        <div><span style={{ color:T.dim }}>iteration: </span><span style={{ color:T.text }}>{currentFrame.iteration}</span></div>
                        <div><span style={{ color:T.dim }}>conflicts: </span><span style={{ color: currentFrame.conflicts===0 ? T.green : T.red }}>{currentFrame.conflicts}</span></div>
                        <div><span style={{ color:T.dim }}>soft score: </span><span style={{ color:T.cyan }}>{currentFrame.soft}%</span></div>
                        {currentFrame.temperature && <div><span style={{ color:T.dim }}>temperature: </span><span style={{ color:T.amber }}>{currentFrame.temperature.toFixed(3)}</span></div>}
                        {currentFrame.changed && <div><span style={{ color:T.dim }}>last moved: </span><span style={{ color:T.purple }}>{currentFrame.changed}</span></div>}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SCHEDULE TAB */}
          {tab === "schedule" && (
            <div className="anim-up">
              <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:20, fontWeight:800, marginBottom:4 }}>Master Timetable</h2>
              <p style={{ fontSize:12, color:T.muted, marginBottom:20 }}>Final solved schedule — zero conflict state</p>
              <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:20 }}>
                <TimetableGrid assignment={solveResult?.assignment || null} conflictPairs={[]} title={solveResult ? `${(solveResult.algo||"").toUpperCase()} · ${solveResult.time}ms · ${solveResult.conflicts} conflicts` : "RUN A SOLVER FIRST"} />
              </div>
            </div>
          )}

          {/* ANALYTICS TAB */}
          {tab === "analytics" && (
            <div className="anim-up">
              <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:20, fontWeight:800, marginBottom:20 }}>Analytics</h2>
              <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:20, marginBottom:16 }}>
                <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:16 }}>ALGORITHM BENCHMARK</div>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
                  {[{ k:"backtracking", l:"Backtracking + MRV", c:T.accent }, { k:"minconflicts", l:"Min-Conflicts", c:T.green }, { k:"annealing", l:"Simulated Annealing", c:T.amber }].map(({ k, l, c }) => {
                    const r = allResults[k];
                    return (
                      <div key={k} style={{ background:T.surface2, borderRadius:10, padding:16, border:`1px solid ${r ? c+"22" : T.border}` }}>
                        <div style={{ fontSize:11, fontWeight:700, color:c, marginBottom:10 }}>{l}</div>
                        {r ? (<><div style={{ fontSize:28, fontWeight:800, fontFamily:"'Sora',sans-serif", color:c, lineHeight:1 }}>{r.time}ms</div><div style={{ fontSize:10, color:T.muted, fontFamily:"monospace", marginTop:6 }}>{r.conflicts} conflicts · {r.soft}% soft · {(r.history||[]).length} states</div></>) : <div style={{ fontSize:11, color:T.dim }}>Not run yet</div>}
                      </div>
                    );
                  })}
                </div>
              </div>
              {allResults.annealing?.history?.length > 1 && (
                <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:20, marginBottom:16 }}>
                  <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:10 }}>SIMULATED ANNEALING — ENERGY FUNCTION OVER TIME</div>
                  <div style={{ height:140 }}><EnergyCurve history={allResults.annealing.history} frameIndex={allResults.annealing.history.length - 1} /></div>
                </div>
              )}
              {datasetInfo && (
                <div style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:20, marginBottom:16 }}>
                  <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:14 }}>DATASET INFO</div>
                  <div style={{ display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap:12 }}>
                    {[
                      { label: "Classes", value: datasetInfo.num_classes, color: T.accent },
                      { label: "Rooms", value: datasetInfo.num_rooms, color: T.purple },
                      { label: "Students", value: datasetInfo.num_students, color: T.green },
                      { label: "Constraints", value: datasetInfo.num_constraints, color: T.amber },
                    ].map(m => (
                      <div key={m.label} style={{ background:T.surface2, borderRadius:8, padding:12 }}>
                        <div style={{ fontSize:22, fontWeight:800, fontFamily:"'Sora',sans-serif", color:m.color }}>{m.value}</div>
                        <div style={{ fontSize:9, color:T.dim, marginTop:2 }}>{m.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
                {[
                  { title:"ROOM UTILIZATION", items: (datasetInfo?.rooms || DATASET.rooms).map(r => { const usage = solveResult?.assignment ? Object.values(solveResult.assignment).filter(v => v.roomId === (r.id || r.name)).length : 0; return { label: r.name || r.id, value: usage, max: 5 }; }), color: T.purple },
                  { title:"COURSE LOAD", items: (datasetInfo?.courses || []).slice(0, 10).map(c => ({ label: c.id, value: c.num_classes, max: 5 })), color: T.amber },
                ].map(panel => (
                  <div key={panel.title} style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:14, padding:20 }}>
                    <div style={{ fontSize:10, color:T.muted, letterSpacing:"0.12em", fontFamily:"monospace", marginBottom:14 }}>{panel.title}</div>
                    {panel.items.map((item,i) => (
                      <div key={i} style={{ marginBottom:10 }}>
                        <div style={{ display:"flex", justifyContent:"space-between", fontSize:11, color:T.muted, marginBottom:4 }}><span>{item.label}</span><span style={{ fontFamily:"monospace", color:panel.color }}>{item.value}</span></div>
                        <div style={{ background:"rgba(255,255,255,0.05)", borderRadius:3, height:4 }}><div style={{ width:`${Math.min((item.value/Math.max(item.max,1))*100, 100)}%`, height:"100%", background:panel.color, borderRadius:3, transition:"width 0.7s ease" }} /></div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI TAB */}
          {tab === "ai" && (
            <div className="anim-up">
              <h2 style={{ fontFamily:"'Sora',sans-serif", fontSize:20, fontWeight:800, marginBottom:6 }}>AI Timetabling Assistant</h2>
              <p style={{ fontSize:12, color:T.muted, marginBottom:20 }}>Powered by Claude — streaming responses with structured optimization suggestions</p>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
                {["Analyze room utilization","Identify bottlenecks","Suggest slot for new AI Ethics course","Who is overloaded?"].map(s => (
                  <button key={s} onClick={() => setAiPrompt(s)} style={{ padding:"5px 12px", borderRadius:20, fontSize:11, cursor:"pointer", fontFamily:"inherit", background:"rgba(255,255,255,0.04)", border:`1px solid ${T.border}`, color:T.muted, transition:"all 0.15s" }}>{s}</button>
                ))}
              </div>
              <div style={{ display:"flex", gap:10, marginBottom:18 }}>
                <textarea value={aiPrompt} onChange={e => setAiPrompt(e.target.value)} onKeyDown={e => { if(e.key==="Enter"&&(e.ctrlKey||e.metaKey)) handleAI(); }} placeholder="Ask anything… (Ctrl+Enter)" rows={3}
                  style={{ flex:1, background:T.surface, border:`1px solid ${T.border}`, color:T.text, padding:"12px 14px", borderRadius:10, fontSize:12, fontFamily:"inherit", resize:"vertical", lineHeight:1.6 }} />
                <button onClick={handleAI} disabled={aiLoading}
                  style={{ padding:"12px 20px", borderRadius:10, fontSize:13, fontWeight:700, fontFamily:"inherit", cursor: aiLoading ? "not-allowed" : "pointer", border:"none", background:`linear-gradient(135deg, ${T.accent}, ${T.purple})`, color:"#fff", alignSelf:"stretch" }}>
                  {aiLoading ? <span style={{ display:"inline-block", animation:"spin 0.7s linear infinite" }}>◌</span> : "→"}
                </button>
              </div>
              {(aiResponse || aiLoading) && (
                <div style={{ background:T.surface, border:`1px solid rgba(79,110,247,0.2)`, borderRadius:12, padding:20, marginBottom:14 }}>
                  <div style={{ fontSize:9, color:T.accent, letterSpacing:"0.15em", fontFamily:"monospace", marginBottom:12 }}>◈ CLAUDE {aiLoading ? "STREAMING" : "ANALYSIS"}{aiLoading && <span style={{ marginLeft:8, fontSize:8, color:T.amber }}>● LIVE</span>}</div>
                  <p style={{ fontSize:13, color:T.muted, lineHeight:1.8 }}>{aiResponse}{aiLoading && <span className="cursor-blink" style={{ display:"inline-block", width:2, height:14, background:T.accent, marginLeft:2, verticalAlign:"middle" }} />}</p>
                </div>
              )}
              {aiSuggestions.length > 0 && (
                <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                  {aiSuggestions.map((s,i) => {
                    const impactColor = s.impact==="high" ? T.red : s.impact==="medium" ? T.amber : T.green;
                    return (
                      <div key={i} style={{ background:T.surface, border:`1px solid ${T.border}`, borderRadius:10, padding:"14px 16px", display:"flex", gap:12, animation:`slideIn 0.3s ease ${i*0.06}s both` }}>
                        <div style={{ width:26, height:26, borderRadius:6, background:`${impactColor}18`, color:impactColor, display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:700, fontFamily:"monospace", flexShrink:0 }}>{i+1}</div>
                        <div style={{ flex:1 }}><div style={{ fontSize:12, fontWeight:600, marginBottom:3 }}>{s.title}</div><div style={{ fontSize:11, color:T.muted, lineHeight:1.6 }}>{s.description}</div></div>
                        <span style={{ fontSize:9, padding:"3px 7px", borderRadius:5, fontFamily:"monospace", background:`${impactColor}12`, color:impactColor, alignSelf:"flex-start" }}>{s.impact}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
