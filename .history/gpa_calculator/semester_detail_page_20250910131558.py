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

        # Form section
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 15), padx=20)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Subject name
        ctk.CTkLabel(form_frame, text="Subject Name:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=0, column=0, sticky="w", pady=3)
        self.subject_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.subject_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Credit hours
        ctk.CTkLabel(form_frame, text="Credit Hours:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=1, column=0, sticky="w", pady=3)
        self.credit_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.credit_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Grade
        ctk.CTkLabel(form_frame, text="Grade:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=2, column=0, sticky="w", pady=3)
        self.grade_option = ctk.CTkOptionMenu(
            form_frame, 
            values=list(GRADE_POINTS.keys()),
            height=30,
            corner_radius=6
        )
        self.grade_option.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=3)
        self.grade_option.set("A")

        # Add Subject button
        add_btn = ctk.CTkButton(
            form_frame, 
            text="Add Subject", 
            command=self.add_subject, 
            height=32,
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Subjects list header - using exact positioning for perfect alignment
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Create invisible grid for alignment reference
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, minsize=50)
        header_frame.grid_columnconfigure(2, minsize=60)
        header_frame.grid_columnconfigure(3, minsize=35)
        
        # Header labels with exact positioning
        ctk.CTkLabel(header_frame, text="Course Name", font=ctk.CTkFont(size=10, weight="bold"), text_color="#d1d5db").grid(row=0, column=0, sticky="w", padx=(10, 5))
        ctk.CTkLabel(header_frame, text="Credits", font=ctk.CTkFont(size=10, weight="bold"), text_color="#d1d5db").grid(row=0, column=1, sticky="w", padx=(0, 5))
        ctk.CTkLabel(header_frame, text="Grade", font=ctk.CTkFont(size=10, weight="bold"), text_color="#d1d5db").grid(row=0, column=2, sticky="w", padx=(0, 5))
        ctk.CTkLabel(header_frame, text="Action", font=ctk.CTkFont(size=10, weight="bold"), text_color="#d1d5db").grid(row=0, column=3, sticky="e", padx=(0, 10))

        # Subjects list
        self.subject_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.subject_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))

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
        # Clean, minimal row design with grid layout optimized for 360px width
        row = ctk.CTkFrame(self.subject_list_frame, height=35, corner_radius=6)
        row.pack(fill="x", pady=1, padx=0)
        row.pack_propagate(False)
        
        # Configure grid columns to match header exactly
        row.grid_columnconfigure(0, weight=2)  # Course name gets more space
        row.grid_columnconfigure(1, minsize=45)  # Credits - smaller
        row.grid_columnconfigure(2, minsize=55)  # Grade - smaller
        row.grid_columnconfigure(3, minsize=30)  # Action - smaller

        # Subject name entry
        name_entry = ctk.CTkEntry(row, height=22, corner_radius=4, font=ctk.CTkFont(size=11))
        name_entry.insert(0, str(name) if name is not None else "")
        name_entry.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=5)

        # Credit hours entry
        credit_entry = ctk.CTkEntry(row, height=22, corner_radius=4, font=ctk.CTkFont(size=11))
        credit_entry.insert(0, str(credit) if credit is not None else "")
        credit_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=5)

        # Grade dropdown
        grade_option = ctk.CTkOptionMenu(
            row, 
            values=list(GRADE_POINTS.keys()), 
            height=22,
            corner_radius=4,
            font=ctk.CTkFont(size=11)
        )
        grade_option.set(grade if grade is not None else "A")
        grade_option.grid(row=0, column=2, sticky="ew", padx=(0, 4), pady=5)

        # Delete button
        del_btn = ctk.CTkButton(
            row,
            text="×",
            width=22,
            height=22,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=11,
            border_width=0,
            text_color="white",
            font=ctk.CTkFont(size=9, weight="bold"),
            command=lambda r=row: self.remove_subject(r),
        )
        del_btn.grid(row=0, column=3, sticky="e", padx=(0, 8), pady=5)

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
