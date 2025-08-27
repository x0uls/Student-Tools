import math
import random
from constants import DEFAULT_WORK_MIN, DEFAULT_BREAK_MIN, LONG_BREAK_MIN, WORK_QUOTES, BREAK_QUOTES

# Global state
is_paused = False
timer = None
reps = 0
time_left = 0
total_time = 0
completed_focus_sessions = 0
total_focus_minutes = 0


def reset_timer(window, canvas, timer_text, progress_arc, mode_label, quote_label,
                check_marks, session_label, minutes_label, theme):
    global reps, timer, is_paused, time_left, completed_focus_sessions, total_focus_minutes
    if timer:
        window.after_cancel(timer)
    reps = 0
    is_paused = False
    time_left = 0
    completed_focus_sessions = 0
    total_focus_minutes = 0

    canvas.itemconfig(timer_text, text="00:00")
    canvas.itemconfig(progress_arc, extent=0)
    mode_label.config(text="🕓 Ready?", fg=theme["text"])
    quote_label.config(text="Let's begin a session.")
    check_marks.config(text="")
    session_label.config(text="Completed Focus Sessions: 0")
    minutes_label.config(text="Total Focus Minutes: 0")


def start_timer(window, canvas, timer_text, progress_arc, mode_label, quote_label,
                check_marks, session_label, minutes_label, theme,
                work_entry, break_entry):
    global reps, total_time, time_left, is_paused
    reps += 1
    is_paused = False

    work_min = int(work_entry.get() or DEFAULT_WORK_MIN)
    break_min = int(break_entry.get() or DEFAULT_BREAK_MIN)

    if reps % 8 == 0:
        total_time = LONG_BREAK_MIN * 60
        mode_label.config(text="🌙 Long Break", fg="red")
        quote_label.config(text=random.choice(BREAK_QUOTES))
    elif reps % 2 == 0:
        total_time = break_min * 60
        mode_label.config(text="☕ Break", fg="orange")
        quote_label.config(text=random.choice(BREAK_QUOTES))
    else:
        total_time = work_min * 60
        mode_label.config(text="💼 Focus", fg="green")
        quote_label.config(text=random.choice(WORK_QUOTES))

    time_left = total_time
    countdown(window, canvas, timer_text, progress_arc, mode_label, quote_label,
              check_marks, session_label, minutes_label, theme,
              work_entry, break_entry)


def countdown(window, canvas, timer_text, progress_arc, mode_label, quote_label,
              check_marks, session_label, minutes_label, theme,
              work_entry, break_entry):
    global time_left, timer, is_paused, completed_focus_sessions, total_focus_minutes

    if not is_paused and time_left > 0:
        minutes = math.floor(time_left / 60)
        seconds = time_left % 60
        canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")

        progress = (1 - time_left / total_time) * 360
        canvas.itemconfig(progress_arc, extent=progress)

        time_left -= 1
        timer = window.after(1000, countdown, window, canvas, timer_text, progress_arc,
                             mode_label, quote_label, check_marks, session_label,
                             minutes_label, theme, work_entry, break_entry)

    elif time_left == 0:
        if reps % 2 == 1:  # finished work session
            completed_focus_sessions += 1
            total_focus_minutes += int(work_entry.get() or DEFAULT_WORK_MIN)
            check_marks.config(text="✔" * completed_focus_sessions)
            session_label.config(text=f"Completed Focus Sessions: {completed_focus_sessions}")
            minutes_label.config(text=f"Total Focus Minutes: {total_focus_minutes}")
        start_timer(window, canvas, timer_text, progress_arc, mode_label, quote_label,
                    check_marks, session_label, minutes_label, theme,
                    work_entry, break_entry)


def pause_timer():
    global is_paused
    is_paused = True


def resume_timer(window, canvas, timer_text, progress_arc, mode_label, quote_label,
                 check_marks, session_label, minutes_label, theme,
                 work_entry, break_entry):
    global is_paused
    if is_paused:
        is_paused = False
        countdown(window, canvas, timer_text, progress_arc, mode_label, quote_label,
                  check_marks, session_label, minutes_label, theme,
                  work_entry, break_entry)
