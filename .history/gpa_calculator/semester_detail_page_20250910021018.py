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

        # --- Header ---
        header_frame = ctk.CTkFrame(self, corner_radius=15)
        header_frame.pack(fill="x", pady=(20, 15), padx=20)
        
        # Header content container
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        # Semester name
        title_label = ctk.CTkLabel(
            header_content, 
            text=semester_name, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        # GPA display
        self.gpa_label = ctk.CTkLabel(
            header_content, 
            text="GPA: 0.00", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1a73e8"
        )
        self.gpa_label.pack(side="right")

        # --- Subject Form ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10, padx=10)

        # Labels and entries
        ctk.CTkLabel(form_frame, text="Subject Name:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.subject_entry = ctk.CTkEntry(form_frame, width=150)
        self.subject_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Credit Hours:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.credit_entry = ctk.CTkEntry(form_frame, width=150)
        self.credit_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Grade:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.grade_option = ctk.CTkOptionMenu(
            form_frame, values=list(GRADE_POINTS.keys())
        )
        self.grade_option.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.grade_option.set("A")

        # Center Add Subject button
        add_btn = ctk.CTkButton(
            form_frame, text="Add Subject", command=self.add_subject, width=150
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Make sure both columns expand evenly so button stays centered
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Scrollable Subject List ---
        self.subject_list_frame = ctk.CTkScrollableFrame(
            self, label_text="Subjects Added"
        )
        self.subject_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Preload existing subjects
        if existing_subjects:
            for subj in existing_subjects:
                self._add_subject_row(subj["name"], subj["credit"], subj["grade"])
            self._update_gpa()

        # --- Back Button ---
        back_btn = ctk.CTkButton(self, text="Back", command=self.go_back_callback)
        back_btn.pack(pady=10)

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
        row = ctk.CTkFrame(self.subject_list_frame, height=35)
        row.pack(fill="x", pady=2, padx=5)

        # Name entry slightly smaller so delete button fits
        name_entry = ctk.CTkEntry(row, width=130)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=(5, 2), pady=2)

        credit_entry = ctk.CTkEntry(row, width=50)
        credit_entry.insert(0, str(credit))
        credit_entry.pack(side="left", padx=(2, 2), pady=2)

        grade_option = ctk.CTkOptionMenu(
            row, values=list(GRADE_POINTS.keys()), width=70
        )
        grade_option.set(grade)
        grade_option.pack(side="left", padx=(2, 2), pady=2)

        del_btn = ctk.CTkButton(
            row,
            text="X",
            width=30,
            height=25,
            fg_color="red",
            hover_color="#ff6666",
            command=lambda r=row: self.remove_subject(r),
        )
        del_btn.pack(side="right", padx=(2, 5), pady=2)

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
