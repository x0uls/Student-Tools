import tkinter as tk


class SemesterCard(tk.Frame):
    def __init__(self, parent, semester_name, gpa, on_click):
        super().__init__(parent, bg="#f0f0f0", bd=2, relief="groove", padx=10, pady=5)
        tk.Label(
            self, text=semester_name, font=("Helvetica", 16, "bold"), bg="#f0f0f0"
        ).pack(anchor="w")
        tk.Label(self, text=f"GPA: {gpa}", font=("Helvetica", 12), bg="#f0f0f0").pack(
            anchor="w"
        )
        self.bind("<Button-1>", lambda e: on_click())
