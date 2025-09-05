import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .semester_detail_page import GRADE_POINTS


class GPAChartPage(ctk.CTkFrame):
    def __init__(self, parent, semesters, go_back_callback):
        super().__init__(parent)
        self.parent = parent
        self.semesters = semesters
        self.go_back_callback = go_back_callback

        # Header
        ctk.CTkLabel(
            self, text="Semester GPA Trend", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Back button
        ctk.CTkButton(self, text="Back", command=self.go_back).pack(pady=5)

        # Chart frame
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Matplotlib figure
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Semester GPA Trend")
        self.ax.set_xlabel("Semester")
        self.ax.set_ylabel("GPA")
        self.ax.set_ylim(0, 4)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Draw chart
        self.draw_chart()

    def draw_chart(self):
        gpas = [sem["gpa"] for sem in self.semesters]
        self.ax.clear()

        # Plot line + markers (clip_on=False so dots at 4.0 aren’t cut off)
        self.ax.plot(
            range(1, len(gpas) + 1),
            gpas,
            marker="o",
            color="blue",
            linewidth=2,
            clip_on=False,  # keep full marker visible
        )

        # Titles/labels
        self.ax.set_title("Semester GPA Trend")
        self.ax.set_xlabel("Semester")
        self.ax.set_ylabel("GPA")

        # Fix Y-axis to GPA scale
        self.ax.set_ylim(0, 4)

        # X ticks
        self.ax.set_xticks(range(1, len(gpas) + 1))

        self.canvas.draw()

    def go_back(self):
        self.place_forget()
        self.go_back_callback()
