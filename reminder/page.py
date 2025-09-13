import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import json
import os
import threading
import time


class Reminder:
    """
    Handles scheduling and displaying reminders.
    """
    def __init__(self, message, remind_time, repeat=False, interval_minutes=0, callback=None):
        self.message = message
        self.remind_time = remind_time
        self.repeat = repeat
        self.interval = timedelta(minutes=interval_minutes)
        self.callback = callback  # Function to call for UI updates
        self._stop_event = threading.Event()
        self.thread = None

    def start(self):
        def run():
            while not self._stop_event.is_set():
                now = datetime.now()
                wait_seconds = (self.remind_time - now).total_seconds()
                if wait_seconds > 0:
                    time.sleep(min(wait_seconds, 1))
                    continue
                if self.callback:
                    self.callback(self, self.message)
                if self.repeat:
                    self.remind_time += self.interval
                else:
                    break
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)


class ReminderPage(ctk.CTkFrame):
    """
    The main page for setting reminders.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._storage_path = os.path.join(os.path.dirname(__file__), "reminders.json")

        # Main scrollable area (themed)
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.scrollable_frame,
            text="⏰ Simple Reminder App",
            font=("Helvetica", 18, "bold"),
        ).pack(pady=10)

        # Reminder message input
        ctk.CTkLabel(self.scrollable_frame, text="Reminder Message:").pack()
        self.msg_entry = ctk.CTkEntry(self.scrollable_frame, width=300, placeholder_text="What should I remind you?")
        self.msg_entry.pack(pady=5)

        # Date selector (themed entry + calendar button)
        ctk.CTkLabel(self.scrollable_frame, text="Date:").pack()
        date_row = ctk.CTkFrame(self.scrollable_frame)
        date_row.pack(pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ctk.CTkEntry(date_row, width=180, textvariable=self.date_var, placeholder_text="yyyy-mm-dd")
        self.date_entry.pack(side="left", padx=(0, 6))
        
        # Auto-format date with dashes and validation
        def format_date(event=None):
            current = self.date_var.get()
            digits_only = ''.join(filter(str.isdigit, current))[:8]  # Limit to 8 digits
            
            if len(digits_only) < 4:
                formatted = digits_only
            else:
                formatted = digits_only[:4]  # Year
                if len(digits_only) >= 5:
                    month_first = digits_only[4]
                    if month_first in '01':
                        formatted += "-" + month_first
                        if len(digits_only) >= 6:
                            month_second = digits_only[5]
                            if (month_first == '0' and month_second in '123456789') or \
                               (month_first == '1' and month_second in '012'):
                                formatted += month_second
                                if len(digits_only) >= 7:
                                    formatted += "-" + digits_only[6]
                                    if len(digits_only) >= 8:
                                        day_second = digits_only[7]
                                        day_value = int(digits_only[6:8])
                                        month_value = int(digits_only[4:6])
                                        max_days = {1:31,3:31,5:31,7:31,8:31,10:31,12:31,4:30,6:30,9:30,11:30,2:28}
                                        if day_value <= max_days.get(month_value, 31):
                                            formatted += day_second
                    else:
                        return
            
            if formatted != current:
                self.date_var.set(formatted)
        
        self.date_entry.bind('<KeyRelease>', format_date)
        ctk.CTkButton(date_row, text="📅", width=40, command=self.open_calendar).pack(side="left")

        # Time picker (simple entry fields)
        ctk.CTkLabel(self.scrollable_frame, text="Time:").pack()
        time_frame = ctk.CTkFrame(self.scrollable_frame)
        time_frame.pack(pady=5)
        
        # 12-hour format time entry with AM/PM
        self.hour_var = tk.StringVar(value="8")
        self.minute_var = tk.StringVar(value="00")
        self.ampm_var = tk.StringVar(value="AM")
        
        # Validation functions
        def _validate_range(proposed_value, min_val, max_val):
            return not proposed_value or (proposed_value.isdigit() and min_val <= int(proposed_value) <= max_val)
        
        _validate_hour = lambda v: _validate_range(v, 1, 12)
        _validate_minute = lambda v: _validate_range(v, 0, 59)
        
        # Hour entry (1-12)
        hour_vcmd = self.register(_validate_hour)
        self.hour_entry = ctk.CTkEntry(
            time_frame, 
            textvariable=self.hour_var, 
            width=60,
            placeholder_text="8"
        )
        self.hour_entry.configure(validate="key", validatecommand=(hour_vcmd, "%P"))
        self.hour_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(time_frame, text=":").pack(side="left", padx=2)
        
        # Minute entry (00-59)
        minute_vcmd = self.register(_validate_minute)
        self.minute_entry = ctk.CTkEntry(
            time_frame, 
            textvariable=self.minute_var, 
            width=60,
            placeholder_text="00"
        )
        self.minute_entry.configure(validate="key", validatecommand=(minute_vcmd, "%P"))
        self.minute_entry.pack(side="left", padx=(5, 5))
        
        # AM/PM selection
        self.ampm_combo = ctk.CTkComboBox(
            time_frame,
            variable=self.ampm_var,
            width=60,
            values=["AM", "PM"],
            fg_color=("gray75", "gray25"),
            button_color=("gray70", "gray30"),
            button_hover_color=("gray60", "gray40")
        )
        self.ampm_combo.pack(side="left", padx=(5, 0))


        # Remind after (minutes) input
        ctk.CTkLabel(self.scrollable_frame, text="Remind After (minutes):").pack()

        # Validation: only allow blank (for editing) or positive integers
        _validate_positive = lambda v: not v or (v.isdigit() and int(v) > 0)
        vcmd = self.register(_validate_positive)
        self.minutes_entry = ctk.CTkEntry(self.scrollable_frame, width=100, placeholder_text="e.g. 15")
        # CTkEntry supports underlying validate options from tkinter.Entry
        self.minutes_entry.configure(validate="key", validatecommand=(vcmd, "%P"))
        self.minutes_entry.pack(pady=5)

        # Repeat checkbox and interval
        self.repeat_var = tk.BooleanVar()
        repeat_frame = ctk.CTkFrame(self.scrollable_frame)
        repeat_frame.pack(pady=5)
        ctk.CTkCheckBox(repeat_frame, text="Repeat", variable=self.repeat_var, command=self._on_repeat_toggle).pack(side="left")
        ctk.CTkLabel(repeat_frame, text="every").pack(side="left", padx=(10, 0))
        # Validation for repeat interval: positive integers only
        self._repeat_vcmd = self.register(_validate_positive)
        self.repeat_interval_entry = ctk.CTkEntry(repeat_frame, width=60, placeholder_text="min")
        self.repeat_interval_entry.configure(validate="key", validatecommand=(self._repeat_vcmd, "%P"))
        self.repeat_interval_entry.pack(side="left", padx=5)
        ctk.CTkLabel(repeat_frame, text="minutes").pack(side="left")
        # Initialize repeat interval disabled by default
        self._on_repeat_toggle()

        # Add Reminder button
        ctk.CTkButton(self.scrollable_frame, text="Set Reminder", command=self.add_reminder).pack(pady=10)

        # Reminders section with border (card)
        reminders_card = ctk.CTkFrame(self.scrollable_frame, corner_radius=12, border_width=1)
        reminders_card.pack(pady=8, padx=8, fill="x")
        ctk.CTkLabel(reminders_card, text="Your Reminders:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
        self.reminder_list = ctk.CTkScrollableFrame(reminders_card, height=180)
        self.reminder_list.pack(padx=8, pady=8, fill="x")

        self.reminder_vars = []      # BooleanVar for each reminder
        self.reminder_widgets = []   # Checkbutton widget for each reminder row
        self.reminders = []          # (Reminder instance, display_text)

        # Delete button for selected reminders
        self.delete_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="Delete Selected",
            command=self.delete_selected_reminder,
            state="disabled"
        )
        self.delete_btn.pack(pady=8)

        # Load saved reminders from disk
        self.load_reminders()

    def show_reminder(self, reminder, message):
        self.after(0, lambda: self._show_toast_notification(reminder, message))

    # --- Phone-like toast notification ---
    def _show_toast_notification(self, reminder, message):
        if not hasattr(self, "_active_toasts"):
            self._active_toasts = []

        parent = self.winfo_toplevel()

        # Play notification sound (non-blocking if possible)
        try:
            import sys
            if sys.platform.startswith("win"):
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK) if hasattr(winsound, 'MessageBeep') else winsound.Beep(1000, 120)
            else:
                parent.bell()
        except Exception:
            pass

        toast = ctk.CTkToplevel(parent)
        toast.overrideredirect(True)
        try:
            toast.attributes("-topmost", True, "-alpha", 0.0)
        except Exception:
            pass

        # Content
        container = ctk.CTkFrame(toast, corner_radius=14)
        container.pack(fill="both", expand=True, padx=2, pady=2)
        title = ctk.CTkLabel(container, text="⏰ Reminder", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(anchor="w", padx=14, pady=(12, 2))
        body = ctk.CTkLabel(container, text=message, wraplength=260, font=ctk.CTkFont(size=12))
        body.pack(anchor="w", padx=14, pady=(0, 10))
        btn_row = ctk.CTkFrame(container)
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        dismiss_btn = ctk.CTkButton(btn_row, text="Dismiss", width=90, command=lambda: _close(True))
        dismiss_btn.pack(side="right", padx=6)

        # Geometry: bottom-right inside the app window, stack upward
        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        width = 300
        height = 110
        gap = 8
        margin = 16
        stack_index = len(self._active_toasts)
        x = px + pw - width - margin
        target_y = py + ph - (height + margin) - stack_index * (height + gap)

        # Start slightly below (for slide-up)
        start_y = target_y + 30
        toast.geometry(f"{width}x{height}+{x}+{start_y}")

        # Track
        record = {"win": toast, "target_y": target_y, "x": x, "height": height}
        self._active_toasts.append(record)

        # Slide + fade-in animation
        def animate_step(alpha=0.0, y=start_y):
            try:
                toast.geometry(f"{width}x{height}+{x}+{int(y)}")
                toast.attributes("-alpha", alpha)
            except Exception:
                return

            if alpha < 1.0 or y > target_y:
                alpha = min(1.0, alpha + 0.12)
                y = max(target_y, y - 8)
                parent.after(16, lambda: animate_step(alpha, y))
            else:
                schedule_auto_close()

        def schedule_auto_close():
            toast.bind("<Enter>", lambda e: cancel_auto_close())
            toast.bind("<Leave>", lambda e: schedule_again())
            record["auto_id"] = parent.after(4500, lambda: _close(False))

        def cancel_auto_close():
            aid = record.get("auto_id")
            if aid:
                parent.after_cancel(aid)
                record["auto_id"] = None

        def schedule_again():
            cancel_auto_close()
            record["auto_id"] = parent.after(2000, lambda: _close(False))

        def _close(user):
            # If user dismissed, cancel the reminder and remove from list (both repeating and non-repeating)
            if user:
                reminder.stop()
                self._remove_reminder_instance(reminder)
            else:
                # For auto-close, only remove non-repeating reminders (repeating ones should continue)
                if not getattr(reminder, "repeat", False):
                    reminder.stop()
                    self._remove_reminder_instance(reminder)
            cancel_auto_close()

            # Fade-out and slide-down
            def fade_out(alpha=1.0, y=target_y):
                try:
                    toast.attributes("-alpha", alpha)
                    toast.geometry(f"{width}x{height}+{x}+{int(y)}")
                except Exception:
                    return _cleanup()
                if alpha > 0.0:
                    alpha = max(0.0, alpha - 0.15)
                    y = y + 10
                    parent.after(16, lambda: fade_out(alpha, y))
                else:
                    _cleanup()

            def _cleanup():
                toast.destroy()
                if record in self._active_toasts:
                    idx = self._active_toasts.index(record)
                    self._active_toasts.pop(idx)
                    _restack(idx)

            fade_out()

        def _restack(start_idx):
            for i in range(start_idx, len(self._active_toasts)):
                rec = self._active_toasts[i]
                rec["target_y"] = rec["target_y"] + height + gap
                _animate_to(rec)

        def _animate_to(rec):
            tw = rec["win"]
            tx = rec["x"]
            ty = rec["target_y"]
            try:
                geo = tw.geometry()
                parts = geo.split("+")
                cy = int(parts[-1]) if len(parts) >= 3 else ty
            except Exception:
                return

            if cy < ty:
                ny = min(ty, cy + 12)
                try:
                    tw.geometry(f"{width}x{height}+{tx}+{int(ny)}")
                except Exception:
                    return
                parent.after(16, lambda: _animate_to(rec))
            else:
                tw.geometry(f"{width}x{height}+{tx}+{int(ty)}")

        animate_step()

    def _remove_reminder_instance(self, reminder_instance):
        try:
            idx = next(i for i, (r, _) in enumerate(self.reminders) if r is reminder_instance)
        except StopIteration:
            return
        
        # Stop and remove reminder
        reminder, _ = self.reminders[idx]
        reminder.stop()
        self.reminders.pop(idx)
        
        # Remove UI elements
        self.reminder_vars.pop(idx)
        checkbox = self.reminder_widgets.pop(idx)
        checkbox.destroy()
        
        self.update_delete_button_state()
        self.save_reminders()

    # --- UI helpers & persistence ---
    def _add_ui_row(self, display_text):
        var = tk.BooleanVar()
        cb = ctk.CTkCheckBox(
            self.reminder_list,
            text=display_text,
            variable=var,
            command=self.update_delete_button_state
        )
        cb.pack(side="top", anchor="w", padx=2, pady=4)
        self.reminder_vars.append(var)
        self.reminder_widgets.append(cb)

    def save_reminders(self):
        try:
            data = [{
                "message": r.message,
                "remind_time": r.remind_time.isoformat(),
                "repeat": r.repeat,
                "interval_minutes": int(r.interval.total_seconds() // 60) if r.repeat else 0,
            } for r, _ in self.reminders]
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_reminders(self):
        try:
            if not os.path.exists(self._storage_path):
                return
            with open(self._storage_path, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception:
            return

        now = datetime.now()
        for item in items:
            try:
                message = item.get("message", "")
                remind_time = datetime.fromisoformat(item.get("remind_time"))
                repeat = bool(item.get("repeat", False))
                interval_minutes = int(item.get("interval_minutes", 0))

                # Skip past non-repeating reminders
                if not repeat and remind_time <= now:
                    continue
                
                # Adjust repeating reminders to next occurrence
                if repeat and interval_minutes > 0:
                    while remind_time <= now:
                        remind_time += timedelta(minutes=interval_minutes)

                reminder = Reminder(message, remind_time, repeat, interval_minutes, self.show_reminder)
                reminder.start()

                display_text = f"{remind_time.strftime('%Y-%m-%d %H:%M')} | {message}"
                if repeat:
                    display_text += f" (every {interval_minutes} min)"

                self.reminders.append((reminder, display_text))
                self._add_ui_row(display_text)
            except Exception:
                continue

    def add_reminder(self):
        try:
            message = self.msg_entry.get()
            date_str = self.date_var.get().strip()
            hour = self.hour_var.get()
            minute = self.minute_var.get()
            minutes_str = self.minutes_entry.get().strip()
            repeat = self.repeat_var.get()
            interval_minutes = 0

            if not message.strip():
                messagebox.showwarning("Warning", "Please enter a reminder message.")
                return

            # Determine remind_time: use date+time if both are filled, else use minutes
            remind_time = None
            if date_str and hour and minute:
                try:
                    # Convert 12-hour format to 24-hour format
                    hour_int = int(hour)
                    if self.ampm_var.get() == "PM" and hour_int != 12:
                        hour_int += 12
                    elif self.ampm_var.get() == "AM" and hour_int == 12:
                        hour_int = 0
                    
                    remind_time = datetime.strptime(f"{date_str} {hour_int:02d}:{minute}", "%Y-%m-%d %H:%M")
                    if remind_time <= datetime.now():
                        messagebox.showwarning("Warning", "Please enter a future date and time.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid date or time format.")
                    return
            elif minutes_str:
                try:
                    minutes = int(minutes_str)
                    if minutes <= 0:
                        messagebox.showwarning("Warning", "Please enter a positive number of minutes.")
                        return
                    remind_time = datetime.now() + timedelta(minutes=minutes)
                except ValueError:  
                    messagebox.showerror("Error", "Please enter a valid number of minutes.")
                    return
            else:
                messagebox.showwarning("Warning", "Please enter either a date and time or minutes from now.")
                return

            if repeat:
                interval_text = self.repeat_interval_entry.get().strip()
                if not interval_text:
                    messagebox.showwarning("Warning", "Please enter a repeat interval in minutes.")
                    return
                try:
                    interval_minutes = int(interval_text)
                    if interval_minutes <= 0:
                        messagebox.showwarning("Warning", "Repeat interval must be a positive number.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Repeat interval must be a number.")
                    return

            reminder = Reminder(message, remind_time, repeat, interval_minutes, self.show_reminder)
            reminder.start()

            display_text = f"{remind_time.strftime('%Y-%m-%d %H:%M')} | {message}"
            if repeat:
                display_text += f" (every {interval_minutes} min)"

            self.reminders.append((reminder, display_text))
            self._add_ui_row(display_text)
            self.update_delete_button_state()
            self.save_reminders()

            # Clear inputs for convenience
            for entry in [self.msg_entry, self.minutes_entry, self.repeat_interval_entry]:
                entry.delete(0, "end")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def open_calendar(self):
        # Avoid multiple popups
        if hasattr(self, "_cal_win") and self._cal_win and self._cal_win.winfo_exists():
            self._cal_win.lift()
            return
        self._cal_win = ctk.CTkToplevel(self)
        self._cal_win.title("Select Date")
        self._cal_win.resizable(False, False)

        # Colors aligned with CustomTkinter dark theme
        colors = {
            "bg": "#1f1f1f", "fg": "#d6d6d6", "accent": "#1a2b4c", "sel": "#2f4b7a", "other": "#7a7a7a"
        }
        
        today = datetime.now().date()
        self._calendar = Calendar(
            self._cal_win, selectmode="day", year=today.year, month=today.month, day=today.day,
            date_pattern="yyyy-mm-dd", background=colors["bg"], disabledbackground=colors["bg"],
            bordercolor=colors["accent"], headersbackground=colors["bg"], normalbackground=colors["bg"],
            weekendbackground=colors["bg"], selectbackground=colors["sel"], foreground=colors["fg"],
            normalforeground=colors["fg"], headersforeground=colors["fg"], weekendforeground=colors["fg"],
            othermonthforeground=colors["other"], othermonthbackground=colors["bg"], othermonthwebackground=colors["bg"]
        )
        self._calendar.pack(padx=10, pady=(10, 6))

        btn_row = ctk.CTkFrame(self._cal_win)
        btn_row.pack(pady=(0, 10))
        ctk.CTkButton(btn_row, text="OK", command=self._on_calendar_ok, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Cancel", command=self._cal_win.destroy, width=80).pack(side="left", padx=5)

    def _on_calendar_ok(self):
        self.date_var.set(self._calendar.get_date())
        if hasattr(self, "_cal_win") and self._cal_win and self._cal_win.winfo_exists():
            self._cal_win.destroy()

    def _on_repeat_toggle(self):
        state = "normal" if self.repeat_var.get() else "disabled"
        self.repeat_interval_entry.configure(state=state)


    def update_delete_button_state(self):
        self.delete_btn.configure(state="normal" if any(var.get() for var in self.reminder_vars) else "disabled")

    def delete_selected_reminder(self):
        to_delete = [i for i, var in enumerate(self.reminder_vars) if var.get()]
        if not to_delete:
            messagebox.showwarning("Warning", "Please tick reminder(s) to delete.")
            return
        # Delete from highest index to lowest to avoid shifting issues
        for idx in sorted(to_delete, reverse=True):
            self.reminders[idx][0].stop()  # Stop reminder
            self.reminders.pop(idx)
            self.reminder_vars.pop(idx)
            self.reminder_widgets.pop(idx).destroy()  # Destroy widget
        self.update_delete_button_state()
        self.save_reminders()