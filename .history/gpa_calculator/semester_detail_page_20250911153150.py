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

        # Course name
        ctk.CTkLabel(form_frame, text="Course Name:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=0, column=0, sticky="w", pady=3)
        self.subject_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.subject_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=3)

        # Credit hours
        ctk.CTkLabel(form_frame, text="Credit Hours:", font=ctk.CTkFont(size=12), text_color="#d1d5db").grid(row=1, column=0, sticky="w", pady=3)
        self.credit_entry = ctk.CTkEntry(form_frame, height=30, corner_radius=6)
        self.credit_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=3)
        
        # Bind validation to credit entry
        self.credit_entry.bind("<KeyRelease>", self.validate_credit_input)
        self.credit_entry.bind("<KeyPress>", self.on_credit_key_press)

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

        # No header - saves space in 360px window

        # Course list - scrollable frame for content
        self.subject_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.subject_list_frame.pack(fill="both", expand=True, padx=15, pady=(10, 20))

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
            self.show_smooth_message("Please fill in all fields")
            return

        try:
            credit = float(credit)
            if credit <= 0:
                self.show_smooth_message("Only numbers greater than 0 are allowed")
                return
        except ValueError:
            self.show_smooth_message("Only numbers allowed. No special characters allowed.")
            return

        # Add the row
        self._add_subject_row(name, credit, grade)

        # Clear form fields
        self.subject_entry.delete(0, "end")
        self.credit_entry.delete(0, "end")
        self.grade_option.set("A")

        # Update GPA
        self._update_gpa()

    def validate_credit_input(self, event):
        """Validate credit hours input in real-time."""
        value = self.credit_entry.get()
        
        # Allow empty string (user is still typing)
        if not value:
            return
        
        # Check if it's a valid single digit
        if value.isdigit():
            num_value = int(value)
            if num_value <= 0:
                self.show_smooth_message("Only numbers greater than 0 are allowed")
            else:
                self.hide_message()
        elif value.endswith('.0') and value[:-2].isdigit():
            # Handle auto-formatted values like "2.0"
            num_value = int(value[:-2])
            if num_value <= 0:
                self.show_smooth_message("Only numbers greater than 0 are allowed")
            else:
                self.hide_message()
        else:
            self.show_smooth_message("Only single digits allowed")

    def on_credit_key_press(self, event):
        """Prevent invalid characters from being entered in credit field."""
        # Allow backspace, delete, tab, enter, and arrow keys
        if event.keysym in ['BackSpace', 'Delete', 'Tab', 'Return', 'Left', 'Right', 'Up', 'Down']:
            return
        
        # Only allow single digits (no decimal points)
        if event.char and event.char.isdigit():
            # Check if field already has a digit
            if self.credit_entry.get():
                self.show_smooth_message("Only single digits allowed")
                return "break"
            return
        
        # Block all other characters and show appropriate error message
        if event.char:
            if event.char.isalpha():
                self.show_smooth_message("Only numbers allowed", duration=7000)
            else:
                self.show_smooth_message("No special characters allowed", duration=7000)
        return "break"

    def validate_row_credit_input(self, credit_entry):
        """Validate credit hours input in row entries."""
        value = credit_entry.get()
        
        # Allow empty string (user is still typing)
        if not value:
            return
        
        # Check if it's a valid single digit
        if value.isdigit():
            num_value = int(value)
            if num_value <= 0:
                self.show_smooth_message("Only numbers greater than 0 are allowed")
            else:
                self.hide_message()
                # Update GPA when valid input is entered
                self._update_gpa()
        else:
            self.show_smooth_message("Only single digits allowed")

    def on_row_credit_key_press(self, event, credit_entry):
        """Prevent invalid characters from being entered in row credit field."""
        # Allow backspace, delete, tab, enter, and arrow keys
        if event.keysym in ['BackSpace', 'Delete', 'Tab', 'Return', 'Left', 'Right', 'Up', 'Down']:
            return
        
        # Only allow single digits (no decimal points)
        if event.char and event.char.isdigit():
            # Check if field already has a digit
            if credit_entry.get():
                self.show_smooth_message("Only single digits allowed")
                return "break"
            return
        
        # Block all other characters and show appropriate error message
        if event.char:
            if event.char.isalpha():
                self.show_smooth_message("No letters allowed", duration=7000)
            else:
                self.show_smooth_message("No special characters allowed", duration=7000)
        return "break"

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
        credit_entry.bind("<KeyRelease>", lambda e: self.validate_row_credit_input(credit_entry))
        credit_entry.bind("<KeyPress>", lambda e: self.on_row_credit_key_press(e, credit_entry))

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

        # Update GPA on change
        name_entry.bind("<KeyRelease>", lambda e: self._update_gpa())
        credit_entry.bind("<KeyRelease>", lambda e: self._update_gpa())
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

    def show_smooth_message(self, text, duration=5000):
        """Show a smooth, modern message with slide animation."""
        # Cancel any existing message timer
        if hasattr(self, 'message_timer'):
            self.after_cancel(self.message_timer)
        
        # Hide any existing message first
        self.hide_message()
        
        # Create message label
        self.current_message = ctk.CTkLabel(
            self,
            text=text,
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#ff4757",
            corner_radius=15,
            padx=20,
            pady=8,
        )
        
        # Start positioned below the visible area
        self.current_message.place(relx=0.5, rely=1.1, anchor="s")
        
        # Slide in animation
        self.slide_in_message()
        
        # Auto-hide after duration
        self.message_timer = self.after(duration, self.slide_out_message)
    
    def slide_in_message(self):
        """Slide the message in from bottom."""
        if hasattr(self, 'current_message') and self.current_message:
            current_y = float(self.current_message.place_info()['rely'])
            if current_y > 0.95:  # Stop at target position
                new_y = current_y - 0.02
                self.current_message.place(relx=0.5, rely=new_y, anchor="s")
                self.after(10, self.slide_in_message)
    
    def slide_out_message(self):
        """Slide the message out to bottom."""
        if hasattr(self, 'current_message') and self.current_message:
            current_y = float(self.current_message.place_info()['rely'])
            if current_y < 1.2:  # Continue sliding down
                new_y = current_y + 0.02
                self.current_message.place(relx=0.5, rely=new_y, anchor="s")
                self.after(10, self.slide_out_message)
            else:
                # Animation complete, destroy the message
                self.current_message.destroy()
                self.current_message = None
                if hasattr(self, 'message_timer'):
                    delattr(self, 'message_timer')
    
    def hide_message(self):
        """Hide any current message immediately."""
        if hasattr(self, 'message_timer'):
            self.after_cancel(self.message_timer)
            delattr(self, 'message_timer')
        
        if hasattr(self, 'current_message') and self.current_message:
            self.current_message.destroy()
            self.current_message = None
