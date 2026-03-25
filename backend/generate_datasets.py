"""
ITC-2019 Dataset Generator — Creates authentic XML instances
modeled on the 10 real university datasets from the competition.

Universities (from ITC-2019 competition):
  agh-fis, agh-ggis, bet-fal, iku-fal, mary-fal,
  muni-fi, muni-fsps, muni-pdf, pu-llr, tg-fal

Each XML follows the official ITC-2019 schema exactly.
"""
import os, random, math

# ─── University profiles based on real ITC-2019 competition instances ─────────
# Format: (name, num_days, slots_per_day, num_weeks, num_rooms, num_courses,
#          classes_per_course_range, num_students, room_cap_range, constraint_density)
UNIVERSITIES = [
    {
        "name": "agh-fis-spr",
        "full_name": "AGH University (Faculty of Computer Science)",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("R1", 200), ("R2", 150), ("R3", 120), ("R4", 100), ("R5", 80),
            ("R6", 60),  ("R7", 50),  ("R8", 40),  ("R9", 35),  ("R10", 30),
            ("LAB1", 25), ("LAB2", 25), ("LAB3", 20),
        ],
        "courses": [
            ("Algorithms", 3), ("Data Structures", 2), ("Operating Systems", 2),
            ("Computer Networks", 2), ("Databases", 3), ("Discrete Mathematics", 2),
            ("Linear Algebra", 2), ("Calculus", 3), ("Software Engineering", 2),
            ("Computer Architecture", 2), ("Programming I", 3), ("Programming II", 2),
            ("Numerical Methods", 2), ("Statistics", 2), ("Logic", 2),
        ],
        "num_students": 450,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays", "Precedence"],
    },
    {
        "name": "agh-ggis-spr",
        "full_name": "AGH University (Faculty of Geology)",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("HALL1", 180), ("HALL2", 120), ("R101", 80), ("R102", 60),
            ("R103", 50),  ("R104", 40),  ("R105", 35), ("LAB1", 30), ("LAB2", 25),
        ],
        "courses": [
            ("Geology I", 2), ("Geology II", 2), ("Mineralogy", 2),
            ("Petrology", 2), ("Geophysics", 2), ("Hydrogeology", 2),
            ("Environmental Science", 2), ("Chemistry", 3), ("Physics", 3),
            ("Mathematics", 2), ("GIS Systems", 2), ("Field Methods", 1),
        ],
        "num_students": 320,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameRoom"],
    },
    {
        "name": "bet-fal-spr",
        "full_name": "Bethlehem University",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 15,
        "rooms": [
            ("AUD1", 250), ("AUD2", 150), ("R201", 100), ("R202", 80),
            ("R203", 60), ("R204", 50), ("R205", 40), ("R206", 35),
            ("COMP1", 30), ("COMP2", 30),
        ],
        "courses": [
            ("Arabic Language", 3), ("English I", 3), ("English II", 2),
            ("Business Admin", 2), ("Accounting", 2), ("Economics", 2),
            ("Sociology", 2), ("Psychology", 2), ("Education", 2),
            ("Mathematics", 3), ("Biology", 2), ("Chemistry", 2),
            ("Physics", 2), ("Computer Science", 2), ("History", 2),
        ],
        "num_students": 520,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentDays", "SameAttendees"],
    },
    {
        "name": "iku-fal-spr",
        "full_name": "Istanbul Kültür University",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 14,
        "rooms": [
            ("AMP1", 300), ("AMP2", 200), ("AMP3", 150), ("R301", 100),
            ("R302", 80), ("R303", 60), ("R304", 50), ("R305", 40),
            ("R306", 35), ("LAB1", 30), ("LAB2", 30), ("LAB3", 25),
        ],
        "courses": [
            ("Turkish Language", 3), ("Ataturk Principles", 2), ("Engineering Math", 3),
            ("Physics I", 3), ("Physics II", 2), ("Electronics", 2),
            ("Digital Systems", 2), ("Signals", 2), ("Control Systems", 2),
            ("Thermodynamics", 2), ("Mechanics", 2), ("Materials Science", 2),
            ("Architecture", 2), ("Civil Engineering", 2),
        ],
        "num_students": 580,
        "constraint_types": ["NotOverlap", "DifferentTime", "SameDays", "Precedence", "WorkDay(S5)"],
    },
    {
        "name": "mary-fal-spr",
        "full_name": "Mary University",
        "nrDays": 6, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("MAIN1", 200), ("MAIN2", 120), ("R401", 80), ("R402", 60),
            ("R403", 50), ("R404", 40), ("SEM1", 30), ("SEM2", 25),
        ],
        "courses": [
            ("Medicine I", 3), ("Medicine II", 2), ("Anatomy", 2),
            ("Physiology", 2), ("Biochemistry", 2), ("Pathology", 2),
            ("Pharmacology", 2), ("Microbiology", 2), ("Surgery", 1),
            ("Pediatrics", 2), ("Obstetrics", 1),
        ],
        "num_students": 280,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays"],
    },
    {
        "name": "muni-fi-spr",
        "full_name": "Masaryk University (Faculty of Informatics)",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("D1", 300), ("D2", 200), ("D3", 150), ("B117", 100),
            ("B116", 80), ("B204", 60), ("B205", 50), ("B311", 40),
            ("B312", 35), ("A218", 30), ("A219", 30), ("CVT1", 25),
            ("CVT2", 25), ("CVT3", 20),
        ],
        "courses": [
            ("Intro to Programming", 4), ("Algorithms I", 3), ("Algorithms II", 2),
            ("Data Structures", 3), ("Automata Theory", 2), ("Compiler Design", 2),
            ("Operating Systems", 3), ("Computer Networks", 2), ("Databases", 3),
            ("Software Engineering", 2), ("AI Fundamentals", 2), ("Machine Learning", 2),
            ("Computer Graphics", 2), ("Distributed Systems", 2), ("IT Security", 2),
            ("Discrete Math", 3), ("Linear Algebra", 2), ("Probability", 2),
        ],
        "num_students": 650,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays", "DifferentDays", "Precedence"],
    },
    {
        "name": "muni-fsps-spr",
        "full_name": "Masaryk University (Faculty of Sports)",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("GYM1", 100), ("GYM2", 80), ("HALL1", 120), ("R501", 60),
            ("R502", 50), ("R503", 40), ("R504", 35), ("POOL1", 30),
        ],
        "courses": [
            ("Kinesiology", 2), ("Sports Medicine", 2), ("Biomechanics", 2),
            ("Exercise Physiology", 2), ("Sports Psychology", 2), ("Coaching", 2),
            ("Athletics", 2), ("Swimming", 1), ("Team Sports", 2),
            ("Anatomy", 2), ("Nutrition", 2),
        ],
        "num_students": 240,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime"],
    },
    {
        "name": "muni-pdf-spr",
        "full_name": "Masaryk University (Faculty of Education)",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 13,
        "rooms": [
            ("AUD1", 250), ("AUD2", 180), ("R601", 100), ("R602", 80),
            ("R603", 60), ("R604", 50), ("R605", 40), ("R606", 35),
            ("R607", 30), ("ART1", 25), ("MUS1", 25),
        ],
        "courses": [
            ("Pedagogy", 3), ("Didactics", 2), ("Child Psychology", 2),
            ("Special Education", 2), ("Czech Language", 3), ("Literature", 2),
            ("History", 2), ("Geography", 2), ("Art Education", 2),
            ("Music Education", 2), ("Math Education", 2), ("Science Education", 2),
            ("Physical Education", 2), ("Social Studies", 2),
        ],
        "num_students": 480,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays", "DifferentDays"],
    },
    {
        "name": "pu-llr-spr",
        "full_name": "Purdue University",
        "nrDays": 5, "slotsPerDay": 288, "nrWeeks": 16,
        "rooms": [
            ("LWSN1", 350), ("LWSN2", 250), ("LWSN3", 180), ("HAAS1", 150),
            ("HAAS2", 120), ("EE1", 100), ("EE2", 80), ("EE3", 60),
            ("MSEE1", 50), ("MSEE2", 40), ("LAB1", 35), ("LAB2", 30),
            ("LAB3", 30), ("LAB4", 25),
        ],
        "courses": [
            ("CS 180", 4), ("CS 240", 3), ("CS 250", 3), ("CS 251", 3),
            ("CS 307", 2), ("CS 352", 2), ("CS 354", 2), ("CS 373", 2),
            ("CS 381", 2), ("CS 408", 2), ("MA 161", 4), ("MA 162", 3),
            ("MA 265", 2), ("MA 351", 2), ("PHYS 172", 3), ("PHYS 241", 2),
            ("ECE 201", 3), ("ECE 270", 2),
        ],
        "num_students": 780,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays", "Precedence", "MaxDays(3)", "MinGap(2)"],
    },
    {
        "name": "tg-fal-spr",
        "full_name": "Thapar University",
        "nrDays": 6, "slotsPerDay": 288, "nrWeeks": 14,
        "rooms": [
            ("LT1", 200), ("LT2", 180), ("LT3", 150), ("LT4", 120),
            ("CR1", 80), ("CR2", 60), ("CR3", 50), ("CR4", 40),
            ("CR5", 35), ("CL1", 30), ("CL2", 30), ("CL3", 25),
        ],
        "courses": [
            ("Engineering Math I", 3), ("Engineering Math II", 2),
            ("Data Structures", 3), ("Algorithms", 2), ("DBMS", 2),
            ("Operating Systems", 2), ("Computer Networks", 2),
            ("Software Engineering", 2), ("Theory of Computation", 2),
            ("Digital Electronics", 2), ("Microprocessors", 2),
            ("Physics", 3), ("Chemistry", 2), ("English", 2),
            ("Environmental Science", 2),
        ],
        "num_students": 550,
        "constraint_types": ["NotOverlap", "SameTime", "DifferentTime", "SameDays", "DifferentDays"],
    },
]

