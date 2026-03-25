// Web Worker factory for solver — runs solver entirely off main thread
import { COURSE_PALETTE } from "./constants";

const WORKER_SOURCE = `
const DAYS_LEN = 5;
const SLOTS_LEN = 8;

class SolverEngine {
  constructor(dataset) {
    this.courses = dataset.courses;
    this.professors = dataset.professors;
    this.rooms = dataset.rooms;
    this._profByCourse = {};
    dataset.professors.forEach(p => p.courses.forEach(cid => { this._profByCourse[cid] = p; }));
    this._domains = this._buildDomains();
  }

  _buildDomains() {
    const domains = {};
    for (const course of this.courses) {
      const rooms = this.rooms.filter(r => r.capacity >= course.enrolled && r.type === course.type);
      const d = [];
      for (let day = 0; day < DAYS_LEN; day++)
        for (let slot = 0; slot < SLOTS_LEN; slot++)
          for (const room of rooms) d.push({ day, slot, roomId: room.id });
      domains[course.id] = d;
    }
    return domains;
  }

  countConflicts(assignment) {
    const entries = Object.entries(assignment);
    let c = 0;
    for (let i = 0; i < entries.length; i++) {
      for (let j = i + 1; j < entries.length; j++) {
        const [id1, v1] = entries[i], [id2, v2] = entries[j];
        if (v1.day !== v2.day || v1.slot !== v2.slot) continue;
        if (v1.roomId === v2.roomId) { c++; continue; }
        const p1 = this._profByCourse[id1], p2 = this._profByCourse[id2];
        if (p1 && p2 && p1.id === p2.id) c++;
      }
    }
    return c;
  }

  getConflictPairs(assignment) {
    const entries = Object.entries(assignment);
    const pairs = [];
    for (let i = 0; i < entries.length; i++) {
      for (let j = i + 1; j < entries.length; j++) {
        const [id1, v1] = entries[i], [id2, v2] = entries[j];
        if (v1.day !== v2.day || v1.slot !== v2.slot) continue;
        const roomConflict = v1.roomId === v2.roomId;
        const p1 = this._profByCourse[id1], p2 = this._profByCourse[id2];
        const profConflict = p1 && p2 && p1.id === p2.id;
        if (roomConflict || profConflict) pairs.push([id1, id2]);
      }
    }
    return pairs;
  }

  softScore(assignment) {
    let s = 0, t = 0;
    for (const [cid, val] of Object.entries(assignment)) {
      const prof = this._profByCourse[cid];
      if (prof && prof.preferred && prof.preferred.includes(val.slot)) s++;
      t++;
    }
    return t > 0 ? Math.round((s / t) * 100) : 0;
  }

  solveBacktracking(onFrame) {
    const t0 = performance.now();
    const stats = { backtracks: 0, nodes: 0 };
    const _bt = (assignment, domains) => {
      if (Object.keys(assignment).length === this.courses.length) return assignment;
      stats.nodes++;
      let best = null, bestSize = Infinity;
      for (const c of this.courses) {
        if (assignment[c.id] !== undefined) continue;
        const sz = (domains[c.id] || []).length;
        if (sz < bestSize) { bestSize = sz; best = c.id; }
      }
      if (!best) return null;
      for (const val of (domains[best] || [])) {
        let ok = true;
        const p = this._profByCourse[best];
        for (const [cid, v] of Object.entries(assignment)) {
          if (v.day !== val.day || v.slot !== val.slot) continue;
          if (v.roomId === val.roomId) { ok = false; break; }
          const p2 = this._profByCourse[cid];
          if (p && p2 && p.id === p2.id) { ok = false; break; }
        }
        if (!ok) continue;
        assignment[best] = val;
        const conflicts = this.countConflicts(assignment);
        if (stats.nodes % 5 === 0) {
          onFrame({ iteration: stats.nodes, assignment: { ...assignment }, conflicts, soft: this.softScore(assignment), changed: best });
        }
        const result = _bt(assignment, domains);
        if (result) return result;
        delete assignment[best];
        stats.backtracks++;
      }
      return null;
    };
    const domains = {};
    for (const c of this.courses) domains[c.id] = [...this._domains[c.id]];
    const result = _bt({}, domains);
    const time = Math.round(performance.now() - t0);
    if (result) onFrame({ iteration: stats.nodes, assignment: result, conflicts: 0, soft: this.softScore(result), changed: null });
    return { assignment: result, time, backtracks: stats.backtracks, nodes: stats.nodes, conflicts: result ? 0 : -1, soft: result ? this.softScore(result) : 0, algo: "backtracking" };
  }

  solveMinConflicts(maxIter, maxRestarts, onFrame) {
    maxIter = maxIter || 4000;
    maxRestarts = maxRestarts || 3;
    const t0 = performance.now();
    let bestResult = null, bestConflicts = Infinity;
    for (let restart = 0; restart < maxRestarts; restart++) {
      const assignment = {};
      for (const c of this.courses) {
        const dom = this._domains[c.id];
        assignment[c.id] = dom[Math.floor(Math.random() * dom.length)];
      }
      for (let iter = 0; iter < maxIter; iter++) {
        const conflicts = this.countConflicts(assignment);
        if (iter % 8 === 0 || conflicts < bestConflicts) {
          onFrame({ iteration: restart * maxIter + iter, assignment: { ...assignment }, conflicts, soft: this.softScore(assignment), changed: null, conflictPairs: this.getConflictPairs(assignment) });
        }
        if (conflicts === 0) {
          return { assignment, time: Math.round(performance.now() - t0), conflicts: 0, soft: this.softScore(assignment), iterations: iter, restarts: restart, algo: "minconflicts" };
        }
        const conflicted = this._findConflicted(assignment);
        if (!conflicted) break;
        const dom = this._domains[conflicted];
        let minC = Infinity, bestVals = [];
        for (const val of dom) {
          const c = this.countConflicts({ ...assignment, [conflicted]: val });
          if (c < minC) { minC = c; bestVals = [val]; }
          else if (c === minC) bestVals.push(val);
        }
        assignment[conflicted] = bestVals[Math.floor(Math.random() * bestVals.length)];
        if (conflicts < bestConflicts) { bestConflicts = conflicts; bestResult = { ...assignment }; }
      }
    }
    return { assignment: bestResult, time: Math.round(performance.now() - t0), conflicts: bestConflicts, soft: bestResult ? this.softScore(bestResult) : 0, algo: "minconflicts" };
  }

  _findConflicted(assignment) {
    const conflicted = [];
    const entries = Object.entries(assignment);
    for (const [id, val] of entries) {
      for (const [id2, val2] of entries) {
        if (id === id2) continue;
        if (val.day === val2.day && val.slot === val2.slot) {
          const p1 = this._profByCourse[id], p2 = this._profByCourse[id2];
          if (val.roomId === val2.roomId || (p1 && p2 && p1.id === p2.id)) {
            conflicted.push(id);
            break;
          }
        }
      }
    }
    return conflicted.length ? conflicted[Math.floor(Math.random() * conflicted.length)] : null;
  }

  solveSimulatedAnnealing(T0, cooling, maxIter, onFrame) {
    T0 = T0 || 80; cooling = cooling || 0.975; maxIter = maxIter || 6000;
    const t0 = performance.now();
    let current = {};
    for (const c of this.courses) {
      const dom = this._domains[c.id];
      current[c.id] = dom[Math.floor(Math.random() * dom.length)];
    }
    const energy = (a) => this.countConflicts(a) * 1000 + (100 - this.softScore(a));
    let E = energy(current);
    let best = { ...current }, bestE = E;
    let Temp = T0;
    for (let i = 0; i < maxIter; i++) {
      const keys = Object.keys(current);
      const cid = keys[Math.floor(Math.random() * keys.length)];
      const dom = this._domains[cid];
      const newVal = dom[Math.floor(Math.random() * dom.length)];
      const neighbor = { ...current, [cid]: newVal };
      const Enew = energy(neighbor);
      const delta = Enew - E;
      if (delta < 0 || Math.random() < Math.exp(-delta / Temp)) { current = neighbor; E = Enew; }
      if (E < bestE) { bestE = E; best = { ...current }; }
      Temp *= cooling;
      if (i % 12 === 0) {
        const conflicts = this.countConflicts(current);
        onFrame({ iteration: i, assignment: { ...current }, conflicts, soft: this.softScore(current), energy: E, temperature: Temp, changed: cid, conflictPairs: this.getConflictPairs(current) });
      }
    }
    return { assignment: best, time: Math.round(performance.now() - t0), conflicts: this.countConflicts(best), soft: this.softScore(best), algo: "annealing" };
  }

  buildConflictGraph() {
    const N = this.courses.length;
    const nodes = this.courses.map((c, i) => {
      const angle = (i / N) * Math.PI * 2;
      const radius = 3.5, spread = 0.4;
      return {
        id: c.id, label: c.name, color: COURSE_PALETTE[i % COURSE_PALETTE.length],
        position: [
          Math.cos(angle) * radius + (Math.random() - 0.5) * spread,
          (Math.random() - 0.5) * 2.5,
          Math.sin(angle) * radius + (Math.random() - 0.5) * spread,
        ],
      };
    });
    const edges = [];
    for (let i = 0; i < this.courses.length; i++) {
      for (let j = i + 1; j < this.courses.length; j++) {
        const ci = this.courses[i], cj = this.courses[j];
        const pi = this._profByCourse[ci.id], pj = this._profByCourse[cj.id];
        if (pi && pj && pi.id === pj.id)
          edges.push({ source: ci.id, target: cj.id, type: "professor", color: "#F0455A" });
      }
    }
    return { nodes, edges };
  }
}

const COURSE_PALETTE = ${JSON.stringify(COURSE_PALETTE)};

self.onmessage = function(e) {
  const { algo, dataset } = e.data;
  const engine = new SolverEngine(dataset);
  const onFrame = (frame) => { self.postMessage({ type: "frame", frame }); };
  let result;
  if (algo === "backtracking") result = engine.solveBacktracking(onFrame);
  else if (algo === "minconflicts") result = engine.solveMinConflicts(4000, 3, onFrame);
  else result = engine.solveSimulatedAnnealing(80, 0.975, 6000, onFrame);
  const graphData = engine.buildConflictGraph();
  self.postMessage({ type: "done", result, graphData });
};
`;

