import tkinter as tk


class ReminderPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        tk.Label(
            self,
            text="Reminder App (Coming Soon)",
            font=("Helvetica", 20, "bold"),
            bg="white",
        ).pack(pady=40)
