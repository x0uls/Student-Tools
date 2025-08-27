import customtkinter as ctk
from PIL import Image

# Global appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

from gpa_calculator import GPACalculatorPage
from pomodoro import PomodoroPage
from reminder import ReminderPage


class MultiToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Multi-Tool")
        self.geometry("360x640")
        self.resizable(False, False)

        # Container for pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        # Dictionary to hold page objects
        self.pages = {}

        # --- Load images ---
        self.icon_size = (28, 28)
        self.calc_icon = self.load_icon("assets/calculator.png")
        self.timer_icon = self.load_icon("assets/timer.png")
        self.remind_icon = self.load_icon("assets/reminder.png")

        # Bottom navigation bar
        navbar = ctk.CTkFrame(self, height=50)
        navbar.pack(side="bottom", fill="x")
        navbar.grid_columnconfigure((0, 1, 2), weight=1)

        # Icon buttons
        ctk.CTkButton(
            navbar,
            image=self.calc_icon,
            text="",
            command=lambda: self.show_page("gpa"),
            hover_color="#1a2b4c",
        ).grid(row=0, column=0, sticky="nsew")

        ctk.CTkButton(
            navbar,
            image=self.timer_icon,
            text="",
            command=lambda: self.show_page("pomodoro"),
            hover_color="#1a2b4c",
        ).grid(row=0, column=1, sticky="nsew")

        ctk.CTkButton(
            navbar,
            image=self.remind_icon,
            text="",
            command=lambda: self.show_page("reminder"),
            hover_color="#1a2b4c",
        ).grid(row=0, column=2, sticky="nsew")

        # Start with GPA page
        self.show_page("gpa")

    def load_icon(self, path):
        """Helper to load and resize icons as CTkImage."""
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=self.icon_size)

    def show_page(self, page_name):
        if page_name not in self.pages:
            if page_name == "gpa":
                self.pages[page_name] = GPACalculatorPage(self.container)
            elif page_name == "pomodoro":
                self.pages[page_name] = PomodoroPage(self.container)
            elif page_name == "reminder":
                self.pages[page_name] = ReminderPage(self.container)

            self.pages[page_name].place(relwidth=1, relheight=1)

        self.pages[page_name].lift()


if __name__ == "__main__":
    app = MultiToolApp()
    app.mainloop()