export function createSolverWorker() {
  const blob = new Blob([WORKER_SOURCE], { type: "application/javascript" });
  return new Worker(URL.createObjectURL(blob));
}

export function buildConflictGraphLocal(dataset) {
  const profByCourse = {};
  dataset.professors.forEach(p => p.courses.forEach(cid => { profByCourse[cid] = p; }));
  const N = dataset.courses.length;
  const nodes = dataset.courses.map((c, i) => {
    const angle = (i / N) * Math.PI * 2;
    const radius = 3.5, spread = 0.4;
    return {
      id: c.id, label: c.name, color: COURSE_PALETTE[i % COURSE_PALETTE.length],
      position: [
        Math.cos(angle) * radius + (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * 2.5,
        Math.sin(angle) * radius + (Math.random() - 0.5) * spread,
      ],
    };
  });
  const edges = [];
  for (let i = 0; i < dataset.courses.length; i++) {
    for (let j = i + 1; j < dataset.courses.length; j++) {
      const ci = dataset.courses[i], cj = dataset.courses[j];
      const pi = profByCourse[ci.id], pj = profByCourse[cj.id];
      if (pi && pj && pi.id === pj.id)
        edges.push({ source: ci.id, target: cj.id, type: "professor", color: "#F0455A" });
    }
  }
  return { nodes, edges };
}
