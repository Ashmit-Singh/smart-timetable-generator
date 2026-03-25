"use client";
// Timetable grid, Playback panel, Energy curve, and Btn components
import { useState, useEffect, useRef, useMemo, memo } from "react";
import { T, DAYS, SLOTS, DATASET, colorMap } from "./constants";

// ── BTN ──
export function Btn({ children, onClick, small, style }) {
  const [hover, setHover] = useState(false);
  return (
    <button onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ background: hover ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.04)", border: `1px solid ${T.border}`, color: T.muted, borderRadius: 6, padding: small ? "6px 10px" : "8px 16px", fontSize: 12, cursor: "pointer", fontFamily: "monospace", transition: "all 0.15s", ...style }}>
      {children}
    </button>
  );
}

// ── BUILD GRID ──
function buildGrid(assignment, filterFn) {
  const grid = {};
  DAYS.forEach(d => { grid[d] = {}; SLOTS.forEach(s => { grid[d][s] = null; }); });
  if (!assignment) return grid;
  for (const [cid, val] of Object.entries(assignment)) {
    if (filterFn && !filterFn(cid)) continue;
    const daysArr = val.days !== undefined ? val.days : [val.day];
    const slot = SLOTS[val.slot];
    if (!slot) continue;
    
    for (const dIdx of daysArr) {
      const day = DAYS[dIdx];
      if (!day) continue;
      const course = val.course || DATASET.courses.find(c => c.id === cid);
      const prof = val.prof || DATASET.professors.find(p => p.courses.includes(cid));
      const room = val.room || DATASET.rooms.find(r => r.id === val.roomId);
      grid[day][slot] = { course, prof, room, color: val.color || colorMap[cid] };
    }
  }
  return grid;
}

