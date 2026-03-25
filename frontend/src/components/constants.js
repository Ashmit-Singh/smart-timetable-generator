// Design tokens & dataset for ChronoGrid Elite v4.0

export const T = {
  bg: "#04040A",
  surface: "#0C0C15",
  surface2: "#12121E",
  border: "rgba(255,255,255,0.055)",
  borderHover: "rgba(255,255,255,0.12)",
  text: "#E8E8F0",
  muted: "#5C6070",
  dim: "#2A2D3A",
  accent: "#4F6EF7",
  accentGlow: "rgba(79,110,247,0.25)",
  green: "#1EE07F",
  red: "#F0455A",
  amber: "#F5A524",
  cyan: "#06D6D6",
  purple: "#9B6EF7",
  pink: "#F06EAB",
};

export const COURSE_PALETTE = [
  { hex: "#4F6EF7", glow: "rgba(79,110,247,0.6)" },
  { hex: "#1EE07F", glow: "rgba(30,224,127,0.6)" },
  { hex: "#F0455A", glow: "rgba(240,69,90,0.6)" },
  { hex: "#F5A524", glow: "rgba(245,165,36,0.6)" },
  { hex: "#9B6EF7", glow: "rgba(155,110,247,0.6)" },
  { hex: "#06D6D6", glow: "rgba(6,214,214,0.6)" },
  { hex: "#F06EAB", glow: "rgba(240,110,171,0.6)" },
  { hex: "#2ED9C3", glow: "rgba(46,217,195,0.6)" },
  { hex: "#FF8C42", glow: "rgba(255,140,66,0.6)" },
  { hex: "#B06EF7", glow: "rgba(176,110,247,0.6)" },
];

export const DAYS = ["MON", "TUE", "WED", "THU", "FRI"];
export const SLOTS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];

export const DATASET = {
  courses: [
    { id: "CS101",   name: "Data Structures",   credits: 4, enrolled: 65, type: "lecture" },
    { id: "CS201",   name: "Algorithms",         credits: 4, enrolled: 58, type: "lecture" },
    { id: "CS301",   name: "Operating Systems",  credits: 4, enrolled: 72, type: "lecture" },
    { id: "CS401",   name: "Database Systems",   credits: 3, enrolled: 55, type: "lecture" },
    { id: "CS501",   name: "Computer Networks",  credits: 3, enrolled: 60, type: "lecture" },
    { id: "CS601",   name: "Machine Learning",   credits: 3, enrolled: 45, type: "lecture" },
    { id: "MATH101", name: "Discrete Math",      credits: 4, enrolled: 80, type: "lecture" },
    { id: "MATH201", name: "Linear Algebra",     credits: 3, enrolled: 70, type: "lecture" },
    { id: "CS-LAB1", name: "DS Lab",             credits: 2, enrolled: 30, type: "lab"     },
    { id: "CS-LAB2", name: "Networks Lab",       credits: 2, enrolled: 28, type: "lab"     },
  ],
  professors: [
    { id: "P001", name: "Dr. Arjun Mehta",   courses: ["CS101","CS-LAB1"],  preferred: [1,2,3] },
    { id: "P002", name: "Dr. Priya Sharma",  courses: ["CS201","CS301"],    preferred: [2,3,4] },
    { id: "P003", name: "Dr. Rajesh Kumar",  courses: ["CS401","CS501"],    preferred: [0,1,2] },
    { id: "P004", name: "Dr. Sunita Patel",  courses: ["CS601","MATH101"],  preferred: [3,4,5] },
    { id: "P005", name: "Dr. Vikram Singh",  courses: ["MATH201","CS-LAB2"],preferred: [1,2,6] },
  ],
  rooms: [
    { id: "R101", name: "Hall A",   capacity: 100, type: "lecture" },
    { id: "R102", name: "Hall B",   capacity: 80,  type: "lecture" },
    { id: "R103", name: "Room C",   capacity: 70,  type: "lecture" },
    { id: "R104", name: "Room D",   capacity: 60,  type: "lecture" },
    { id: "LAB1", name: "CS Lab 1", capacity: 35,  type: "lab"     },
    { id: "LAB2", name: "CS Lab 2", capacity: 35,  type: "lab"     },
  ],
};

export const colorMap = {};
DATASET.courses.forEach((c, i) => { colorMap[c.id] = COURSE_PALETTE[i % COURSE_PALETTE.length]; });