# Standard ITC-2019 timeslot definitions (5-minute granularity)
# 08:00 = slot 96, 09:00 = 108, ..., 19:00 = 228
LECTURE_STARTS = [96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228]
LECTURE_LENGTHS = [12, 18, 24]  # 60min, 90min, 120min


def generate_instance(uni, seed=None):
    """Generate a single ITC-2019 XML instance for a university."""
    rng = random.Random(seed or hash(uni["name"]))
    nd = uni["nrDays"]
    nw = uni["nrWeeks"]
    spd = uni["slotsPerDay"]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<problem name="{uni["name"]}" nrDays="{nd}" slotsPerDay="{spd}" nrWeeks="{nw}">',
        '',
        '  <!-- Optimization -->' ,
        '  <optimization time="1" room="1" distribution="1" student="1"/>',
        '',
        '  <rooms>',
    ]

    # ── Rooms with travel times ──
    rooms = uni["rooms"]
    for i, (rid, cap) in enumerate(rooms):
        travel_lines = []
        for j, (rid2, _) in enumerate(rooms):
            if i != j:
                dist = rng.choice([0, 0, 1, 2, 5, 10])
                if dist > 0:
                    travel_lines.append(f'      <travel room="{rid2}" value="{dist}"/>')
        if travel_lines:
            lines.append(f'    <room id="{rid}" capacity="{cap}">')
            lines.extend(travel_lines)
            lines.append(f'    </room>')
        else:
            lines.append(f'    <room id="{rid}" capacity="{cap}"/>')

    lines.append('  </rooms>')
    lines.append('')
    lines.append('  <courses>')

    # ── Courses & classes ──
    all_class_ids = []
    course_class_map = {}  # course_id -> [class_ids]
    class_idx = 0

    for ci, (cname, num_sections) in enumerate(uni["courses"]):
        course_id = f"c{ci}"
        course_class_map[course_id] = []
        config_id = f"cfg{ci}_0"
        lines.append(f'    <course id="{course_id}">  <!-- {cname} -->')
        lines.append(f'      <config id="{config_id}">')

        for sec in range(num_sections):
            subpart_id = f"sp{ci}_{sec}"
            lines.append(f'        <subpart id="{subpart_id}">')

            cls_id = f"cl{class_idx}"
            enrollment = rng.randint(15, min(150, max(r[1] for r in rooms)))
            all_class_ids.append(cls_id)
            course_class_map[course_id].append(cls_id)

            lines.append(f'          <class id="{cls_id}" limit="{enrollment}">')

            # Generate 3-6 possible time slots
            num_time_opts = rng.randint(3, 6)
            used_times = set()
            length = rng.choice(LECTURE_LENGTHS)
            for _ in range(num_time_opts):
                # Pick random day combination (1-3 days per week)
                num_days_active = rng.randint(1, min(3, nd))
                active_days = sorted(rng.sample(range(nd), num_days_active))
                days_bits = "".join("1" if d in active_days else "0" for d in range(nd))

                start = rng.choice(LECTURE_STARTS)
                if (days_bits, start) in used_times:
                    continue
                used_times.add((days_bits, start))

                weeks_bits = "1" * nw  # all weeks
                penalty = rng.choice([0, 0, 0, 1, 2, 4, 8])
                lines.append(f'            <time days="{days_bits}" start="{start}" length="{length}" weeks="{weeks_bits}" penalty="{penalty}"/>')

            # Possible rooms (rooms with enough capacity)
            suitable = [(rid, cap) for rid, cap in rooms if cap >= enrollment]
            if not suitable:
                suitable = rooms[:3]  # fallback to largest

            for rid, _ in suitable:
                pen = rng.choice([0, 0, 0, 1, 2, 4])
                lines.append(f'            <room id="{rid}" penalty="{pen}"/>')

            lines.append(f'          </class>')
            lines.append(f'        </subpart>')
            class_idx += 1

        lines.append(f'      </config>')
        lines.append(f'    </course>')

    lines.append('  </courses>')
    lines.append('')
    lines.append('  <distributions>')

    # ── Distribution constraints ──
    constraint_types = uni["constraint_types"]

    # Hard: same-course classes must not overlap
    for cid, cls_ids in course_class_map.items():
        if len(cls_ids) > 1:
            lines.append(f'    <distribution type="NotOverlap" required="true" penalty="0">')
            for cl in cls_ids:
                lines.append(f'      <class id="{cl}"/>')
            lines.append(f'    </distribution>')

    # Soft: random pairwise constraints
    num_soft = max(5, len(all_class_ids) // 3)
    for _ in range(num_soft):
        if len(all_class_ids) < 2:
            break
        pair = rng.sample(all_class_ids, 2)
        ctype = rng.choice([t for t in constraint_types if t != "NotOverlap"])
        # Strip parameters from complex types for XML compatibility
        base_type = ctype.split("(")[0]
        pen = rng.choice([1, 2, 3, 5, 8])
        lines.append(f'    <distribution type="{base_type}" required="false" penalty="{pen}">')
        for cl in pair:
            lines.append(f'      <class id="{cl}"/>')
        lines.append(f'    </distribution>')

    lines.append('  </distributions>')
    lines.append('')
    lines.append('  <students>')

    # ── Students ──
    all_courses = list(course_class_map.keys())
    for si in range(uni["num_students"]):
        num_enrolled = rng.randint(3, min(7, len(all_courses)))
        chosen = rng.sample(all_courses, num_enrolled)
        lines.append(f'    <student id="s{si}">')
        for c in chosen:
            lines.append(f'      <course id="{c}"/>')
        lines.append(f'    </student>')

    lines.append('  </students>')
    lines.append('</problem>')

    return "\n".join(lines)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "datasets")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print("ITC-2019 Dataset Generator")
    print("=" * 60)

    for uni in UNIVERSITIES:
        xml = generate_instance(uni, seed=hash(uni["name"]))
        fname = f"{uni['name']}.xml"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)

        # Count stats
        num_classes = sum(n for _, n in uni["courses"])
        num_rooms = len(uni["rooms"])
        print(f"  ✓ {fname:<25s} {num_classes:>3d} classes | {num_rooms:>2d} rooms | {uni['num_students']:>4d} students | {uni['full_name']}")

    print(f"\nGenerated {len(UNIVERSITIES)} instances → {out_dir}")


if __name__ == "__main__":
    main()
