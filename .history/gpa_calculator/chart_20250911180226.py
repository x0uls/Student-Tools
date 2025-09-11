import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GPAChartPage(ctk.CTkFrame):
    """Page displaying GPA trend chart with bar and line visualization."""
    
    def __init__(self, parent, semesters, go_back_callback):
        """Initialize chart page with header and matplotlib figure."""
        super().__init__(parent)
        self.semesters = semesters
        self.go_back_callback = go_back_callback

        # Create header with back button and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
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
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="GPA Trend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="right")

        # Create chart frame and matplotlib figure
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))

        self.figure = Figure(figsize=(3.2, 2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Configure white background for mobile display
        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        self.ax.tick_params(colors='black', labelsize=8)
        self.ax.set_ylim(0, 4.2)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.draw_chart()

    def _configure_axes(self):
        """Configure chart axes with labels, limits, and grid."""
        self.ax.set_facecolor('white')
        self.ax.tick_params(colors='black', labelsize=8)
        self.ax.set_xlabel("Semester", color='black', fontsize=9)
        self.ax.set_ylabel("GPA", color='black', fontsize=9)
        self.ax.set_ylim(0, 4.2)
        self.ax.set_yticks([0, 1, 2, 3, 4])
        self.ax.grid(True, alpha=0.3, color='gray')

    def draw_chart(self):
        """Draw GPA trend chart with bars and line, or show no data message."""
        gpas = [sem["gpa"] for sem in self.semesters if sem.get("gpa", 0) > 0]
        if not gpas or not self.semesters:
            self.ax.clear()
            self._configure_axes()
            self.ax.text(0.5, 0.5, 'No semester data available', 
                        transform=self.ax.transAxes, ha='center', va='center',
                        fontsize=12, color='gray')
            self.canvas.draw()
            return
            
        self.ax.clear()
        self._configure_axes()

        # Plot bars for semester GPAs
        self.ax.bar(
            range(1, len(gpas) + 1),
            gpas,
            color="#4A9EFF",
            alpha=0.6,
            width=0.6,
            label="Semester GPA"
        )
        
        # Plot line curve for trend
        self.ax.plot(
            range(1, len(gpas) + 1),
            gpas,
            marker="o",
            color="#FF6B6B",
            linewidth=3,
            markersize=8,
            markerfacecolor="white",
            markeredgecolor="#FF6B6B",
            markeredgewidth=2,
            label="GPA Trend"
        )

        self.ax.set_xticks(range(1, len(gpas) + 1))
        self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.20), 
                      ncol=2, fontsize=8, framealpha=0.9)
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw()

    def go_back(self):
        """Hide chart page and return to main page."""
        self.place_forget()
        self.go_back_callback()
