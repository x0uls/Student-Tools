import math
import random
from .constants import (
    DEFAULT_WORK_MIN,
    DEFAULT_BREAK_MIN,
    LONG_BREAK_MIN,
    WORK_QUOTES,
    BREAK_QUOTES,
)

# Global state
is_paused = False
timer = None
reps = 0
time_left = 0
total_time = 0
completed_focus_sessions = 0
total_focus_minutes = 0


def reset_timer(
    window,
    canvas,
    timer_text,
    progress_arc,
    mode_label,
    quote_label,
    check_marks,
    session_label,
    minutes_label,
    theme,
    start_button,   # ✅ this is always the START button
):
    global reps, timer, is_paused, time_left, completed_focus_sessions, total_focus_minutes
    if timer:
        window.after_cancel(timer)
        timer = None  # clear leftover callback

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

    # ✅ Restore Start button
    start_button.config(
        state="normal",
        text="▶ Start",
        bg=theme["button_bg"],
        fg=theme["button_fg"]
    )


def start_timer(
    window,
    canvas,
    timer_text,
    progress_arc,
    mode_label,
    quote_label,
    check_marks,
    session_label,
    minutes_label,
    theme,
    work_entry,
    break_entry,
    start_button,  # 👈 keep start_button always
):
    global reps, total_time, time_left, is_paused, timer

    # Cancel any old timer
    if timer:
        window.after_cancel(timer)
        timer = None

    # ✅ Change to Skip button (but keep same logic)
    start_button.config(
        state="normal",
        text="⏭ Skip",
        bg=theme["button_bg"],
        fg=theme["button_fg"]
    )

    reps += 1
    is_paused = False

    # Validate inputs
    try:
        work_min = int(work_entry.get())
    except ValueError:
        work_min = DEFAULT_WORK_MIN

    try:
        break_min = int(break_entry.get())
    except ValueError:
        break_min = DEFAULT_BREAK_MIN

    # Session logic
    if reps % 8 == 0:
        total_time = LONG_BREAK_MIN * 60
        mode_label.config(
            text="🌙 Long Break", fg=theme["text"]
        )
        quote_label.config(text=random.choice(BREAK_QUOTES))
    elif reps % 2 == 0:
        total_time = break_min * 60
        mode_label.config(
            text="☕ Break", fg=theme["text"]
        )
        quote_label.config(text=random.choice(BREAK_QUOTES))
    else:
        total_time = work_min * 60
        mode_label.config(
            text="💼 Focus", fg=theme["text"]
        )
        quote_label.config(text=random.choice(WORK_QUOTES))

    # Initialize timer
    time_left = total_time
    countdown(
        window,
        canvas,
        timer_text,
        progress_arc,
        mode_label,
        quote_label,
        check_marks,
        session_label,
        minutes_label,
        theme,
        work_entry,
        break_entry,
        start_button,
        resume=False,
    )


def countdown(
    window,
    canvas,
    timer_text,
    progress_arc,
    mode_label,
    quote_label,
    check_marks,
    session_label,
    minutes_label,
    theme,
    work_entry,
    break_entry,
    start_button,  # 👈 keep passing it through
    resume=False,  # flag to avoid stealing a second after resume
):
    global time_left, timer, is_paused, completed_focus_sessions, total_focus_minutes, total_time, reps

    if not is_paused and time_left >= 0:
        # Update display
        minutes = math.floor(time_left / 60)
        seconds = time_left % 60
        canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")

        if total_time > 0:
            progress = (1 - time_left / total_time) * 360
            canvas.itemconfig(progress_arc, extent=progress)

        if time_left == 0:
            # Finished session
            if reps % 2 == 1:  # just finished a focus session
                completed_focus_sessions += 1
                total_focus_minutes += int(work_entry.get() or DEFAULT_WORK_MIN)
                check_marks.config(text="✔" * completed_focus_sessions)
                session_label.config(
                    text=f"Completed Focus Sessions: {completed_focus_sessions}"
                )
                minutes_label.config(text=f"Total Focus Minutes: {total_focus_minutes}")

            # auto-start next session
            start_timer(
                window,
                canvas,
                timer_text,
                progress_arc,
                mode_label,
                quote_label,
                check_marks,
                session_label,
                minutes_label,
                theme,
                work_entry,
                break_entry,
                start_button,  # 👈 don’t drop it!
            )
        else:
            # Only decrement after first tick, unless resuming
            def tick():
                decrement_and_continue(
                    window,
                    canvas,
                    timer_text,
                    progress_arc,
                    mode_label,
                    quote_label,
                    check_marks,
                    session_label,
                    minutes_label,
                    theme,
                    work_entry,
                    break_entry,
                    start_button,
                )

            timer = window.after(1000, tick)


def decrement_and_continue(
    window,
    canvas,
    timer_text,
    progress_arc,
    mode_label,
    quote_label,
    check_marks,
    session_label,
    minutes_label,
    theme,
    work_entry,
    break_entry,
    start_button,
):
    global time_left
    time_left -= 1
    countdown(
        window,
        canvas,
        timer_text,
        progress_arc,
        mode_label,
        quote_label,
        check_marks,
        session_label,
        minutes_label,
        theme,
        work_entry,
        break_entry,
        start_button,
        resume=False,
    )


def pause_timer():
    global is_paused
    is_paused = True


def resume_timer(
    window,
    canvas,
    timer_text,
    progress_arc,
    mode_label,
    quote_label,
    check_marks,
    session_label,
    minutes_label,
    theme,
    work_entry,
    break_entry,
    start_button,
):
    global is_paused, timer
    if is_paused and time_left > 0:
        if timer:
            window.after_cancel(timer)
        is_paused = False
        countdown(
            window,
            canvas,
            timer_text,
            progress_arc,
            mode_label,
            quote_label,
            check_marks,
            session_label,
            minutes_label,
            theme,
            work_entry,
            break_entry,
            start_button,
            resume=True,  # prevent losing a second
        )
