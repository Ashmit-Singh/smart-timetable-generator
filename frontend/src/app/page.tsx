"use client";

import dynamic from "next/dynamic";

// Dynamic import with SSR disabled — Three.js requires browser APIs (WebGL, Canvas)
const ChronoGrid = dynamic(() => import("@/components/ChronoGrid"), { ssr: false });

export default function Home() {
  return <ChronoGrid />;
}
