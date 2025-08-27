# ui.py
import tkinter as tk
from constants import LIGHT_THEME, DARK_THEME, FONT_NAME
from timer_logic import start_timer, reset_timer, pause_timer, resume_timer, is_paused


class PomodoroPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=360, height=640, bg="white")

        # Lock frame size
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.is_dark_mode = False
        self.current_theme = LIGHT_THEME
        self.parent = parent

        # Define strict grid
        self.grid_rowconfigure(list(range(9)), weight=1)
        self.grid_columnconfigure(list(range(3)), weight=1)

        # Build UI
        self.build_ui()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME

        # Update colors
        self.config(bg=self.current_theme["bg"])
        self.canvas.config(bg=self.current_theme["canvas"])
        self.canvas.itemconfig(self.progress_arc, outline=self.current_theme["arc"])
        self.canvas.itemconfig(self.timer_text, fill=self.current_theme["text"])
        self.canvas.itemconfig("bgcircle", outline=self.current_theme["outline"])

        self.theme_toggle.config(
            text="🌙" if self.is_dark_mode else "☀️",
            bg=self.current_theme["bg"],
            fg="white" if self.is_dark_mode else "black",
            activebackground=self.current_theme["bg"],
            activeforeground="white" if self.is_dark_mode else "black",
            selectcolor=self.current_theme["bg"]
        )

        for widget in [
            self.mode_label, self.work_label, self.break_label,
            self.quote_label, self.check_marks, self.session_label, self.minutes_label
        ]:
            widget.config(bg=self.current_theme["bg"], fg=self.current_theme["text"])

        self.work_entry.config(bg=self.current_theme["entry_bg"], fg=self.current_theme["text"], insertbackground=self.current_theme["text"])
        self.break_entry.config(bg=self.current_theme["entry_bg"], fg=self.current_theme["text"], insertbackground=self.current_theme["text"])
        self.start_button.config(bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"])
        self.reset_button.config(bg="#ff6f61", fg="white")

    def build_ui(self):
        # Theme Toggle
        self.theme_toggle = tk.Checkbutton(
            self, text="☀️", bg=self.current_theme["bg"], fg="black", font=(FONT_NAME, 12, "bold"),
            selectcolor=self.current_theme["bg"], activebackground=self.current_theme["bg"], activeforeground="black",
            bd=0, highlightthickness=0, indicatoron=False, cursor="hand2", padx=5, pady=2,
            command=self.toggle_theme
        )
        self.theme_toggle.place(relx=1.0, x=-10, y=10, anchor="ne")

        # Mode Label
        self.mode_label = tk.Label(self, text="🕓 Ready?", fg=self.current_theme["text"],
                                   bg=self.current_theme["bg"], font=(FONT_NAME, 22, "bold"))
        self.mode_label.grid(column=0, row=0, columnspan=3, pady=(10, 0), sticky="n")

        # Canvas Timer
        self.canvas = tk.Canvas(self, width=220, height=220, bg=self.current_theme["canvas"], highlightthickness=0)
        self.canvas.create_oval(10, 10, 210, 210, outline=self.current_theme["outline"], width=6, tags="bgcircle")
        self.progress_arc = self.canvas.create_arc(10, 10, 210, 210, start=90, extent=0, style="arc",
                                                   outline=self.current_theme["arc"], width=8)
        self.timer_text = self.canvas.create_text(110, 110, text="00:00", fill=self.current_theme["text"],
                                                  font=(FONT_NAME, 34, "bold"))
        self.canvas.grid(column=0, row=1, columnspan=3, pady=(5, 5))

        # Labels & Inputs
        self.work_label = tk.Label(self, text="Focus (min)", bg=self.current_theme["bg"], fg=self.current_theme["text"], font=(FONT_NAME, 10))
        self.work_label.grid(column=0, row=2, pady=2)
        self.work_entry = tk.Entry(self, width=5, bg=self.current_theme["entry_bg"], fg=self.current_theme["text"])
        self.work_entry.insert(0, "25")
        self.work_entry.grid(column=0, row=3, pady=2)

        self.break_label = tk.Label(self, text="Break (min)", bg=self.current_theme["bg"], fg=self.current_theme["text"], font=(FONT_NAME, 10))
        self.break_label.grid(column=2, row=2, pady=2)
        self.break_entry = tk.Entry(self, width=5, bg=self.current_theme["entry_bg"], fg=self.current_theme["text"])
        self.break_entry.insert(0, "5")
        self.break_entry.grid(column=2, row=3, pady=2)

        # Buttons
        self.start_button = tk.Button(self, text="▶ Start", font=(FONT_NAME, 11),
                                      bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"],
                                      command=lambda: start_timer(self.parent, self.canvas, self.timer_text,
                                                                  self.progress_arc, self.mode_label, self.quote_label,
                                                                  self.check_marks, self.session_label,
                                                                  self.minutes_label, self.current_theme,
                                                                  self.work_entry, self.break_entry),
                                      width=8)
        self.start_button.grid(column=0, row=4, pady=10)

        self.pause_button = tk.Button(self, text="⏸ Pause", font=(FONT_NAME, 11),
                                      bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"], width=8)
        self.pause_button.grid(column=1, row=4, pady=10)

        def toggle_pause():
            from timer_logic import is_paused
            if not is_paused:
                pause_timer()
                self.pause_button.config(text="▶ Resume")
            else:
                resume_timer(self.parent, self.canvas, self.timer_text, self.progress_arc,
                             self.mode_label, self.quote_label, self.check_marks,
                             self.session_label, self.minutes_label, self.current_theme,
                             self.work_entry, self.break_entry)
                self.pause_button.config(text="⏸ Pause")

        self.pause_button.config(command=toggle_pause)

        self.reset_button = tk.Button(self, text="🔁 Reset", font=(FONT_NAME, 11), bg="#ff6f61", fg="white",
                                      command=lambda: reset_timer(self.parent, self.canvas, self.timer_text,
                                                                  self.progress_arc, self.mode_label, self.quote_label,
                                                                  self.check_marks, self.session_label,
                                                                  self.minutes_label, self.current_theme),
                                      width=8)
        self.reset_button.grid(column=2, row=4, pady=10)

        # Info Labels
        self.quote_label = tk.Label(self, text="Let's begin a session.", fg=self.current_theme["text"],
                                    bg=self.current_theme["bg"], font=(FONT_NAME, 11, "italic"), wraplength=300)
        self.quote_label.grid(column=0, row=5, columnspan=3, pady=(5, 5))

        self.session_label = tk.Label(self, text="Completed Focus Sessions: 0", fg=self.current_theme["text"],
                                      bg=self.current_theme["bg"], font=(FONT_NAME, 10, "bold"))
        self.session_label.grid(column=0, row=6, columnspan=3, pady=2)

        self.minutes_label = tk.Label(self, text="Total Focus Minutes: 0", fg=self.current_theme["text"],
                                      bg=self.current_theme["bg"], font=(FONT_NAME, 10, "bold"))
        self.minutes_label.grid(column=0, row=7, columnspan=3, pady=2)

        self.check_marks = tk.Label(self, text="", fg=self.current_theme["arc"],
                                    bg=self.current_theme["bg"], font=(FONT_NAME, 14))
        self.check_marks.grid(column=1, row=8, pady=2)
