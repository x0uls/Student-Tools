import customtkinter as ctk

# TARUMT Grade → Point mapping
GRADE_POINTS = {
    "A+": 4.00,
    "A": 4.00,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.00,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.00,
    "F": 0.00,
}


class SemesterDetailPage(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        semester_name,
        go_back_callback,
        main_page=None,
        existing_subjects=None,
    ):
        super().__init__(parent)
        self.semester_name = semester_name
        self.go_back_callback = go_back_callback
        self.main_page = main_page
        self.subjects = []  # list of dicts storing widget references

        # Configure main frame
        self.configure(fg_color="transparent")
        
        # --- Header --- Clean and minimal
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(30, 20), padx=30)
        
        # Header content container
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x")
        
        # Semester name - clean typography
        title_label = ctk.CTkLabel(
            header_content, 
            text=semester_name, 
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1e293b"
        )
        title_label.pack(side="left")
        
        # GPA display - subtle container
        gpa_container = ctk.CTkFrame(header_content, fg_color="#f1f5f9", corner_radius=10)
        gpa_container.pack(side="right")
        
        self.gpa_label = ctk.CTkLabel(
            gpa_container, 
            text="GPA: 0.00", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a"
        )
        self.gpa_label.pack(pady=12, padx=16)

        # --- Subject Form --- Clean and organized
        form_frame = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=12)
        form_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        # Form title - minimal
        form_title = ctk.CTkLabel(
            form_frame, 
            text="Add Subject", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1e293b"
        )
        form_title.pack(pady=(20, 15))

        # Form content container
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="x", padx=25, pady=(0, 20))

        # Subject name row
        name_row = ctk.CTkFrame(form_content, fg_color="transparent")
        name_row.pack(fill="x", pady=8)
        
        ctk.CTkLabel(name_row, text="Subject Name:", font=ctk.CTkFont(size=14), text_color="#374151").pack(side="left")
        self.subject_entry = ctk.CTkEntry(name_row, width=200, height=32, corner_radius=8)
        self.subject_entry.pack(side="right")

        # Credit hours row
        credit_row = ctk.CTkFrame(form_content, fg_color="transparent")
        credit_row.pack(fill="x", pady=8)
        
        ctk.CTkLabel(credit_row, text="Credit Hours:", font=ctk.CTkFont(size=14), text_color="#374151").pack(side="left")
        self.credit_entry = ctk.CTkEntry(credit_row, width=200, height=32, corner_radius=8)
        self.credit_entry.pack(side="right")

        # Grade row
        grade_row = ctk.CTkFrame(form_content, fg_color="transparent")
        grade_row.pack(fill="x", pady=8)
        
        ctk.CTkLabel(grade_row, text="Grade:", font=ctk.CTkFont(size=14), text_color="#374151").pack(side="left")
        self.grade_option = ctk.CTkOptionMenu(
            grade_row, 
            values=list(GRADE_POINTS.keys()),
            width=200,
            height=32,
            corner_radius=8
        )
        self.grade_option.pack(side="right")
        self.grade_option.set("A")

        # Add Subject button - clean and prominent
        add_btn = ctk.CTkButton(
            form_content, 
            text="Add Subject", 
            command=self.add_subject, 
            width=180,
            height=36,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=18,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white"
        )
        add_btn.pack(pady=(20, 0))

        # --- Scrollable Subject List --- Clean and minimal
        self.subject_list_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent"
        )
        self.subject_list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Preload existing subjects
        if existing_subjects:
            for subj in existing_subjects:
                self._add_subject_row(subj["name"], subj["credit"], subj["grade"])
            self._update_gpa()

        # --- Back Button --- Clean and minimal
        back_btn = ctk.CTkButton(
            self, 
            text="Back to Semesters", 
            command=self.go_back_callback,
            height=36,
            width=180,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=18,
            fg_color="#6b7280",
            hover_color="#4b5563",
            text_color="white"
        )
        back_btn.pack(pady=(0, 30))

    # ----------------------
    # SUBJECT MANAGEMENT
    # ----------------------

    def add_subject(self):
        """Add a new subject from the form."""
        name = self.subject_entry.get().strip()
        credit = self.credit_entry.get().strip()
        grade = self.grade_option.get().strip()

        # --- Validation ---
        if not name or not credit or not grade:
            self.show_temp_message("Please fill all fields")
            return

        try:
            credit = float(credit)
            if credit <= 0:
                raise ValueError
        except ValueError:
            self.show_temp_message("Credit hours must be a positive number")
            return

        # Add the row
        self._add_subject_row(name, credit, grade)

        # Clear form fields
        self.subject_entry.delete(0, "end")
        self.credit_entry.delete(0, "end")
        self.grade_option.set("A")

        # Update GPA
        self._update_gpa()

    def _add_subject_row(self, name, credit, grade):
        # Clean, minimal row design
        row = ctk.CTkFrame(self.subject_list_frame, height=45, corner_radius=8)
        row.pack(fill="x", pady=4, padx=0)
        row.pack_propagate(False)

        # Content container
        content_frame = ctk.CTkFrame(row, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=8)

        # Subject name entry - clean styling
        name_entry = ctk.CTkEntry(content_frame, width=200, height=28, corner_radius=6)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=(0, 12))

        # Credit hours entry
        credit_entry = ctk.CTkEntry(content_frame, width=70, height=28, corner_radius=6)
        credit_entry.insert(0, str(credit))
        credit_entry.pack(side="left", padx=(0, 12))

        # Grade dropdown
        grade_option = ctk.CTkOptionMenu(
            content_frame, 
            values=list(GRADE_POINTS.keys()), 
            width=90,
            height=28,
            corner_radius=6
        )
        grade_option.set(grade)
        grade_option.pack(side="left", padx=(0, 12))

        # Delete button - minimal and clean
        del_btn = ctk.CTkButton(
            content_frame,
            text="×",
            width=24,
            height=24,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=12,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda r=row: self.remove_subject(r),
        )
        del_btn.pack(side="right")

        self.subjects.append(
            {
                "name_entry": name_entry,
                "credit_entry": credit_entry,
                "grade_option": grade_option,
                "row_frame": row,
            }
        )

        # Update GPA on change
        name_entry.bind("<KeyRelease>", lambda e: self._update_gpa())
        credit_entry.bind("<KeyRelease>", lambda e: self._update_gpa())
        grade_option.configure(command=lambda _: self._update_gpa())

    def remove_subject(self, row_frame):
        """Remove a subject row."""
        for subj in self.subjects:
            if subj["row_frame"] == row_frame:
                self.subjects.remove(subj)
                break
        row_frame.destroy()
        self._update_gpa()

    # ----------------------
    # GPA CALCULATION
    # ----------------------

    def _update_gpa(self):
        """Recalculate GPA from all rows."""
        total_points = 0
        total_credits = 0

        for subj in self.subjects:
            try:
                credit = float(subj["credit_entry"].get())
                grade = subj["grade_option"].get()
                points = GRADE_POINTS.get(grade, 0.0)
                total_points += points * credit
                total_credits += credit
            except ValueError:
                continue

        gpa = total_points / total_credits if total_credits > 0 else 0.0
        self.gpa_label.configure(text=f"GPA: {gpa:.2f}")

        # Update main page if exists
        if self.main_page:
            self.main_page.update_semester_subjects(
                self.semester_name, self.get_subjects_data()
            )

    def get_subjects_data(self):
        """Return subjects as plain dicts for storing in main page."""
        subjects_data = []
        for subj in self.subjects:
            try:
                subjects_data.append(
                    {
                        "name": subj["name_entry"].get(),
                        "credit": float(subj["credit_entry"].get()),
                        "grade": subj["grade_option"].get(),
                    }
                )
            except ValueError:
                continue
        return subjects_data

    def show_temp_message(self, text, duration=2000):
        """Show a toast-like message inside the same window."""

        msg_label = ctk.CTkLabel(
            self,
            text=text,
            text_color="white",
            font=("Helvetica", 13, "bold"),
            fg_color="#ff4d4d",
            corner_radius=20,
            padx=15,
            pady=10,
        )
        msg_label.place(relx=0.5, rely=1.05, anchor="s")  # start slightly below

        def slide_in(y=1.05):
            if y > 0.9:  # stop at 0.95 (bottom)
                msg_label.place(relx=0.5, rely=y, anchor="s")
                msg_label.after(15, lambda: slide_in(y - 0.01))

        def slide_out(y=0.95):
            if y < 1.2:  # move down then destroy
                msg_label.place(relx=0.5, rely=y, anchor="s")
                msg_label.after(15, lambda: slide_out(y + 0.01))
            else:
                msg_label.destroy()

        slide_in()
        msg_label.after(duration, lambda: slide_out())