// ── TIMETABLE GRID ──
export const TimetableGrid = memo(function TimetableGrid({ assignment, conflictPairs, changedId, filterFn, title }) {
  const grid = useMemo(() => buildGrid(assignment, filterFn), [assignment, filterFn]);
  const conflictSet = useMemo(() => {
    const s = new Set();
    (conflictPairs || []).forEach(([a, b]) => { s.add(a); s.add(b); });
    return s;
  }, [conflictPairs]);

  return (
    <div>
      {title && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: T.muted, letterSpacing: "0.1em", fontFamily: "monospace" }}>{title}</span>
          {conflictSet.size > 0 && (
            <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: "rgba(240,69,90,0.12)", color: T.red, fontFamily: "monospace", border: "1px solid rgba(240,69,90,0.25)" }}>
              ⚠ {conflictPairs?.length} conflicts
            </span>
          )}
        </div>
      )}
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "separate", borderSpacing: "2px", width: "100%", minWidth: 640 }}>
          <thead><tr>
            <th style={{ width: 64, padding: "6px 8px", fontSize: 9, color: T.dim, textAlign: "left", fontFamily: "monospace", letterSpacing: "0.12em" }}>TIME</th>
            {DAYS.map(d => (<th key={d} style={{ padding: "6px 8px", fontSize: 9, letterSpacing: "0.15em", color: T.muted, textAlign: "center", fontWeight: 700 }}>{d}</th>))}
          </tr></thead>
          <tbody>
            {SLOTS.map(slot => (
              <tr key={slot}>
                <td style={{ padding: "2px 8px", fontSize: 9, color: T.dim, fontFamily: "monospace", verticalAlign: "middle" }}>{slot}</td>
                {DAYS.map(day => {
                  const cell = grid[day]?.[slot];
                  const isConflict = cell && conflictSet.has(cell.course?.id);
                  const isChanged = cell && cell.course?.id === changedId;
                  return (
                    <td key={day} style={{ padding: 0, verticalAlign: "top" }}>
                      {cell ? (
                        <div style={{
                          background: isConflict ? "rgba(240,69,90,0.18)" : cell.color.hex + "22",
                          border: `1px solid ${isConflict ? "rgba(240,69,90,0.5)" : isChanged ? cell.color.hex + "88" : cell.color.hex + "33"}`,
                          borderRadius: 6, padding: "7px 9px", minHeight: 60, position: "relative",
                          transition: "all 0.25s cubic-bezier(0.4,0,0.2,1)",
                          boxShadow: isConflict ? `0 0 12px rgba(240,69,90,0.3)` : isChanged ? `0 0 12px ${cell.color.glow}` : "none",
                        }}>
                          {isConflict && <div style={{ position: "absolute", top: 4, right: 5, width: 5, height: 5, borderRadius: "50%", background: T.red, boxShadow: `0 0 6px ${T.red}` }} />}
                          {isChanged && !isConflict && <div style={{ position: "absolute", top: 4, right: 5, width: 5, height: 5, borderRadius: "50%", background: T.green, boxShadow: `0 0 6px ${T.green}` }} />}
                          <div style={{ fontSize: 10, fontWeight: 700, color: cell.color.hex, lineHeight: 1.3, marginBottom: 2 }}>{cell.course?.name}</div>
                          <div style={{ fontSize: 9, color: T.muted }}>{cell.prof?.name.split(" ").slice(-1)[0]}</div>
                          <div style={{ fontSize: 8, color: T.dim, fontFamily: "monospace" }}>{cell.room?.name}</div>
                        </div>
                      ) : (
                        <div style={{ minHeight: 60, borderRadius: 6, background: "rgba(255,255,255,0.012)", border: "1px solid rgba(255,255,255,0.03)" }} />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});

// ── PLAYBACK HOOK ──
export function usePlayback(history) {
  const [frameIndex, setFrameIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const speedRef = useRef(speed);
  const intervalRef = useRef(null);
  const historyRef = useRef(history);

  useEffect(() => { historyRef.current = history; }, [history]);
  useEffect(() => { speedRef.current = speed; }, [speed]);
  useEffect(() => { setFrameIndex(0); setPlaying(false); }, [history]);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (!playing || !history || history.length === 0) return;
    const tick = () => {
      const delay = Math.max(80, 600 / speedRef.current);
      intervalRef.current = setTimeout(() => {
        setFrameIndex(prev => {
          if (prev >= historyRef.current.length - 1) { setPlaying(false); return prev; }
          return prev + 1;
        });
        if (playing) tick();
      }, delay);
    };
    tick();
    return () => clearTimeout(intervalRef.current);
  }, [playing, history]);

  const currentFrame = history && history.length > 0 ? history[Math.min(frameIndex, history.length - 1)] : null;

  return {
    frameIndex, setFrameIndex, playing, setPlaying, speed, setSpeed, currentFrame,
    totalFrames: history?.length || 0,
    stepForward: () => setFrameIndex(p => Math.min(p + 1, (history?.length || 1) - 1)),
    stepBack: () => setFrameIndex(p => Math.max(p - 1, 0)),
    jumpToEnd: () => setFrameIndex((history?.length || 1) - 1),
    jumpToStart: () => setFrameIndex(0),
  };
}

// ── PLAYBACK PANEL ──
export function PlaybackPanel({ playback, currentFrame, totalFrames, solveResult }) {
  const { frameIndex, setFrameIndex, playing, setPlaying, speed, setSpeed, stepForward, stepBack, jumpToStart, jumpToEnd } = playback;

  if (!solveResult || !solveResult.history || solveResult.history.length === 0) {
    return (
      <div style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 12, padding: 24, textAlign: "center" }}>
        <div style={{ color: T.dim, fontSize: 13 }}>Run a solver to enable optimization playback</div>
      </div>
    );
  }

  const progress = totalFrames > 1 ? frameIndex / (totalFrames - 1) : 0;
  const conflicts = currentFrame?.conflicts ?? 0;
  const soft = currentFrame?.soft ?? 0;
  const algoColors = { minconflicts: T.green, annealing: T.amber, backtracking: T.accent };
  const accentColor = algoColors[solveResult.algo] || T.accent;

  return (
    <div style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 14, overflow: "hidden" }}>
      <div style={{ padding: "14px 20px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: playing ? accentColor : T.muted, boxShadow: playing ? `0 0 8px ${accentColor}` : "none", transition: "all 0.3s" }} />
          <span style={{ fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: "0.12em", fontFamily: "monospace" }}>OPTIMIZATION PLAYBACK</span>
        </div>
        <div style={{ fontSize: 10, color: T.dim, fontFamily: "monospace" }}>{(solveResult.algo || "").toUpperCase()} · {totalFrames} states</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 1, background: T.border }}>
        {[
          { label: "Iteration", value: currentFrame?.iteration ?? 0, color: T.text },
          { label: "Conflicts", value: conflicts, color: conflicts === 0 ? T.green : T.red },
          { label: "Soft Score", value: `${soft}%`, color: T.cyan },
          { label: "Progress", value: `${Math.round(progress * 100)}%`, color: accentColor },
        ].map(m => (
          <div key={m.label} style={{ background: T.surface, padding: "12px 16px" }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: m.color, fontFamily: "monospace", transition: "color 0.3s" }}>{m.value}</div>
            <div style={{ fontSize: 9, color: T.dim, letterSpacing: "0.1em", marginTop: 2 }}>{m.label}</div>
          </div>
        ))}
      </div>
      <div style={{ padding: "16px 20px" }}>
        <div style={{ marginBottom: 14 }}>
          <input type="range" min={0} max={Math.max(0, totalFrames - 1)} value={frameIndex} onChange={e => setFrameIndex(Number(e.target.value))} style={{ width: "100%", accentColor }} />
          <div style={{ display: "flex", gap: 1, marginTop: 6 }}>
            {(solveResult.history || []).map((frame, i) => (
              <div key={i} onClick={() => setFrameIndex(i)} title={`iter ${frame.iteration}: ${frame.conflicts} conflicts`}
                style={{ flex: 1, height: 6, borderRadius: 1, background: frame.conflicts === 0 ? T.green : frame.conflicts < 3 ? T.amber : T.red, opacity: i === frameIndex ? 1 : 0.35, cursor: "pointer", transition: "opacity 0.15s" }} />
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Btn onClick={jumpToStart} small>⟪</Btn>
          <Btn onClick={stepBack} small>‹</Btn>
          <Btn onClick={() => setPlaying(p => !p)} style={{ background: playing ? "rgba(240,69,90,0.15)" : "rgba(79,110,247,0.15)", borderColor: playing ? "rgba(240,69,90,0.4)" : "rgba(79,110,247,0.4)", color: playing ? T.red : T.accent, flex: 1 }}>
            {playing ? "⏸ Pause" : "▶ Play"}
          </Btn>
          <Btn onClick={stepForward} small>›</Btn>
          <Btn onClick={jumpToEnd} small>⟫</Btn>
          <select value={speed} onChange={e => setSpeed(Number(e.target.value))}
            style={{ background: T.surface2, border: `1px solid ${T.border}`, color: T.muted, borderRadius: 6, padding: "6px 10px", fontSize: 11, fontFamily: "monospace" }}>
            <option value={0.5}>0.5×</option><option value={1}>1×</option><option value={2}>2×</option><option value={5}>5×</option><option value={10}>10×</option>
          </select>
        </div>
      </div>
    </div>
  );
}

// ── ENERGY CURVE ──
export function EnergyCurve({ history, frameIndex }) {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !history || history.length < 2) return;
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.offsetWidth, H = canvas.offsetHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    const pad = { t: 16, r: 12, b: 28, l: 44 };
    const values = history.map(f => f.conflicts * 1000 + (100 - (f.soft || 0)));
    const maxV = Math.max(...values, 1);
    const minV = Math.min(...values, 0);
    const toX = i => pad.l + (i / (history.length - 1)) * (W - pad.l - pad.r);
    const toY = v => pad.t + (1 - (v - minV) / Math.max(maxV - minV, 1)) * (H - pad.t - pad.b);
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i <= 3; i++) {
      const y = pad.t + (i / 3) * (H - pad.t - pad.b);
      ctx.beginPath(); ctx.strokeStyle = "rgba(255,255,255,0.04)"; ctx.lineWidth = 1;
      ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    }
    const grad = ctx.createLinearGradient(0, pad.t, 0, H - pad.b);
    grad.addColorStop(0, "rgba(79,110,247,0.25)"); grad.addColorStop(1, "rgba(79,110,247,0)");
    ctx.beginPath(); ctx.moveTo(toX(0), H - pad.b);
    history.forEach((f, i) => ctx.lineTo(toX(i), toY(values[i])));
    ctx.lineTo(toX(history.length - 1), H - pad.b);
    ctx.closePath(); ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath();
    history.forEach((f, i) => i === 0 ? ctx.moveTo(toX(i), toY(values[i])) : ctx.lineTo(toX(i), toY(values[i])));
    ctx.strokeStyle = "#4F6EF7"; ctx.lineWidth = 1.5;
    ctx.shadowColor = "#4F6EF7"; ctx.shadowBlur = 6; ctx.stroke(); ctx.shadowBlur = 0;
    if (frameIndex >= 0 && frameIndex < history.length) {
      const cx = toX(frameIndex), cy = toY(values[frameIndex]);
      ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#4F6EF7"; ctx.shadowColor = "#4F6EF7"; ctx.shadowBlur = 10; ctx.fill(); ctx.shadowBlur = 0;
    }
    ctx.fillStyle = "#374151"; ctx.font = `10px monospace`; ctx.textAlign = "right";
    ctx.fillText(Math.round(maxV), pad.l - 4, pad.t + 6);
    ctx.fillText(Math.round(minV), pad.l - 4, H - pad.b + 2);
  }, [history, frameIndex]);
  return <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />;
}

