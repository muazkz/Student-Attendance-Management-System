from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ================= INITIALIZE DATABASE =================
conn = sqlite3.connect("school_attendance.db")
c = conn.cursor()

# Jadual 1: Senarai Induk Pelajar
c.execute("""
CREATE TABLE IF NOT EXISTS students(
    student_id TEXT PRIMARY KEY,
    student_name TEXT
)
""")

# Jadual 2: Rekod Kehadiran Harian
c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    student_id TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
)
""")
conn.commit()


# ================= FUNCTIONS: TAB 1 (MANAGE STUDENTS) =================
def add_student():
    s_id = txt_stu_id.get().strip()
    name = txt_stu_name.get().strip()

    if not s_id or not name:
        messagebox.showerror("Error", "Please fill in both Student ID and Name")
        return

    try:
        c.execute("INSERT INTO students VALUES (?, ?)", (s_id, name))
        conn.commit()
        messagebox.showinfo("Success", f"Added {name} to the class roster.")
        txt_stu_id.delete(0, END)
        txt_stu_name.delete(0, END)
        show_students_roster()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Student ID '{s_id}' already exists!")


def delete_student():
    selected = tree_students.focus()
    if not selected:
        messagebox.showwarning("Warning", "Select a student from the roster to delete")
        return
    
    values = tree_students.item(selected, "values")
    s_id, name = values[0], values[1]

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?\nThis will also remove their past attendance records."):
        c.execute("DELETE FROM students WHERE student_id=?", (s_id,))
        c.execute("DELETE FROM attendance WHERE student_id=?", (s_id,))
        conn.commit()
        messagebox.showinfo("Deleted", "Student removed successfully.")
        show_students_roster()


def show_students_roster():
    tree_students.delete(*tree_students.get_children())
    c.execute("SELECT * FROM students ORDER BY student_id")
    for row in c.fetchall():
        tree_students.insert("", END, values=row)


# ================= FUNCTIONS: TAB 2 (TAKE ATTENDANCE) =================
def calculate_percentage():
    selected_date = txt_date.get().strip()
    
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (selected_date,))
    present = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Absent'", (selected_date,))
    absent = c.fetchone()[0]
    
    percentage = (present / total_students) * 100 if total_students > 0 and (present + absent) > 0 else 0.0

    lbl_total.config(text=f"Total Class Size: {total_students}")
    lbl_present.config(text=f"Present Today: {present}")
    lbl_absent.config(text=f"Absent Today: {absent}")
    lbl_percentage.config(text=f"Attendance Rate: {percentage:.2f}%")


def load_attendance_by_date():
    selected_date = txt_date.get().strip()
    if not selected_date:
        messagebox.showwarning("Warning", "Please enter a valid date")
        return

    tree_attendance.delete(*tree_attendance.get_children())
    
    # Semak jika kehadiran untuk tarikh ini sudah wujud
    c.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (selected_date,))
    exists = c.fetchone()[0]
    
    if exists == 0:
        # Jika hari baru, bawa masuk senarai pelajar terkini dari Tab 1 (Default: Present)
        c.execute("SELECT student_id, student_name FROM students ORDER BY student_id")
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Roster Empty", "Please register students in Tab 1 first!")
            return
        for row in rows:
            tree_attendance.insert("", END, values=(row[0], row[1], "Present", "New Record"))
    else:
        # Jika rekod tarikh ini sudah ada, paparkan data lama untuk diedit/disemak
        c.execute("""
            SELECT s.student_id, s.student_name, a.status, a.id 
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            WHERE a.date = ? ORDER BY s.student_id
        """, (selected_date,))
        for row in c.fetchall():
            tree_attendance.insert("", END, values=row)
            
    calculate_percentage()


def toggle_status(new_status):
    selected_item = tree_attendance.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a student from the table first")
        return
        
    current_values = list(tree_attendance.item(selected_item, "values"))
    current_values[2] = new_status  # Ubah status ruangan indeks ke-2
    tree_attendance.item(selected_item, values=current_values)


def save_attendance():
    selected_date = txt_date.get().strip()
    items = tree_attendance.get_children()
    
    if not items:
        messagebox.showwarning("Warning", "No data to save. Load a date first.")
        return

    for item in items:
        values = tree_attendance.item(item, "values")
        student_id, status, record_type = values[0], values[2], values[3]

        if record_type == "New Record":
            c.execute("INSERT INTO attendance (date, student_id, status) VALUES (?, ?, ?)", 
                      (selected_date, student_id, status))
        else:
            c.execute("UPDATE attendance SET status = ? WHERE id = ?", (status, record_type))
            
    conn.commit()
    messagebox.showinfo("Success", f"Attendance roster for {selected_date} saved!")
    load_attendance_by_date()


# ================= GLOBAL CONFIGS =================
def change_theme(color):
    root.config(bg=color)
    title.config(bg=color)
    style.configure("TNotebook", background=color)
    style.configure("TFrame", background=color)


def on_closing():
    conn.close()
    root.destroy()


# ================= GUI RECONSTRUCTION =================
root = Tk()
root.title("Advanced Student Roster & Attendance System")
root.geometry("1000x700")
root.config(bg="lightblue")

style = ttk.Style()
style.theme_use("clam")

# Main Header
title = Label(root, text="STUDENT ROSTER & ATTENDANCE MANAGEMENT", font=("Arial", 16, "bold"), bg="lightblue", pady=10)
title.pack()

# Theme Buttons
theme_frame = Frame(root)
theme_frame.pack(pady=5)
themes = [("Blue", "lightblue"), ("Green", "lightgreen"), ("Pink", "pink"), ("White", "white")]
for i, (text, col) in enumerate(themes):
    Button(theme_frame, text=text, command=lambda c=col: change_theme(c)).grid(row=0, column=i, padx=5)

# TABS CONTROLLER (NOTEBOOK)
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=15, pady=10)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="  1. Manage Class Roster (Daftar Pelajar)  ")
notebook.add(tab2, text="  2. Take Daily Attendance (Ambil Kehadiran)  ")


# ================= TAB 1 DESIGN: MANAGE STUDENTS =================
frame_inputs = Frame(tab1, pady=10)
frame_inputs.pack()

Label(frame_inputs, text="Student ID:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=E)
txt_stu_id = Entry(frame_inputs, width=20, font=("Arial", 10))
txt_stu_id.grid(row=0, column=1, padx=5, pady=5)

Label(frame_inputs, text="Full Name:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky=E)
txt_stu_name = Entry(frame_inputs, width=35, font=("Arial", 10))
txt_stu_name.grid(row=1, column=1, padx=5, pady=5)

btn_add = Button(frame_inputs, text="Add New Student", bg="green", fg="white", font=("Arial", 10, "bold"), command=add_student)
btn_add.grid(row=2, column=0, columnspan=2, pady=10, ipady=3, sticky=EW)

btn_delete = Button(frame_inputs, text="Remove Selected Student", bg="red", fg="white", font=("Arial", 10), command=delete_student)
btn_delete.grid(row=3, column=0, columnspan=2, sticky=EW)

# Tab 1 Table (Roster)
tree_students = ttk.Treeview(tab1, columns=("ID", "Name"), show="headings")
tree_students.heading("ID", text="Student ID")
tree_students.heading("Name", text="Student Name")
tree_students.column("ID", width=200, anchor=CENTER)
tree_students.column("Name", width=500, anchor=W)
tree_students.pack(fill=BOTH, expand=True, padx=20, pady=15)


# ================= TAB 2 DESIGN: TAKE ATTENDANCE =================
frame_date = Frame(tab2, pady=10)
frame_date.pack()

Label(frame_date, text="Select Date (YYYY-MM-DD):", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)
txt_date = Entry(frame_date, font=("Arial", 11), width=15, justify=CENTER)
txt_date.insert(0, datetime.today().strftime('%Y-%m-%d'))  # Auto-load tarikh hari ini
txt_date.grid(row=0, column=1, padx=5)

Button(frame_date, text="Load / Refresh Date", bg="blue", fg="white", font=("Arial", 10, "bold"), command=load_attendance_by_date).grid(row=0, column=2, padx=10)

# Attendance Status Toggles
frame_ctrl = Frame(tab2, pady=5)
frame_ctrl.pack()

Button(frame_ctrl, text="MARK PRESENT", bg="darkgreen", fg="white", width=15, font=("Arial", 10, "bold"), command=lambda: toggle_status("Present")).grid(row=0, column=0, padx=5)
Button(frame_ctrl, text="MARK ABSENT", bg="darkred", fg="white", width=15, font=("Arial", 10, "bold"), command=lambda: toggle_status("Absent")).grid(row=0, column=1, padx=5)
Button(frame_ctrl, text="💾 SAVE ATTENDANCE", bg="orange", fg="black", width=22, font=("Arial", 10, "bold"), command=save_attendance).grid(row=0, column=2, padx=15)

# Stats Tracker
frame_stats = Frame(tab2)
frame_stats.pack(pady=5)
lbl_total = Label(frame_stats, text="Total Class Size: 0", font=("Arial", 10, "bold"))
lbl_total.grid(row=0, column=0, padx=15)
lbl_present = Label(frame_stats, text="Present Today: 0", font=("Arial", 10, "bold"), fg="green")
lbl_present.grid(row=0, column=1, padx=15)
lbl_absent = Label(frame_stats, text="Absent Today: 0", font=("Arial", 10, "bold"), fg="red")
lbl_absent.grid(row=0, column=2, padx=15)
lbl_percentage = Label(tab2, text="Attendance Rate: 0.00%", font=("Arial", 11, "bold"))
lbl_percentage.pack(pady=2)

# Tab 2 Table (Daily Checker)
tree_attendance = ttk.Treeview(tab2, columns=("ID", "Name", "Status", "SysID"), show="headings")
tree_attendance.heading("ID", text="Student ID")
tree_attendance.heading("Name", text="Student Name")
tree_attendance.heading("Status", text="Attendance Status")
tree_attendance.heading("SysID", text="Record Database Key")

tree_attendance.column("ID", width=150, anchor=CENTER)
tree_attendance.column("Name", width=350, anchor=W)
tree_attendance.column("Status", width=150, anchor=CENTER)
tree_attendance.column("SysID", width=120, anchor=CENTER)
tree_attendance.pack(fill=BOTH, expand=True, padx=20, pady=10)


# ================= START APPLICATION =================
show_students_roster()
load_attendance_by_date()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
