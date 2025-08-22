import tkinter as tk


class PomodoroPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        tk.Label(
            self,
            text="Pomodoro Timer (Coming Soon)",
            font=("Helvetica", 20, "bold"),
            bg="white",
        ).pack(pady=40)
