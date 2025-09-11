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

        # Header with back button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back",
            font=ctk.CTkFont(size=12),
            height=30,
            width=70,
            corner_radius=8,
            command=self.go_back,
        )
        back_btn.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="GPA Trend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="right")

        # Chart frame
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))

        # Matplotlib figure - optimized for mobile
        self.figure = Figure(figsize=(3.2, 2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Configure for mobile display
        self.figure.patch.set_facecolor('#2b2b2b')  # Dark background
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white', labelsize=8)
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
