import customtkinter as ctk

# Global appearance
ctk.set_appearance_mode("dark")  # "dark" or "system"
ctk.set_default_color_theme("dark-blue")  # "blue", "green", "dark-blue"

from gpa_calculator import GPACalculatorPage
from pomodoro import PomodoroPage
from reminder import ReminderPage


class MultiToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Multi-Tool")
        self.geometry("360x640")

        # Container for pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        # Dictionary to hold page objects (initially empty)
        self.pages = {}

        # Bottom navigation bar
        navbar = ctk.CTkFrame(self, height=50)
        navbar.pack(side="bottom", fill="x")

        ctk.CTkButton(navbar, text="GPA", command=lambda: self.show_page("gpa")).pack(
            side="left", expand=True, fill="both"
        )
        ctk.CTkButton(
            navbar, text="Pomodoro", command=lambda: self.show_page("pomodoro")
        ).pack(side="left", expand=True, fill="both")
        ctk.CTkButton(
            navbar, text="Reminder", command=lambda: self.show_page("reminder")
        ).pack(side="left", expand=True, fill="both")

        # Start with GPA page
        self.show_page("gpa")

    def show_page(self, page_name):
        # If page doesn't exist yet, create it
        if page_name not in self.pages:
            if page_name == "gpa":
                self.pages[page_name] = GPACalculatorPage(self.container)
            elif page_name == "pomodoro":
                self.pages[page_name] = PomodoroPage(self.container)
            elif page_name == "reminder":
                self.pages[page_name] = ReminderPage(self.container)

            self.pages[page_name].place(relwidth=1, relheight=1)

        # Bring the page to front
        self.pages[page_name].lift()


if __name__ == "__main__":
    app = MultiToolApp()
    app.mainloop()
