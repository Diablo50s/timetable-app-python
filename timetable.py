# Timetable + Attendance + Marks GUI App - Fully Updated

import csv
import os
from datetime import datetime, timedelta
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# --- CONFIGURATION ---
class Config:
    """Class to hold all application constants."""
    FILENAME = "timetable.csv"
    ATTENDANCE_FILE = "attendance.csv"
    MARKS_FILE = "marks.csv"
    PERIODS = 9
    START_TIME = datetime.strptime("09:00 AM", "%I:%M %p")
    SLOT_DURATION = timedelta(minutes=55)
    BREAK_START = datetime.strptime("01:35 PM", "%I:%M %p")
    BREAK_END = datetime.strptime("02:30 PM", "%I:%M %p")
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    @staticmethod
    def generate_time_slots() -> list[str]:
        """Generate time slots while skipping the break."""
        time_slots = []
        t = Config.START_TIME
        while len(time_slots) < Config.PERIODS:
            if Config.BREAK_START <= t < Config.BREAK_END:
                t = Config.BREAK_END
            time_slots.append(t.strftime("%I:%M %p"))
            t += Config.SLOT_DURATION
        return time_slots

# --- MAIN APPLICATION CLASS ---
class TimetableApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Timetable, Attendance & Marks Manager")
        self.geometry("1000x650")
        
        self.time_slots = Config.generate_time_slots()
        
        # Initialize notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        # Frames for each tab
        self.frame_add_class = ttk.Frame(self.notebook)
        self.frame_timetable = ttk.Frame(self.notebook)
        self.frame_mark_attendance = ttk.Frame(self.notebook)
        self.frame_attendance_summary = ttk.Frame(self.notebook)
        self.frame_add_marks = ttk.Frame(self.notebook)
        self.frame_view_marks = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_add_class, text="Add Class")
        self.notebook.add(self.frame_timetable, text="Timetable")
        self.notebook.add(self.frame_mark_attendance, text="Mark Attendance")
        self.notebook.add(self.frame_attendance_summary, text="Attendance Summary")
        self.notebook.add(self.frame_add_marks, text="Add Marks")
        self.notebook.add(self.frame_view_marks, text="View Marks")

        # Setup GUI for each tab
        self.setup_add_class_tab()
        self.setup_timetable_tab()
        self.setup_attendance_tab()
        self.setup_attendance_summary_tab()
        self.setup_marks_tab()
        self.setup_view_marks_tab()

    # --- Utility Functions ---
    def get_subjects(self) -> list[str]:
        """Get a sorted list of all subjects from the timetable file."""
        subjects = set()
        if os.path.exists(Config.FILENAME):
            with open(Config.FILENAME, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subjects.add(row["Subject"])
        return sorted(subjects)

    # --- GUI Setup for Tabs ---
    def setup_add_class_tab(self):
        """Builds the GUI for the 'Add Class' tab."""
        ttk.Label(self.frame_add_class, text="Select Day:").pack(pady=(10, 0))
        self.day_var = ttk.StringVar(value=Config.DAYS[0])
        ttk.Combobox(self.frame_add_class, textvariable=self.day_var, values=Config.DAYS, state="readonly").pack(pady=5)

        self.hour_var, self.minute_var, self.ampm_var = ttk.StringVar(value="09"), ttk.StringVar(value="00"), ttk.StringVar(value="AM")
        ttk.Label(self.frame_add_class, text="Time:").pack()
        time_frame = ttk.Frame(self.frame_add_class)
        time_frame.pack()
        ttk.Combobox(time_frame, textvariable=self.hour_var, values=[f"{h:02}" for h in range(1, 13)], width=5, state="readonly").pack(side="left")
        ttk.Combobox(time_frame, textvariable=self.minute_var, values=[f"{m:02}" for m in range(0, 60, 5)], width=5, state="readonly").pack(side="left")
        ttk.Combobox(time_frame, textvariable=self.ampm_var, values=["AM", "PM"], width=5, state="readonly").pack(side="left")

        self.subject_entry = ttk.Entry(self.frame_add_class)
        ttk.Label(self.frame_add_class, text="Subject:").pack(pady=(10, 0))
        self.subject_entry.pack(pady=5)
        ttk.Button(self.frame_add_class, text="Save", command=self.save_class_entry, bootstyle="success").pack(pady=10)
    
    def setup_timetable_tab(self):
        """Builds the GUI for the 'Timetable' tab."""
        self.populate_timetable_grid()
    
    def setup_attendance_tab(self):
        """Builds the GUI for the 'Mark Attendance' tab."""
        self.mark_attendance_ui()
    
    def setup_attendance_summary_tab(self):
        """Builds the GUI for the 'Attendance Summary' tab."""
        self.show_attendance_summary()
    
    def setup_marks_tab(self):
        """Builds the GUI for the 'Add Marks' tab."""
        self.frame_add_marks.grid_columnconfigure(0, weight=1)
        self.frame_add_marks.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self.frame_add_marks, text="Subject:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.marks_subject_dropdown = ttk.Combobox(self.frame_add_marks, state="readonly")
        self.marks_subject_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.update_marks_subjects()
        
        ttk.Label(self.frame_add_marks, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.marks_type_entry = ttk.Entry(self.frame_add_marks)
        self.marks_type_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.frame_add_marks, text="Obtained:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.marks_obtained_entry = ttk.Entry(self.frame_add_marks)
        self.marks_obtained_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.frame_add_marks, text="Total:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.marks_total_entry = ttk.Entry(self.frame_add_marks)
        self.marks_total_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        btn_frame = ttk.Frame(self.frame_add_marks)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save Marks", command=self.save_marks, bootstyle="success").pack()

    def setup_view_marks_tab(self):
        """Builds the GUI for the 'View Marks' tab."""
        self.view_marks()

    # --- Core Logic Functions ---
    def save_class_entry(self):
        """Saves a timetable entry to the CSV file."""
        day = self.day_var.get()
        time = f"{self.hour_var.get()}:{self.minute_var.get()} {self.ampm_var.get()}"
        subject = self.subject_entry.get().strip().title()

        if not subject:
            messagebox.showerror("Missing Subject", "Please enter a subject.")
            return

        try:
            datetime.strptime(time, "%I:%M %p")
        except ValueError:
            messagebox.showerror("Invalid Time", "Invalid time format.")
            return

        rows = []
        updated = False
        if os.path.exists(Config.FILENAME):
            with open(Config.FILENAME, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        for row in rows:
            if row["Day"] == day and row["Time"] == time:
                if messagebox.askyesno("Update Entry", f"Class at {time} on {day} already exists. Overwrite?"):
                    row["Subject"] = subject
                    updated = True
                else:
                    return
                break
        
        if not updated:
            rows.append({"Day": day, "Time": time, "Subject": subject})

        fieldnames = ["Day", "Time", "Subject"]
        with open(Config.FILENAME, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        messagebox.showinfo("Saved", f"{day} | {time} | {subject} -> {'Updated' if updated else 'Added'}!")
        self.subject_entry.delete(0, "end")
        self.populate_timetable_grid()
        self.update_marks_subjects()
        self.show_attendance_summary()
        self.view_marks()

    def populate_timetable_grid(self):
        """Populates the timetable grid on the GUI."""
        for widget in self.frame_timetable.winfo_children():
            widget.destroy()

        grid = {day: {slot: "" for slot in self.time_slots} for day in Config.DAYS}
        if os.path.exists(Config.FILENAME):
            with open(Config.FILENAME, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    d, t, s = row["Day"], row["Time"], row["Subject"]
                    if d in grid and t in grid[d]:
                        grid[d][t] = s

        # Headers
        ttk.Label(self.frame_timetable, text="", width=12).grid(row=0, column=0)
        for col, time in enumerate(self.time_slots, start=1):
            ttk.Label(self.frame_timetable, text=time, width=12, anchor="center", bootstyle="secondary").grid(row=0, column=col)
        
        # Grid content
        for row_idx, day in enumerate(Config.DAYS, start=1):
            ttk.Label(self.frame_timetable, text=day, width=12, anchor="center", bootstyle="success").grid(row=row_idx, column=0)
            for col_idx, time in enumerate(self.time_slots, start=1):
                sub = grid[day][time]
                ttk.Label(self.frame_timetable, text=sub, width=12, anchor="center", bootstyle="info").grid(row=row_idx, column=col_idx)

    def save_attendance(self, date: str, day: str, time: str, subject: str, status: str):
        """Saves an attendance record to the CSV file."""
        if os.path.exists(Config.ATTENDANCE_FILE):
            with open(Config.ATTENDANCE_FILE, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Date"] == date and row["Day"] == day and row["Time"] == time and row["Subject"] == subject:
                        messagebox.showinfo("Already Marked", "Attendance for this class has already been recorded.")
                        return

        fieldnames = ["Date", "Day", "Time", "Subject", "Status"]
        write_header = not os.path.exists(Config.ATTENDANCE_FILE) or os.stat(Config.ATTENDANCE_FILE).st_size == 0
        with open(Config.ATTENDANCE_FILE, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow({"Date": date, "Day": day, "Time": time, "Subject": subject, "Status": status})
            messagebox.showinfo("Success", f"Attendance for {subject} marked as {status}.")
        self.show_attendance_summary()
        self.mark_attendance_ui()

    def mark_attendance_ui(self):
        """Builds the 'Mark Attendance' GUI and refreshes class lists."""
        for widget in self.frame_mark_attendance.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_mark_attendance, text="Select Date (YYYY-MM-DD):").pack(pady=5)
        self.date_var = ttk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(self.frame_mark_attendance, textvariable=self.date_var)
        date_entry.pack(pady=5)

        ttk.Button(self.frame_mark_attendance, text="Show Classes", command=self.refresh_classes_for_attendance).pack(pady=5)
        self.classes_frame = ttk.Frame(self.frame_mark_attendance)
        self.classes_frame.pack()
        self.refresh_classes_for_attendance()

    def refresh_classes_for_attendance(self):
        """Refreshes the list of classes for the selected date."""
        for w in self.classes_frame.winfo_children():
            w.destroy()
        
        try:
            selected_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            ttk.Label(self.classes_frame, text="Invalid date format. Use YYYY-MM-DD").pack()
            return
        
        selected_day = selected_date.strftime("%A")
        class_list = []
        if os.path.exists(Config.FILENAME):
            with open(Config.FILENAME, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Day"] == selected_day:
                        class_list.append((row["Time"], row["Subject"]))
        
        if not class_list:
            ttk.Label(self.classes_frame, text=f"No classes on {selected_day}.").pack()
            return
            
        for idx, (time, subject) in enumerate(class_list):
            ttk.Label(self.classes_frame, text=f"{time} - {subject}").grid(row=idx, column=0, padx=5, pady=5)
            
            # Use lambda with keyword arguments for clarity
            ttk.Button(self.classes_frame, text="✔ Present", bootstyle="success",
                       command=lambda t=time, s=subject: self.save_attendance(self.date_var.get(), selected_day, t, s, "Present")
                       ).grid(row=idx, column=1)
            
            ttk.Button(self.classes_frame, text="✘ Absent", bootstyle="danger",
                       command=lambda t=time, s=subject: self.save_attendance(self.date_var.get(), selected_day, t, s, "Absent")
                       ).grid(row=idx, column=2)

    def show_attendance_summary(self):
        """Displays the attendance summary on the GUI."""
        for widget in self.frame_attendance_summary.winfo_children():
            widget.destroy()

        subject_counts = {}
        if not os.path.exists(Config.ATTENDANCE_FILE):
            ttk.Label(self.frame_attendance_summary, text="No attendance records found.").pack()
            return
        
        with open(Config.ATTENDANCE_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                subject = row["Subject"]
                status = row["Status"]
                if subject not in subject_counts:
                    subject_counts[subject] = {"Present": 0, "Total": 0}
                if status == "Present":
                    subject_counts[subject]["Present"] += 1
                subject_counts[subject]["Total"] += 1

        ttk.Label(self.frame_attendance_summary, text="Subject", width=20, bootstyle="secondary").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.frame_attendance_summary, text="Attendance", width=15, bootstyle="secondary").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.frame_attendance_summary, text="Percentage", width=15, bootstyle="secondary").grid(row=0, column=2, padx=5, pady=5)

        for i, (sub, count) in enumerate(subject_counts.items(), start=1):
            percent = round((count['Present'] / count['Total']) * 100, 1) if count['Total'] else 0
            ttk.Label(self.frame_attendance_summary, text=sub).grid(row=i, column=0, padx=5, pady=5)
            ttk.Label(self.frame_attendance_summary, text=f"{count['Present']}/{count['Total']}").grid(row=i, column=1, padx=5, pady=5)
            ttk.Label(self.frame_attendance_summary, text=f"{percent}%").grid(row=i, column=2, padx=5, pady=5)

    def save_marks(self):
        """Saves a marks entry to the CSV file."""
        sub = self.marks_subject_dropdown.get().strip().title()
        mtype = self.marks_type_entry.get().strip().title()
        obtained = self.marks_obtained_entry.get().strip()
        total = self.marks_total_entry.get().strip()

        if not (sub and mtype and obtained and total):
            messagebox.showerror("Error", "Fill all fields")
            return
        
        try:
            obtained = int(obtained)
            total = int(total)
            if obtained > total:
                messagebox.showerror("Error", "Obtained marks cannot be greater than total marks.")
                return
        except ValueError:
            messagebox.showerror("Error", "Marks must be valid numbers.")
            return

        fieldnames = ["Subject", "Type", "Obtained", "Total"]
        write_header = not os.path.exists(Config.MARKS_FILE) or os.stat(Config.MARKS_FILE).st_size == 0
        with open(Config.MARKS_FILE, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow({"Subject": sub, "Type": mtype, "Obtained": obtained, "Total": total})
        
        messagebox.showinfo("Saved", f"Marks saved for {sub} - {mtype}.")
        self.marks_subject_dropdown.set("")
        self.marks_type_entry.delete(0, "end")
        self.marks_obtained_entry.delete(0, "end")
        self.marks_total_entry.delete(0, "end")
        self.view_marks()

    def view_marks(self):
        """Displays all marks records on the GUI."""
        for widget in self.frame_view_marks.winfo_children():
            widget.destroy()
        
        if not os.path.exists(Config.MARKS_FILE):
            ttk.Label(self.frame_view_marks, text="No marks data found.").pack()
            return
            
        with open(Config.MARKS_FILE, newline='') as f:
            reader = csv.DictReader(f)
            
            # Create a reusable header function to avoid repetition
            def create_header(frame, headers):
                for col_idx, header in enumerate(headers):
                    ttk.Label(frame, text=header, width=15, bootstyle="secondary").grid(row=0, column=col_idx, padx=5, pady=5)

            headers = ["Subject", "Type", "Obtained", "Total"]
            create_header(self.frame_view_marks, headers)

            for i, row in enumerate(reader, start=1):
                ttk.Label(self.frame_view_marks, text=row["Subject"]).grid(row=i, column=0, padx=5, pady=5)
                ttk.Label(self.frame_view_marks, text=row["Type"]).grid(row=i, column=1, padx=5, pady=5)
                ttk.Label(self.frame_view_marks, text=row["Obtained"]).grid(row=i, column=2, padx=5, pady=5)
                ttk.Label(self.frame_view_marks, text=row["Total"]).grid(row=i, column=3, padx=5, pady=5)
                
    def update_marks_subjects(self):
        """Updates the subjects dropdown for the marks tab."""
        subjects = self.get_subjects()
        self.marks_subject_dropdown["values"] = subjects
        if subjects:
            self.marks_subject_dropdown.set(subjects[0])

# --- Main Entry Point ---
if __name__ == "__main__":
    app = TimetableApp()
    app.mainloop()
