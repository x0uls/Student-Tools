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
        
        # Top row with back button and title
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

        # Course name
        ctk.CTkLabel(form_frame, text="Course Name:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=0, column=0, sticky="w", pady=3)
        self.subject_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.subject_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Credit hours
        ctk.CTkLabel(form_frame, text="Credit Hours:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=1, column=0, sticky="w", pady=3)
        self.credit_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.credit_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=3)
        
        # Bind validation to credit entry
        self.credit_entry.bind("<KeyPress>", self.handle_credit_input)

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

        # Add Course button
        add_btn = ctk.CTkButton(
            form_frame, 
            text="Add Course", 
            command=self.add_subject, 
            height=32,
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        add_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Course list - scrollable frame for content
        self.subject_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.subject_list_frame.pack(fill="both", expand=True, padx=15, pady=(10, 20))

        # Preload existing subjects
        if existing_subjects:
            for subj in existing_subjects:
                self._add_subject_row(subj["name"], subj["credit"], subj["grade"])
            self._update_gpa(update_main_page=False)

    # ----------------------
    # SUBJECT MANAGEMENT
    # ----------------------

    def add_subject(self):
        """Add a new subject from the form."""
        name = self.subject_entry.get().strip()
        credit = self.credit_entry.get().strip()
        grade = self.grade_option.get().strip()

        # Simple validation
        if not name or not credit:
            self.show_error("Please fill in all fields")
            return

        try:
            credit = float(credit)
            if credit <= 0:
                self.show_error("Only numbers greater than 0 are allowed")
                return
        except ValueError:
            self.show_error("Invalid credit value")
            return

        # Add the row and clear form
        self._add_subject_row(name, credit, grade)
        self.subject_entry.delete(0, "end")
        self.credit_entry.delete(0, "end")
        self.grade_option.set("A")
        self._update_gpa()


    def handle_credit_input(self, event, credit_entry=None):
        """Unified credit input handler with auto-decimal formatting."""
        # Allow navigation keys
        if event.keysym in ['BackSpace', 'Delete', 'Tab', 'Return', 'Left', 'Right', 'Up', 'Down']:
            return
        
        # Handle digit input
        if event.char and event.char.isdigit():
            if event.char == '0':
                self.show_error("Only numbers greater than 0 are allowed")
                return "break"
            
            # Use provided entry or default to main entry
            entry = credit_entry or self.credit_entry
            current_value = entry.get()
            
            # Block character and format manually
            self.after(1, lambda: self._format_credit_entry(entry, event.char))
            return "break"
        
        # Block invalid characters
        if event.char:
            self.show_error("Only numbers allowed!" if event.char.isalpha() else "No special characters allowed!")
        return "break"

    def _format_credit_entry(self, entry, digit):
        """Format credit entry with .0 decimal."""
        entry.delete(0, "end")
        entry.insert(0, f"{digit}.0")
        self.hide_message()
        
        # Update GPA if this is a row entry
        if entry != self.credit_entry:
            self._update_gpa()

    def _add_subject_row(self, name, credit, grade):
        # Create row container
        row_container = ctk.CTkFrame(self.subject_list_frame, height=42, corner_radius=6)
        row_container.pack(fill="x", pady=2, padx=3)
        row_container.pack_propagate(False)

        # Course name (flexible, biggest space)
        name_entry = ctk.CTkEntry(
            row_container,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        name_entry.insert(0, str(name) if name is not None else "")
        name_entry.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=6)

        # Credit hours (compact, fits 3.0 etc.)
        credit_entry = ctk.CTkEntry(
            row_container,
            width=45,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        credit_entry.insert(0, str(credit) if credit is not None else "")
        credit_entry.pack(side="left", padx=(0, 4), pady=6)
        
        # Bind validation to row credit entry
        credit_entry.bind("<KeyPress>", lambda e: self.handle_credit_input(e, credit_entry))

        # Grade dropdown (compact but readable)
        grade_option = ctk.CTkOptionMenu(
            row_container,
            values=list(GRADE_POINTS.keys()),
            width=55,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        grade_option.set(grade if grade is not None else "A")
        grade_option.pack(side="left", padx=(0, 4), pady=6)

        # Remove button ("×" instead of 🗑️)
        del_btn = ctk.CTkButton(
            row_container,
            text="×",
            width=18,
            height=28,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=6,
            border_width=0,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda r=row_container: self.remove_subject(r),
        )
        del_btn.pack(side="right", padx=(0, 6), pady=6)

        self.subjects.append(
            {
                "name_entry": name_entry,
                "credit_entry": credit_entry,
                "grade_option": grade_option,
                "row_frame": row_container,
            }
        )

        # Update GPA on change (only for grade dropdown, not on every keystroke)
        grade_option.configure(command=lambda _: self._update_gpa())

    def remove_subject(self, row_container):
        """Remove a subject row."""
        for subj in self.subjects:
            if subj["row_frame"] == row_container:
                self.subjects.remove(subj)
                break
        row_container.destroy()
        self._update_gpa()

    # ----------------------
    # GPA CALCULATION
    # ----------------------

    def _update_gpa(self, update_main_page=True):
        """Recalculate GPA from all rows."""
        subjects_data = self.get_subjects_data()
        gpa = self._calculate_gpa(subjects_data)
        self.gpa_label.configure(text=f"GPA: {gpa:.2f}")

        # Update main page if exists and requested
        if self.main_page and update_main_page:
            self.main_page.update_semester_subjects(self.semester_name, subjects_data)

    def _calculate_gpa(self, subjects_data):
        """Calculate GPA from subjects data."""
        if not subjects_data:
            return 0.0
        total_points = sum(GRADE_POINTS[s["grade"]] * s["credit"] for s in subjects_data)
        total_credits = sum(s["credit"] for s in subjects_data)
        return total_points / total_credits if total_credits > 0 else 0.0

    def get_subjects_data(self):
        """Return subjects as plain dicts for storing in main page."""
        subjects_data = []
        for subj in self.subjects:
            try:
                subjects_data.append({
                    "name": subj["name_entry"].get(),
                    "credit": float(subj["credit_entry"].get()),
                    "grade": subj["grade_option"].get(),
                })
            except ValueError:
                continue
        return subjects_data

    def show_error(self, text, duration=3000):
        """Show error message with simple animation."""
        # Cancel existing timer and hide current message
        if hasattr(self, 'message_timer'):
            self.after_cancel(self.message_timer)
        self.hide_message()
        
        # Create and show message
        self.current_message = ctk.CTkLabel(
            self, text=text, text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#ff4757", corner_radius=15, padx=20, pady=8
        )
        self.current_message.place(relx=0.5, rely=0.95, anchor="s")
        
        # Auto-hide
        self.message_timer = self.after(duration, self.hide_message)
    
    def hide_message(self):
        """Hide current message."""
        if hasattr(self, 'message_timer'):
            self.after_cancel(self.message_timer)
            delattr(self, 'message_timer')
        if hasattr(self, 'current_message') and self.current_message:
            self.current_message.destroy()
            self.current_message = None
