import customtkinter as ctk
import openpyxl
import os
from .semester_detail_page import SemesterDetailPage, GRADE_POINTS
from .chart import GPAChartPage


class GPACalculatorPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Header
        ctk.CTkLabel(
            self, text="GPA Calculator", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Total CGPA display
        self.cgpa_label = ctk.CTkLabel(
            self, text="Total CGPA: 0.00", font=ctk.CTkFont(size=14)
        )
        self.cgpa_label.pack(pady=5)

        # Semester cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Inner frame for the semester cards
        self.semester_frame = ctk.CTkFrame(self.scrollable_frame)
        self.semester_frame.pack(fill="both", expand=True)

        # Keep track of semesters
        self.semesters = []

        # Add Semester Button
        self.add_sem_btn = ctk.CTkButton(
            self,
            text="Add Semester",
            font=ctk.CTkFont(size=14),
            command=self.add_semester,
        )
        self.add_sem_btn.pack(pady=10)

        self.chart_link = ctk.CTkLabel(
            self,
            text="📈 View GPA Chart",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="blue",
            cursor="hand2",
        )
        self.chart_link.pack(pady=5)

        self.chart_link.bind("<Button-1>", lambda e: self.open_chart_page())

        self.load_from_excel()

    def add_semester(self):
        sem_number = len(self.semesters) + 1
        sem_name = f"Semester {sem_number}"

        sem_data = {
            "name": sem_name,
            "gpa": 0.0,
            "subjects": [],
            "detail_page": None,
            "card": None,
            "gpa_label": None,
        }
        self.semesters.append(sem_data)
        self._create_semester_card(sem_data)
        self._update_total_cgpa()

    def _create_semester_card(self, sem):
        card = ctk.CTkFrame(self.semester_frame, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        sem["card"] = card

        # Horizontal container inside the card
        container = ctk.CTkFrame(card)
        container.pack(fill="x", padx=5, pady=5)

        # Left side: name + GPA labels
        left_frame = ctk.CTkFrame(container)
        left_frame.pack(side="left", fill="x", expand=True)

        # Inside _create_semester_card:
        name_label = ctk.CTkLabel(
            left_frame, text=sem["name"], font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w")
        sem["name_label"] = name_label  # store reference

        gpa_label = ctk.CTkLabel(
            left_frame, text=f"GPA: {sem['gpa']:.2f}", font=ctk.CTkFont(size=12)
        )
        gpa_label.pack(anchor="w")
        sem["gpa_label"] = gpa_label

        remove_btn = ctk.CTkButton(
            card,
            text="X",
            width=25,
            height=25,
            fg_color="red",
            hover_color="darkred",
            corner_radius=12,
            border_width=0,
            text_color="white",
            command=lambda s=sem: self.remove_semester(s),
        )

        remove_btn.place(relx=0.98, rely=0.5, x=-5, y=0, anchor="e")

        # Bind click to open semester
        def on_click(event, s=sem):
            self.open_semester(s)

        for widget in [card, left_frame, name_label, gpa_label]:
            widget.bind("<Button-1>", on_click)

    def remove_semester(self, sem):
        """Remove semester card and data."""
        # Destroy the card
        if sem["card"]:
            sem["card"].destroy()
        # Destroy detail page if it exists
        if sem["detail_page"]:
            sem["detail_page"].destroy()
        # Remove from list
        self.semesters.remove(sem)
        # Update total CGPA
        self._update_total_cgpa()
        # Re-number remaining semesters
        for i, s in enumerate(self.semesters, start=1):
            s["name"] = f"Semester {i}"
            if s.get("name_label"):
                s["name_label"].configure(text=s["name"])

    def open_semester(self, sem):
        if sem["detail_page"] is None:
            sem["detail_page"] = SemesterDetailPage(
                self.parent,
                sem["name"],
                lambda dp=None: self.close_semester(sem),
                main_page=self,
                existing_subjects=sem["subjects"],
            )
            sem["detail_page"].place(relwidth=1, relheight=1)
        else:
            sem["detail_page"].place(relwidth=1, relheight=1)

        sem["detail_page"].lift()

    def update_semester_subjects(self, semester_name, subjects):
        sem = next(s for s in self.semesters if s["name"] == semester_name)
        sem["subjects"] = subjects

        # Update GPA
        total_points = sum(GRADE_POINTS[s["grade"]] * s["credit"] for s in subjects)
        total_credits = sum(s["credit"] for s in subjects)
        sem["gpa"] = total_points / total_credits if total_credits else 0.0

        # Update GPA label
        if sem["gpa_label"]:
            sem["gpa_label"].configure(text=f"GPA: {sem['gpa']:.2f}")

        self._update_total_cgpa()
        self.save_to_excel()

    def _update_total_cgpa(self):
        """Calculate CGPA from all semesters."""
        total_points = 0
        total_credits = 0
        for sem in self.semesters:
            for subj in sem["subjects"]:
                total_points += GRADE_POINTS[subj["grade"]] * subj["credit"]
                total_credits += subj["credit"]
        cgpa = total_points / total_credits if total_credits else 0.0
        self.cgpa_label.configure(text=f"Total CGPA: {cgpa:.2f}")
        self.save_to_excel()

    def show_main_page(self):
        self.place(relwidth=1, relheight=1)

    def close_semester(self, sem):
        if sem["detail_page"]:
            sem["detail_page"].place_forget()
        self.show_main_page()

    def open_chart_page(self):
        if not hasattr(self, "chart_page") or self.chart_page is None:
            self.chart_page = GPAChartPage(
                self.parent, self.semesters, go_back_callback=self.show_main_page
            )
            self.chart_page.place(relwidth=1, relheight=1)
        else:
            self.chart_page.draw_chart()
            self.chart_page.place(relwidth=1, relheight=1)

        self.chart_page.lift()

    def save_to_excel(self, filename="gpa_data.xlsx"):
        """Save all semester/subject data into an Excel file."""
        folder = os.path.join(os.path.dirname(__file__))
        os.makedirs(folder, exist_ok=True)  # create folder if it doesn't exist
        file_path = os.path.join(folder, filename)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "GPA Data"

        # Header row
        ws.append(["Semester", "Subject", "Credit", "Grade", "GPA"])

        for sem in self.semesters:
            for subj in sem["subjects"]:
                ws.append(
                    [
                        sem["name"],
                        subj["name"],
                        subj["credit"],
                        subj["grade"],
                        f"{sem['gpa']:.2f}",
                    ]
                )

        # Save workbook
        wb.save(file_path)
        print(f"Data saved automatically to {os.path.abspath(file_path)}")

    def load_from_excel(self, filename="gpa_data.xlsx"):
        folder = os.path.dirname(__file__)
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            return

        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        data_rows = list(ws.iter_rows(values_only=True))[1:]  # skip header

        semesters_dict = {}
        for sem_name, subj_name, credit, grade, gpa in data_rows:
            if sem_name not in semesters_dict:
                semesters_dict[sem_name] = {
                    "name": sem_name,
                    "gpa": 0.0,
                    "subjects": [],
                    "detail_page": None,
                    "card": None,
                    "gpa_label": None,
                }
            semesters_dict[sem_name]["subjects"].append(
                {
                    "name": subj_name,
                    "credit": float(credit),
                    "grade": grade,
                }
            )

        # Clear and rebuild
        self.semesters.clear()
        for sem in semesters_dict.values():
            total_points = sum(
                GRADE_POINTS[s["grade"]] * s["credit"] for s in sem["subjects"]
            )
            total_credits = sum(s["credit"] for s in sem["subjects"])
            sem["gpa"] = total_points / total_credits if total_credits else 0.0

            self.semesters.append(sem)
            self._create_semester_card(sem)

        self._update_total_cgpa()
        print(f"Data loaded from {os.path.abspath(file_path)}")
