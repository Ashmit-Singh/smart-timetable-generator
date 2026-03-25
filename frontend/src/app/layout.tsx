import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ChronoGrid Elite — University Timetable AI",
  description: "Production-grade university timetable generator with 3D conflict graph visualization, Web Worker CSP solvers, and real-time optimization playback.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning style={{ margin: 0, padding: 0, background: "#04040A" }}>{children}</body>
    </html>
  );
}
