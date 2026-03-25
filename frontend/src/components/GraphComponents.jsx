"use client";
// Three.js graph components: CameraController, GraphNode, GraphEdge, GraphScene
import { useState, useEffect, useRef, useCallback, useMemo, memo } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Html, Line, Billboard } from "@react-three/drei";

// Camera fly-to controller
export function CameraController({ targetNodePosition }) {
  const { camera } = useThree();
  const controlsRef = useRef();
  const targetPos = useRef(new THREE.Vector3(0, 2, 9));
  const targetLook = useRef(new THREE.Vector3(0, 0, 0));

  useEffect(() => {
    if (targetNodePosition) {
      const [x, y, z] = targetNodePosition;
      targetPos.current.copy(new THREE.Vector3(x, y + 1.5, z + 4));
      targetLook.current.set(x, y, z);
    } else {
      targetPos.current.set(0, 2, 9);
      targetLook.current.set(0, 0, 0);
    }
  }, [targetNodePosition]);

  useFrame(() => {
    camera.position.lerp(targetPos.current, 0.05);
    if (controlsRef.current) {
      controlsRef.current.target.lerp(targetLook.current, 0.05);
      controlsRef.current.update();
    }
  });

  return (
    <OrbitControls ref={controlsRef} enableDamping dampingFactor={0.06} rotateSpeed={0.6} zoomSpeed={0.8} minDistance={3} maxDistance={18} autoRotate autoRotateSpeed={0.35} />
  );
}

// Graph Node
export const GraphNode = memo(function GraphNode({ node, isHovered, isConflicted, isSelected, onClick, onHover }) {
  const meshRef = useRef();
  const glowRef = useRef();
  const phase = useRef(Math.random() * Math.PI * 2);
  const pos = node.position || [0, 0, 0];
  const nodeColor = typeof node.color === "string" ? node.color : node.color?.hex || "#4F6EF7";
  const nodeGlow = typeof node.color === "string" ? node.color + "99" : node.color?.glow || "rgba(79,110,247,0.6)";
  const color = isConflicted ? "#F0455A" : nodeColor;
  const emissiveColor = isConflicted ? "#aa1122" : nodeColor;

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;
    meshRef.current.position.y = pos[1] + Math.sin(t * 0.8 + phase.current) * 0.12;
    const targetScale = isSelected ? 1.5 : isHovered ? 1.25 : isConflicted ? 1.1 : 1.0;
    meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.12);
    if (glowRef.current) {
      const glowScale = targetScale * (1 + Math.sin(t * 2 + phase.current) * 0.08);
      glowRef.current.scale.setScalar(glowScale * 1.6);
      glowRef.current.material.opacity = isConflicted ? 0.35 + Math.sin(t * 4) * 0.15 : 0.15 + Math.sin(t * 1.5 + phase.current) * 0.05;
    }
  });

  return (
    <group position={pos}>
      <mesh ref={glowRef}><sphereGeometry args={[0.22, 16, 16]} /><meshBasicMaterial color={color} transparent opacity={0.15} depthWrite={false} /></mesh>
      <mesh ref={meshRef}
        onClick={(e) => { e.stopPropagation(); onClick(node.id); }}
        onPointerOver={(e) => { e.stopPropagation(); onHover(node.id); document.body.style.cursor = "pointer"; }}
        onPointerOut={() => { onHover(null); document.body.style.cursor = "default"; }}>
        <sphereGeometry args={[0.14, 32, 32]} />
        <meshStandardMaterial color={color} emissive={emissiveColor} emissiveIntensity={isConflicted ? 0.9 : isHovered ? 0.6 : 0.35} roughness={0.1} metalness={0.5} />
      </mesh>
      {isHovered && (
        <Billboard><Html distanceFactor={6} style={{ pointerEvents: "none", userSelect: "none" }}>
          <div style={{ background: "rgba(12,12,21,0.95)", border: `1px solid ${nodeColor}44`, borderRadius: 8, padding: "7px 11px", whiteSpace: "nowrap", boxShadow: `0 4px 20px ${nodeGlow}` }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: nodeColor, fontFamily: "monospace", letterSpacing: "0.05em" }}>{node.id}</div>
            <div style={{ fontSize: 10, color: "#9AA0B2", marginTop: 2 }}>{node.label}</div>
            {isConflicted && <div style={{ fontSize: 10, color: "#F0455A", marginTop: 3 }}>⚠ CONFLICT</div>}
          </div>
        </Html></Billboard>
      )}
    </group>
  );
});

