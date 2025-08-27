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
        self.resizable(False, False)  # Prevent resizing

        # Container for pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        # Dictionary to hold page objects (initially empty)
        self.pages = {}

        # Bottom navigation bar
        navbar = ctk.CTkFrame(self, height=50)
        navbar.pack(side="bottom", fill="x")

        # Use grid layout for even spacing
        navbar.grid_columnconfigure((0, 1, 2), weight=1)  # three columns, equal width

        ctk.CTkButton(navbar, text="GPA", command=lambda: self.show_page("gpa")).grid(
            row=0, column=0, sticky="nsew"
        )
        ctk.CTkButton(
            navbar, text="Pomodoro", command=lambda: self.show_page("pomodoro")
        ).grid(row=0, column=1, sticky="nsew")
        ctk.CTkButton(
            navbar, text="Reminder", command=lambda: self.show_page("reminder")
        ).grid(row=0, column=2, sticky="nsew")
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
