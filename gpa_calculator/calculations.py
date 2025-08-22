GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "D": 1.0,
    "F": 0.0,
}


def calculate_gpa(subjects):
    total_points = 0
    total_credits = 0
    for subject, credit, grade in subjects:
        gp = GRADE_POINTS.get(grade.upper(), 0.0)
        total_points += gp * credit
        total_credits += credit
    return round(total_points / total_credits, 2) if total_credits else 0.0


def calculate_cgpa(all_semesters):
    total_points = 0
    total_credits = 0
    for subjects in all_semesters:
        for subject, credit, grade in subjects:
            gp = GRADE_POINTS.get(grade.upper(), 0.0)
            total_points += gp * credit
            total_credits += credit
    return round(total_points / total_credits, 2) if total_credits else 0.0
