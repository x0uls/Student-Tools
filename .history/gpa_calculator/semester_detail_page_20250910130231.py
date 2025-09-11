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
        
        # Header section
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        # Back button and title
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        # Back button
        back_btn = ctk.CTkButton(
            top_row,
            text="← Back",
            font=ctk.CTkFont(size=12),
            height=30,
            width=70,
            corner_radius=8,
            command=self.go_back_callback,
        )
        back_btn.pack(side="left")
        
        # Semester title
        title_label = ctk.CTkLabel(
            top_row, 
            text=semester_name, 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="right")
        
        # GPA display
        gpa_frame = ctk.CTkFrame(header_frame, fg_color="#1a2b4c", corner_radius=8)
        gpa_frame.pack(fill="x")
        
        self.gpa_label = ctk.CTkLabel(
            gpa_frame, 
            text="GPA: 0.00", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.gpa_label.pack(pady=10, padx=12)

        # --- Subject Form --- Modern design
        form_frame = ctk.CTkFrame(self, fg_color="#374151", corner_radius=15)
        form_frame.pack(fill="x", pady=(0, 15), padx=20)
        
        # Form title
        form_title = ctk.CTkLabel(
            form_frame, 
            text="➕ Add New Subject", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        form_title.pack(pady=(15, 10))

        # Form content - grid layout
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="x", padx=20, pady=(0, 15))
        form_content.grid_columnconfigure((0, 1), weight=1)

        # Subject name
        ctk.CTkLabel(form_content, text="Subject Name:", font=ctk.CTkFont(size=14), text_color="#d1d5db").grid(row=0, column=0, sticky="w", pady=5)
        self.subject_entry = ctk.CTkEntry(form_content, height=35, corner_radius=8)
        self.subject_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Credit hours
        ctk.CTkLabel(form_content, text="Credit Hours:", font=ctk.CTkFont(size=14), text_color="#d1d5db").grid(row=1, column=0, sticky="w", pady=5)
        self.credit_entry = ctk.CTkEntry(form_content, height=35, corner_radius=8)
        self.credit_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Grade
        ctk.CTkLabel(form_content, text="Grade:", font=ctk.CTkFont(size=14), text_color="#d1d5db").grid(row=2, column=0, sticky="w", pady=5)
        self.grade_option = ctk.CTkOptionMenu(
            form_content, 
            values=list(GRADE_POINTS.keys()),
            height=35,
            corner_radius=8
        )
        self.grade_option.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.grade_option.set("A")

        # Add Subject button
        add_btn = ctk.CTkButton(
            form_content, 
            text="➕ Add Subject", 
            command=self.add_subject, 
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=20,
            fg_color="#059669",
            hover_color="#047857",
            text_color="white"
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=(15, 0))

        # Subjects list section
        subjects_label = ctk.CTkLabel(
            self,
            text="📋 Subjects",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        subjects_label.pack(pady=(10, 5), padx=20, anchor="w")

        # --- Scrollable Subject List --- Modern design
        self.subject_list_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent"
        )
        self.subject_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Preload existing subjects
        if existing_subjects:
            for subj in existing_subjects:
                self._add_subject_row(subj["name"], subj["credit"], subj["grade"])
            self._update_gpa()

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
        # Modern row design
        row = ctk.CTkFrame(self.subject_list_frame, height=50, corner_radius=10)
        row.pack(fill="x", pady=3, padx=0)
        row.pack_propagate(False)

        # Content container
        content_frame = ctk.CTkFrame(row, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Subject name entry
        name_entry = ctk.CTkEntry(content_frame, width=180, height=30, corner_radius=8)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=(0, 10))

        # Credit hours entry
        credit_entry = ctk.CTkEntry(content_frame, width=60, height=30, corner_radius=8)
        credit_entry.insert(0, str(credit))
        credit_entry.pack(side="left", padx=(0, 10))

        # Grade dropdown
        grade_option = ctk.CTkOptionMenu(
            content_frame, 
            values=list(GRADE_POINTS.keys()), 
            width=80,
            height=30,
            corner_radius=8
        )
        grade_option.set(grade)
        grade_option.pack(side="left", padx=(0, 10))

        # Delete button
        del_btn = ctk.CTkButton(
            content_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=15,
            font=ctk.CTkFont(size=12),
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
