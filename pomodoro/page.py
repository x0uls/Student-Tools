import tkinter as tk
import customtkinter as ctk
from .constants import THEME
from .timer_logic import start_timer, reset_timer, pause_timer, resume_timer, is_paused


class PomodoroPage(ctk.CTkFrame):
    def __init__(self, parent):
        self.current_theme = THEME
        super().__init__(parent, width=360, height=640, fg_color=self.current_theme["bg"])

        # Lock frame size
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.parent = parent

        # Define strict grid
        self.grid_rowconfigure(list(range(9)), weight=1)
        self.grid_columnconfigure(list(range(3)), weight=1)

        # Build UI
        self.build_ui()


    def build_ui(self):

        # Mode Label
        self.mode_label = ctk.CTkLabel(
            self,
            text="🕓 Ready?",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.mode_label.grid(column=0, row=0, columnspan=3, pady=(10, 0), sticky="n")

        # Canvas Timer
        self.canvas = tk.Canvas(
            self,
            width=220,
            height=220,
            bg=self.current_theme["canvas"],
            highlightthickness=0,
            bd=0,
            takefocus=0,
        )
        self.canvas.create_oval(
            10,
            10,
            210,
            210,
            outline=self.current_theme["outline"],
            width=6,
            tags="bgcircle",
        )
        self.progress_arc = self.canvas.create_arc(
            10,
            10,
            210,
            210,
            start=90,
            extent=0,
            style="arc",
            outline=self.current_theme["arc"],
            width=8,
        )
        self.timer_text = self.canvas.create_text(
            110,
            110,
            text="00:00",
            fill=self.current_theme["text"],
            font=ctk.CTkFont(size=34, weight="bold"),
        )
        self.canvas.grid(column=0, row=1, columnspan=3, pady=(5, 5))

        # Labels & Inputs
        self.work_label = ctk.CTkLabel(
            self,
            text="Focus (min)",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=10),
        )
        self.work_label.grid(column=0, row=2, pady=(2, 0))
        self.work_entry = ctk.CTkEntry(
            self,
            width=50,
            height=28,
            fg_color=self.current_theme["entry_bg"],
            text_color=self.current_theme["text"],
            placeholder_text="25",
            corner_radius=6,
        )
        self.work_entry.insert(0, "25")
        self.work_entry.grid(column=0, row=3, pady=(0, 2))

        self.break_label = ctk.CTkLabel(
            self,
            text="Break (min)",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=10),
        )
        self.break_label.grid(column=2, row=2, pady=(2, 0))
        self.break_entry = ctk.CTkEntry(
            self,
            width=50,
            height=28,
            fg_color=self.current_theme["entry_bg"],
            text_color=self.current_theme["text"],
            placeholder_text="5",
            corner_radius=6,
        )
        self.break_entry.insert(0, "5")
        self.break_entry.grid(column=2, row=3, pady=(0, 2))

        # Buttons
        self.start_button = ctk.CTkButton(
            self,
            text="🚀 FOCUS",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.current_theme["button_bg"],
            text_color=self.current_theme["button_fg"],
            hover_color=self.current_theme["button_bg_hover"],
            command=lambda: start_timer(
                self.parent,
                self.canvas,
                self.timer_text,
                self.progress_arc,
                self.mode_label,
                self.quote_label,
                self.check_marks,
                self.session_label,
                self.minutes_label,
                self.current_theme,
                self.work_entry,
                self.break_entry,
                self.start_button,
            ),
            width=70,
            height=28,
            corner_radius=8,
        )
        self.start_button.grid(column=0, row=4, pady=(15, 5), padx=(10, 5))

        self.pause_button = ctk.CTkButton(
            self,
            text="⏸ PAUSE",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#4A90E2",
            text_color="white",
            hover_color="#357ABD",
            width=70,
            height=28,
            corner_radius=8,
        )
        self.pause_button.grid(column=1, row=4, pady=(15, 5), padx=5)

        def toggle_pause():
            from .timer_logic import is_paused

            if not is_paused:
                pause_timer()
                self.pause_button.configure(text="▶ RESUME", fg_color="#4A90E2", text_color="white")
            else:
                resume_timer()
                self.pause_button.configure(text="⏸ PAUSE", fg_color="#4A90E2", text_color="white")

        self.pause_button.configure(command=toggle_pause)

        self.reset_button = ctk.CTkButton(
            self,
            text="🔄 RESET",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.current_theme["reset_bg"],
            text_color=self.current_theme["reset_fg"],
            hover_color=self.current_theme["reset_bg_hover"],
            command=lambda: reset_timer(
                self.parent,
                self.canvas,
                self.timer_text,
                self.progress_arc,
                self.mode_label,
                self.quote_label,
                self.check_marks,
                self.session_label,
                self.minutes_label,
                self.current_theme,
                self.start_button,
                self.work_entry,
                self.break_entry,
            ),
            width=70,
            height=28,
            corner_radius=8,
        )
        self.reset_button.grid(column=2, row=4, pady=(15, 5), padx=(5, 10))

        # Info Labels
        self.quote_label = ctk.CTkLabel(
            self,
            text="Let's begin a session.",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=11, slant="italic"),
            wraplength=300,
        )
        self.quote_label.grid(column=0, row=5, columnspan=3, pady=(5, 5))

        self.session_label = ctk.CTkLabel(
            self,
            text="Completed Focus Sessions: 0",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        self.session_label.grid(column=0, row=6, columnspan=3, pady=2)

        self.minutes_label = ctk.CTkLabel(
            self,
            text="Total Focus Minutes: 0",
            text_color=self.current_theme["text"],
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        self.minutes_label.grid(column=0, row=7, columnspan=3, pady=2)

        self.check_marks = ctk.CTkLabel(
            self,
            text="",
            text_color=self.current_theme["arc"],
            font=ctk.CTkFont(size=14),
        )
        self.check_marks.grid(column=1, row=8, pady=2)

        # CustomTkinter buttons handle hover effects automatically

    