// Graph Edge — useFrame MUST be called before any early return (rules of hooks)
export function GraphEdge({ edge, nodeMap, isActive, isConflicted }) {
  const lineRef = useRef();
  const src = nodeMap[edge.source];
  const tgt = nodeMap[edge.target];
  const color = isConflicted ? "#F0455A" : (edge.color || "#ffffff33");
  const opacity = isConflicted ? 0.85 : isActive ? 0.55 : 0.22;

  useFrame(() => {
    if (!lineRef.current) return;
    lineRef.current.material.opacity = THREE.MathUtils.lerp(lineRef.current.material.opacity, opacity, 0.08);
  });

  if (!src || !tgt) return null;

  return (
    <Line ref={lineRef} points={[new THREE.Vector3(...src.position), new THREE.Vector3(...tgt.position)]} color={color} lineWidth={isConflicted ? 2.5 : 1.2} transparent opacity={opacity} depthWrite={false} />
  );
}

// Full Graph Scene
export function GraphScene({ graphData, conflictPairs, selectedNode, onSelectNode, targetNodePosition, compact }) {
  const [hoveredNode, setHoveredNode] = useState(null);

  const nodeMap = useMemo(() => {
    const m = {};
    graphData.nodes.forEach((n, i) => {
      // Handle raw string nodes from backend (not yet normalized)
      const node = typeof n === "string" ? { id: n, label: n, position: [0, 0, 0], color: "#4F6EF7" } : n;
      m[node.id] = node;
    });
    return m;
  }, [graphData]);

  const conflictSet = useMemo(() => {
    const s = new Set();
    conflictPairs.forEach(([a, b]) => { s.add(a); s.add(b); });
    return s;
  }, [conflictPairs]);

  const conflictEdgeSet = useMemo(() => {
    const s = new Set();
    conflictPairs.forEach(([a, b]) => { s.add(`${a}-${b}`); s.add(`${b}-${a}`); });
    return s;
  }, [conflictPairs]);

  const handleNodeClick = useCallback((id) => {
    onSelectNode(id === selectedNode ? null : id);
  }, [selectedNode, onSelectNode]);

  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[0, 8, 0]} intensity={1.2} color="#4F6EF7" />
      <pointLight position={[5, -3, 5]} intensity={0.5} color="#9B6EF7" />
      <pointLight position={[-5, -3, -5]} intensity={0.5} color="#06D6D6" />
      <fog attach="fog" args={["#04040A", 12, 28]} />
      {graphData.edges.map((edge, i) => {
        const isConflicted2 = conflictEdgeSet.has(`${edge.source}-${edge.target}`) || conflictEdgeSet.has(`${edge.target}-${edge.source}`);
        const isActive = selectedNode && (edge.source === selectedNode || edge.target === selectedNode);
        return <GraphEdge key={i} edge={edge} nodeMap={nodeMap} isActive={isActive} isConflicted={isConflicted2} />;
      })}
      {Object.values(nodeMap).map((node, idx) => (
        <GraphNode key={node.id || `node_${idx}`} node={node} isHovered={!compact && hoveredNode === node.id} isConflicted={conflictSet.has(node.id)} isSelected={selectedNode === node.id} onClick={handleNodeClick} onHover={compact ? () => {} : setHoveredNode} />
      ))}
      <CameraController targetNodePosition={targetNodePosition} />
    </>
  );
}
