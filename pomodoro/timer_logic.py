import math
import random
import tkinter.messagebox as messagebox
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

# References to UI objects for actions like resume/skip without re-passing everywhere
window_ref = None
canvas_ref = None
timer_text_ref = None
progress_arc_ref = None
mode_label_ref = None
quote_label_ref = None
check_marks_ref = None
session_label_ref = None
minutes_label_ref = None
theme_ref = None
work_entry_ref = None
break_entry_ref = None
start_button_ref = None
skipped_current = False
skipped_elapsed_seconds = 0


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
    start_button,  
    work_entry,
    break_entry,
):
    global reps, timer, is_paused, time_left, completed_focus_sessions, total_focus_minutes
    if timer:
        window.after_cancel(timer)
        timer = None  

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
    # Re-enable inputs
    try:
        work_entry.config(state="normal")
        break_entry.config(state="normal")
    except Exception:
        pass
    # Restore command to start
    start_button.config(command=lambda: start_timer(
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
    ))


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
    start_button,
):
    global reps, total_time, time_left, is_paused, timer, skipped_current, skipped_elapsed_seconds

    # Cancel any old timer
    if timer:
        window.after_cancel(timer)
        timer = None

    # ✅ Change to Skip button
    start_button.config(
        state="normal",
        text="⏭ Skip",
        bg=theme["button_bg"],
        fg=theme["button_fg"]
    )
    # Store references for pause/resume/skip
    global window_ref, canvas_ref, timer_text_ref, progress_arc_ref, mode_label_ref, quote_label_ref, check_marks_ref, session_label_ref, minutes_label_ref, theme_ref, work_entry_ref, break_entry_ref, start_button_ref
    window_ref = window
    canvas_ref = canvas
    timer_text_ref = timer_text
    progress_arc_ref = progress_arc
    mode_label_ref = mode_label
    quote_label_ref = quote_label
    check_marks_ref = check_marks
    session_label_ref = session_label
    minutes_label_ref = minutes_label
    theme_ref = theme
    work_entry_ref = work_entry
    break_entry_ref = break_entry
    start_button_ref = start_button

    start_button.config(command=skip_current_session)

    # Reset skip tracking for this session
    skipped_current = False
    skipped_elapsed_seconds = 0

    reps += 1
    is_paused = False

    # Validate and clamp inputs
    def _safe_int(value, default):
        try:
            v = int(value)
        except Exception:
            return default
        return max(1, min(120, v))

    raw_work = work_entry.get()
    raw_break = break_entry.get()
    work_min = _safe_int(raw_work, DEFAULT_WORK_MIN)
    break_min = _safe_int(raw_break, DEFAULT_BREAK_MIN)

    # Show one-time warning if clamped
    warnings = []
    try:
        if int(raw_work) != work_min:
            warnings.append(f"Focus minutes adjusted to {work_min} (allowed: 1–120)")
    except Exception:
        if raw_work.strip() != "":
            warnings.append(f"Focus minutes adjusted to {work_min} (allowed: 1–120)")
    try:
        if int(raw_break) != break_min:
            warnings.append(f"Break minutes adjusted to {break_min} (allowed: 1–120)")
    except Exception:
        if raw_break.strip() != "":
            warnings.append(f"Break minutes adjusted to {break_min} (allowed: 1–120)")
    if warnings:
        try:
            messagebox.showwarning("Invalid input", "\n".join(warnings))
        except Exception:
            pass

    # Disable inputs during an active session
    try:
        work_entry.config(state="disabled")
        break_entry.config(state="disabled")
    except Exception:
        pass

    # Session logic
    if reps % 8 == 0:
        total_time = LONG_BREAK_MIN * 60
        mode_label.config(text="🌙 Long Break", fg=theme["text"])
        quote_label.config(text=random.choice(BREAK_QUOTES))
    elif reps % 2 == 0:
        total_time = break_min * 60
        mode_label.config(text="☕ Break", fg=theme["text"])
        quote_label.config(text=random.choice(BREAK_QUOTES))
    else:
        total_time = work_min * 60
        mode_label.config(text="💼 Focus", fg=theme["text"])
        quote_label.config(text=random.choice(WORK_QUOTES))

    # Initialize display cleanly (no 00:00 flash)
    time_left = total_time
    minutes = time_left // 60
    seconds = time_left % 60
    canvas.itemconfig(timer_text, text=f"{minutes:02}:{seconds:02}")
    canvas.itemconfig(progress_arc, extent=0)

    # Start countdown loop
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
    start_button,
    resume=False,
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
                if skipped_current:
                    # Add only actually focused whole minutes, don't count as completed session
                    add_min = max(0, skipped_elapsed_seconds // 60)
                    if add_min > 0:
                        total_focus_minutes += add_min
                        minutes_label.config(text=f"Total Focus Minutes: {total_focus_minutes}")
                else:
                    completed_focus_sessions += 1
                    # Safe add to total focus minutes
                    try:
                        add_min = int(work_entry.get())
                    except Exception:
                        add_min = DEFAULT_WORK_MIN
                    total_focus_minutes += max(1, min(120, add_min))
                    check_marks.config(text="✔" * completed_focus_sessions)
                    session_label.config(
                        text=f"Completed Focus Sessions: {completed_focus_sessions}"
                    )
                    minutes_label.config(text=f"Total Focus Minutes: {total_focus_minutes}")

            # Auto-start next session
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
                start_button,
            )
        else:
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
    global is_paused, timer
    is_paused = True
    # Cancel any pending tick so time doesn't decrement while paused
    if window_ref is not None and timer is not None:
        try:
            window_ref.after_cancel(timer)
        except Exception:
            pass
        timer = None


def resume_timer():
    global is_paused, timer
    if is_paused and time_left > 0:
        if timer and window_ref is not None:
            try:
                window_ref.after_cancel(timer)
            except Exception:
                pass
        is_paused = False
        countdown(
            window_ref,
            canvas_ref,
            timer_text_ref,
            progress_arc_ref,
            mode_label_ref,
            quote_label_ref,
            check_marks_ref,
            session_label_ref,
            minutes_label_ref,
            theme_ref,
            work_entry_ref,
            break_entry_ref,
            start_button_ref,
            resume=True,
        )


def skip_current_session():
    """Skip immediately to the next session without double-incrementing reps."""
    global time_left, timer, skipped_current, skipped_elapsed_seconds
    if window_ref is not None and timer is not None:
        try:
            window_ref.after_cancel(timer)
        except Exception:
            pass
        timer = None
    # Force finish current session and let countdown handle the transition
    # Ensure not paused so the transition happens
    global is_paused
    is_paused = False
    # Record elapsed seconds in this session to compute partial minutes
    try:
        skipped_elapsed_seconds = max(0, total_time - time_left)
    except Exception:
        skipped_elapsed_seconds = 0
    skipped_current = True
    time_left = 0
    countdown(
        window_ref,
        canvas_ref,
        timer_text_ref,
        progress_arc_ref,
        mode_label_ref,
        quote_label_ref,
        check_marks_ref,
        session_label_ref,
        minutes_label_ref,
        theme_ref,
        work_entry_ref,
        break_entry_ref,
        start_button_ref,
        resume=False,
    )
