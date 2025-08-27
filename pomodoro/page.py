import tkinter as tk
from ui import PomodoroPage

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Pomodoro Timer")

    window.geometry("360x640")
    window.resizable(False, False)

    app = PomodoroPage(window)
    app.pack(fill="none", expand=False)

    window.mainloop()
