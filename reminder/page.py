import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
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

    def start(self):
        def run():
            while not self._stop_event.is_set():
                now = datetime.now()
                if now >= self.remind_time:
                    if self.callback:
                        self.callback(self.message)
                    else:
                        messagebox.showinfo("⏰ Reminder", self.message)
                    if self.repeat:
                        self.remind_time += self.interval
                    else:
                        break
                time.sleep(10)
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()

class ReminderPage(ctk.CTkFrame):
    """
    The main page for setting reminders.
    """
    def __init__(self, parent):
        super().__init__(parent)

        # Create a canvas and a vertical scrollbar for scrolling
        canvas = tk.Canvas(self, borderwidth=0, background="#f8f8f8", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ctk.CTkLabel(
            self.scrollable_frame,
            text="⏰ Simple Reminder App",
            font=("Helvetica", 18, "bold"),
        ).pack(pady=10)

        # Reminder message input
        ctk.CTkLabel(self.scrollable_frame, text="Reminder Message:").pack()
        self.msg_entry = ctk.CTkEntry(self.scrollable_frame, width=300)
        self.msg_entry.pack(pady=5)

        # Date picker
        ctk.CTkLabel(self.scrollable_frame, text="Date:").pack()
        self.date_entry = DateEntry(self.scrollable_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(pady=5)

        # Time picker (hour and minute comboboxes)
        ctk.CTkLabel(self.scrollable_frame, text="Time:").pack()
        time_frame = ctk.CTkFrame(self.scrollable_frame)
        time_frame.pack(pady=5)
        self.hour_var = tk.StringVar(value="08")
        self.minute_var = tk.StringVar(value="00")
        self.hour_box = ttk.Combobox(time_frame, textvariable=self.hour_var, width=3, values=[f"{i:02d}" for i in range(24)])
        self.hour_box.pack(side="left")
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        self.minute_box = ttk.Combobox(time_frame, textvariable=self.minute_var, width=3, values=[f"{i:02d}" for i in range(60)])
        self.minute_box.pack(side="left")

        # Remind after (minutes) input
        ctk.CTkLabel(self.scrollable_frame, text="Remind After (minutes):").pack()
        self.minutes_entry = ctk.CTkEntry(self.scrollable_frame, width=100)
        self.minutes_entry.pack(pady=5)

        # Repeat checkbox and interval
        self.repeat_var = tk.BooleanVar()
        repeat_frame = ctk.CTkFrame(self.scrollable_frame)
        repeat_frame.pack(pady=5)
        ctk.CTkCheckBox(repeat_frame, text="Repeat", variable=self.repeat_var).pack(side="left")
        ctk.CTkLabel(repeat_frame, text="every").pack(side="left", padx=(10, 0))
        self.repeat_interval_entry = ctk.CTkEntry(repeat_frame, width=60)
        self.repeat_interval_entry.pack(side="left", padx=5)
        ctk.CTkLabel(repeat_frame, text="minutes").pack(side="left")

        # Add Reminder button
        ctk.CTkButton(self.scrollable_frame, text="Set Reminder", command=self.add_reminder).pack(pady=10)

        # Listbox for reminders
        ctk.CTkLabel(self.scrollable_frame, text="Your Reminders:").pack()
        self.reminder_listbox = tk.Listbox(
            self.scrollable_frame,
            width=60,
            height=8,
            activestyle="dotbox",
            selectbackground="#ffcccc",  # pink highlight
            bg="#f0f0f0",               # light gray background
            fg="#555555"                # dark gray text
        )
        self.reminder_listbox.pack(pady=5)
        self.reminder_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.delete_info_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Select a reminder and click Delete to remove it.",
            text_color="#888888",
            font=("Helvetica", 10, "italic")
        )
        self.delete_info_label.pack()

        self.delete_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="Delete Selected",
            command=self.delete_selected_reminder,
            state="disabled"
        )
        self.delete_btn.pack(pady=5)

        # Store reminders as tuples: (Reminder instance, display_text)
        self.reminders = []

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def show_reminder(self, message):
        self.after(0, lambda: messagebox.showinfo("⏰ Reminder", message))

    def add_reminder(self):
        try:
            message = self.msg_entry.get()
            date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
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
                    remind_time = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")    
                except ValueError:
                    messagebox.showerror("Error", "Invalid date or time format.")
                    return
                if remind_time <= datetime.now():
                    messagebox.showwarning("Warning", "Please enter a future date and time.")
                    return
            elif minutes_str:
                try:
                    minutes = int(minutes_str)
                except ValueError:  
                    messagebox.showerror("Error", "Please enter a valid number of minutes.")
                    return
                if minutes <= 0:
                    messagebox.showwarning("Warning", "Please enter a positive number of minutes.")
                    return
                remind_time = datetime.now() + timedelta(minutes=minutes)
            else:
                messagebox.showwarning("Warning", "Please enter either a date and time or minutes from now.")
                return

            if repeat:
                interval_text = self.repeat_interval_entry.get()
                if not interval_text.strip():
                    messagebox.showwarning("Warning", "Please enter a repeat interval in minutes.")
                    return
                try:
                    interval_minutes = int(interval_text)
                except ValueError:
                    messagebox.showerror("Error", "Repeat interval must be a number.")
                    return
                if interval_minutes <= 0:
                    messagebox.showwarning("Warning", "Repeat interval must be a positive number.")
                    return

            reminder = Reminder(
                message,
                remind_time,
                repeat,
                interval_minutes=interval_minutes if repeat else 0,
                callback=self.show_reminder
            )
            reminder.start()

            # Add to list and listbox
            display_text = f"{remind_time.strftime('%Y-%m-%d %H:%M')} | {message}"
            if repeat:
                display_text += f" (every {interval_minutes} min)"
            self.reminders.append((reminder, display_text))
            self.reminder_listbox.insert("end", display_text)

            if repeat:
                messagebox.showinfo("Success", f"Repeating reminder set for {remind_time.strftime('%Y-%m-%d %H:%M')} every {interval_minutes} minute(s)!")
            else:
                messagebox.showinfo("Success", f"Reminder set for {remind_time.strftime('%Y-%m-%d %H:%M')}!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def on_listbox_select(self, event):
        # Enable delete button only if something is selected
        if self.reminder_listbox.curselection():
            self.delete_btn.configure(state="normal")
        else:
            self.delete_btn.configure(state="disabled")

    def delete_selected_reminder(self):
        selection = self.reminder_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a reminder to delete.")
            return
        idx = selection[0]
        reminder, display_text = self.reminders[idx]
        # Confirmation dialog
        confirm = messagebox.askyesno("Delete Reminder", f"Are you sure you want to delete this reminder?\n\n{display_text}")
        if not confirm:
            return
        reminder.stop()
        self.reminder_listbox.delete(idx)   
        self.reminders.pop(idx)
        self.delete_btn.configure(state="disabled")