// ── WEBGL BACKGROUND ──
export function WebGLBg() {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const gl = canvas.getContext("webgl");
    if (!gl) return;
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; gl.viewport(0, 0, canvas.width, canvas.height); };
    resize(); window.addEventListener("resize", resize);
    const N = 100;
    const pos = new Float32Array(N * 2);
    const vel = new Float32Array(N * 2);
    for (let i = 0; i < N; i++) { pos[i*2]=Math.random()*2-1; pos[i*2+1]=Math.random()*2-1; vel[i*2]=(Math.random()-.5)*.0006; vel[i*2+1]=(Math.random()-.5)*.0006; }
    const vs = `attribute vec2 a;void main(){gl_PointSize=1.6;gl_Position=vec4(a,0,1);}`;
    const fs = `precision mediump float;void main(){float d=length(gl_PointCoord-.5);if(d>.5)discard;gl_FragColor=vec4(.31,.43,.97,.28);}`;
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x,s); gl.compileShader(x); return x; };
    const prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER,vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER,fs));
    gl.linkProgram(prog); gl.useProgram(prog);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buf);
    const loc = gl.getAttribLocation(prog,"a"); gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
    gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
    let raf;
    const draw = () => {
      for(let i=0;i<N;i++){pos[i*2]+=vel[i*2];pos[i*2+1]+=vel[i*2+1];if(Math.abs(pos[i*2])>1)vel[i*2]*=-1;if(Math.abs(pos[i*2+1])>1)vel[i*2+1]*=-1;}
      gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.bufferData(gl.ARRAY_BUFFER,pos,gl.DYNAMIC_DRAW); gl.drawArrays(gl.POINTS,0,N);
      raf=requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize",resize); };
  }, []);
  return <canvas ref={ref} style={{ position:"fixed", top:0, left:0, width:"100%", height:"100%", pointerEvents:"none", zIndex:0, opacity:0.5 }} />;
}
