import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import csv
from datetime import date

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT
)
""")

cursor.execute("SELECT * FROM users")
if not cursor.fetchall():
    cursor.execute("INSERT INTO users VALUES ('admin', 'admin')")
conn.commit()

def login():
    u = user_entry.get()
    p = pass_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    if cursor.fetchone():
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid login")

def open_dashboard():
    root = tk.Tk()
    root.title("Attendance System Dashboard")
    root.geometry("800x500")

    def refresh_students():
        listbox.delete(0, tk.END)
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            listbox.insert(tk.END, f"{row[0]} - {row[1]}")

    def add_student():
        name = student_entry.get()
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        student_entry.delete(0, tk.END)
        refresh_students()

    def mark(status):
        selected = listbox.get(tk.ACTIVE)
        if not selected:
            return

        student_id = selected.split(" - ")[0]
        today = str(date.today())

        cursor.execute(
            "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
            (student_id, today, status)
        )
        conn.commit()
        messagebox.showinfo("Success", f"Marked {status}")

    def show_stats():
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='P' AND date=?", (str(date.today()),))
        present = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='A' AND date=?", (str(date.today()),))
        absent = cursor.fetchone()[0]

        stats_label.config(
            text=f"Total: {total_students} | Present: {present} | Absent: {absent}"
        )

    def export_csv():
        cursor.execute("SELECT * FROM attendance")
        data = cursor.fetchall()

        with open("attendance_report.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Student_ID", "Date", "Status"])
            writer.writerows(data)

        messagebox.showinfo("Exported", "CSV file created!")

    tk.Label(root, text="Student Attendance System", font=("Arial", 18, "bold")).pack(pady=10)

    stats_label = tk.Label(root, text="Stats loading...", font=("Arial", 12))
    stats_label.pack()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    student_entry = tk.Entry(frame)
    student_entry.pack(side=tk.LEFT)

    tk.Button(frame, text="Add Student", command=add_student).pack(side=tk.LEFT, padx=5)

    listbox = tk.Listbox(root, width=40)
    listbox.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    tk.Button(btn_frame, text="Present", bg="lightgreen", command=lambda: mark("P")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Absent", bg="red", command=lambda: mark("A")).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text="Refresh", command=refresh_students).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Export CSV", command=export_csv).pack(side=tk.LEFT, padx=5)

    refresh_students()
    show_stats()

    root.mainloop()

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

tk.Label(login_window, text="Login", font=("Arial", 16)).pack(pady=10)

user_entry = tk.Entry(login_window)
user_entry.pack()
user_entry.insert(0, "admin")

pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()
pass_entry.insert(0, "admin")

tk.Button(login_window, text="Login", command=login).pack(pady=10)

login_window.mainloop()
