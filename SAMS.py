import os
import sqlite3
import csv
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Management System")
        self.root.geometry("1150x720")
        self.root.config(bg="#f4f6f9")
        
        self.db_name = "attendance.db"
        self.selected_photo_path = "" 
        self.init_database()

        # Configure TTK styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=35, font=("Arial", 10)) 
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#d1d8e0")
        
        # ================= TITLE BANNER =================
        title_frame = Frame(self.root, bg="#4b7bec", height=70)
        title_frame.pack(fill=X, side=TOP)
        title_frame.pack_propagate(False)
        
        Label(
            title_frame, 
            text="⚡ STUDENT ATTENDANCE MANAGEMENT SYSTEM (CLICK ROW FOR PHOTO POPUP)", 
            font=("Arial", 18, "bold"), 
            fg="white", 
            bg="#4b7bec"
        ).pack(side=LEFT, padx=20, pady=15)

        # ================= MAIN CONTENT SPLIT =================
        main_body = Frame(self.root, bg="#f4f6f9")
        main_body.pack(fill=BOTH, expand=True, padx=20, pady=15)

        # Left Column: Controls (Inputs, Photo Upload & Search)
        left_panel = Frame(main_body, bg="#f4f6f9", width=420)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Right Column: Records, Stats & Treeview Grid
        right_panel = Frame(main_body, bg="#f4f6f9")
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        # ================= 1. INPUT FORM FRAME =================
        form_frame = LabelFrame(left_panel, text=" Attendance Logging ", font=("Arial", 10, "bold"), bg="white", bd=2, relief=GROOVE)
        form_frame.pack(fill=X, pady=(0, 15), ipady=10)

        Label(form_frame, text="Student ID *", bg="white", font=("Arial", 10)).grid(row=0, column=0, padx=15, pady=8, sticky=W)
        self.txt_id = Entry(form_frame, font=("Arial", 10), width=22)
        self.txt_id.grid(row=0, column=1, padx=10, pady=8)

        Label(form_frame, text="Student Name *", bg="white", font=("Arial", 10)).grid(row=1, column=0, padx=15, pady=8, sticky=W)
        self.txt_name = Entry(form_frame, font=("Arial", 10), width=22)
        self.txt_name.grid(row=1, column=1, padx=10, pady=8)

        Label(form_frame, text="Status", bg="white", font=("Arial", 10)).grid(row=2, column=0, padx=15, pady=8, sticky=W)
        self.status_var = StringVar(value="Present")
        status_options = ["Present", "Absent", "Late", "Excused"]
        status_menu = ttk.OptionMenu(form_frame, self.status_var, status_options[0], *status_options)
        status_menu.grid(row=2, column=1, padx=10, pady=8, sticky=EW)

        # Photo selection row
        Label(form_frame, text="Photo ID", bg="white", font=("Arial", 10)).grid(row=3, column=0, padx=15, pady=8, sticky=W)
        photo_btn_frame = Frame(form_frame, bg="white")
        photo_btn_frame.grid(row=3, column=1, padx=10, pady=8, sticky=W)
        
        Button(photo_btn_frame, text="Choose File (PNG/GIF)...", font=("Arial", 9), bg="#d1d8e0", bd=1, command=self.upload_photo).pack(side=LEFT)
        self.lbl_photo_status = Label(photo_btn_frame, text="No image selected", font=("Arial", 9, "italic"), bg="white", fg="gray")
        self.lbl_photo_status.pack(side=LEFT, padx=5)

        # Form Buttons
        btn_frame = Frame(form_frame, bg="white")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        Button(btn_frame, text="Log Attendance", bg="#20bf6b", fg="white", font=("Arial", 10, "bold"), width=15, bd=0, pady=6, command=self.add_record).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Clear Entry", bg="#a5b1c2", fg="black", font=("Arial", 10), width=10, bd=0, pady=6, command=self.clear_fields).pack(side=LEFT, padx=5)

        # ================= 2. SEARCH & FILTER FRAME =================
        search_frame = LabelFrame(left_panel, text=" View Filters ", font=("Arial", 10, "bold"), bg="white", bd=2, relief=GROOVE)
        search_frame.pack(fill=X, ipady=10)

        Label(search_frame, text="Search ID:", bg="white", font=("Arial", 10)).grid(row=0, column=0, padx=15, pady=10, sticky=W)
        self.txt_search = Entry(search_frame, font=("Arial", 10), width=22)
        self.txt_search.grid(row=0, column=1, padx=10, pady=10)

        Label(search_frame, text="Target Date:", bg="white", font=("Arial", 10)).grid(row=1, column=0, padx=15, pady=10, sticky=W)
        self.txt_date = Entry(search_frame, font=("Arial", 10), width=22)
        self.txt_date.grid(row=1, column=1, padx=10, pady=10)
        self.txt_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        filter_btn_frame = Frame(search_frame, bg="white")
        filter_btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        Button(filter_btn_frame, text="Apply Filter", bg="#4b7bec", fg="white", font=("Arial", 10), width=12, bd=0, pady=4, command=self.search_data).pack(side=LEFT, padx=5)
        Button(filter_btn_frame, text="Show All", bg="#718093", fg="white", font=("Arial", 10), width=12, bd=0, pady=4, command=self.refresh_all).pack(side=LEFT, padx=5)

        # ================= 3. STATS PANEL =================
        stats_card = Frame(right_panel, bg="white", bd=1, relief=SOLID)
        stats_card.pack(fill=X, pady=(0, 15), ipady=10)
        stats_card.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.lbl_total = Label(stats_card, text="Total Records\n0", font=("Arial", 11, "bold"), bg="white", fg="#2f3640")
        self.lbl_total.grid(row=0, column=0, pady=10)
        
        self.lbl_present = Label(stats_card, text="Present\n0", font=("Arial", 11, "bold"), bg="white", fg="#20bf6b")
        self.lbl_present.grid(row=0, column=1, pady=10)
        
        self.lbl_late = Label(stats_card, text="Late\n0", font=("Arial", 11, "bold"), bg="white", fg="#f7b731")
        self.lbl_late.grid(row=0, column=2, pady=10)
        
        self.lbl_absent = Label(stats_card, text="Absent\n0", font=("Arial", 11, "bold"), bg="white", fg="#eb3b5a")
        self.lbl_absent.grid(row=0, column=3, pady=10)
        
        self.lbl_percentage = Label(stats_card, text="Attendance Rate: 0.00%", font=("Arial", 12, "bold"), bg="#d1d8e0", fg="#2f3640", padx=15, pady=5)
        self.lbl_percentage.grid(row=1, column=0, columnspan=4, sticky=EW, padx=20, pady=5)

        # ================= 4. DATA TABLE TREEVIEW =================
        table_frame = Frame(right_panel, bg="white")
        table_frame.pack(fill=BOTH, expand=True)

        scrollbar_y = Scrollbar(table_frame, orient=VERTICAL)
        
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Date", "StudentID", "Name", "Status", "PhotoPath"), show="headings", yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_y.pack(side=RIGHT, fill=Y)

        self.tree.heading("ID", text="Record ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("StudentID", text="Student ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Status", text="Status")
        self.tree.heading("PhotoPath", text="Photo Location")

        self.tree.column("ID", width=70, anchor=CENTER)
        self.tree.column("Date", width=110, anchor=CENTER)
        self.tree.column("StudentID", width=120, anchor=CENTER)
        self.tree.column("Name", width=220, anchor=W)
        self.tree.column("Status", width=110, anchor=CENTER)
        self.tree.column("PhotoPath", width=160, anchor=W)
        self.tree.pack(fill=BOTH, expand=True)

        # CRITICAL: Bind the row selection click directly to trigger the photo window popup
        self.tree.bind("<<TreeviewSelect>>", self.popup_student_photo)

        # Lower Action Bar Buttons
        lower_action_frame = Frame(right_panel, bg="#f4f6f9")
        lower_action_frame.pack(fill=X, pady=(10, 0))

        Button(lower_action_frame, text="Export CSV Data Sheet", bg="#2d3436", fg="white", font=("Arial", 10, "bold"), bd=0, pady=6, padx=15, command=self.export_csv).pack(side=RIGHT, padx=5)
        Button(lower_action_frame, text="Delete Selected Row", bg="#eb3b5a", fg="white", font=("Arial", 10, "bold"), bd=0, pady=6, padx=15, command=self.delete_record).pack(side=RIGHT, padx=5)

        # Initialize Grid View Engine
        self.refresh_all()

    # ================= DATABASE INITIALIZATION =================
    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS attendance(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    photo_path TEXT DEFAULT 'No Image'
                )
            """)
            conn.commit()

    # ================= POPUP ENGINE FUNCTION =================
    def popup_student_photo(self, event):
        """Triggers an instantaneous clean popup window presenting the target student's Photo ID."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        row_values = self.tree.item(selected_item)["values"]
        student_id = row_values[2]
        student_name = row_values[3]
        photo_path = row_values[5]

        # Cancel logic if row contains default text entries or invalid files
        if photo_path in ["No Image", "No Image File", ""]:
            return

        if not os.path.exists(photo_path):
            messagebox.showerror("File Error", f"The image file for {student_name} was moved or deleted from:\n{photo_path}")
            return

        # Create a clean standalone TopLevel popup window
        popup = Toplevel(self.root)
        popup.title(f"Photo ID Profile - {student_id}")
        popup.geometry("340x400")
        popup.config(bg="white")
        popup.resizable(False, False)

        # Force focus onto the popup window instantly
        popup.grab_set()

        Label(popup, text=f"STUDENT CARD", font=("Arial", 11, "bold"), bg="#4b7bec", fg="white", pady=6).pack(fill=X)

        # Load and render the file object safely inside custom canvas wrapper block
        try:
            # We preserve photo storage reference context inside popup so garbage collection won't delete it
            popup.img = PhotoImage(file=photo_path)
            
            canvas = Canvas(popup, width=220, height=220, bg="#f1f2f6", bd=1, relief=SOLID)
            canvas.pack(pady=20)
            
            # Position photo centered exactly inside tracking canvas viewport
            canvas.create_image(110, 110, image=popup.img, anchor=CENTER)
            
        except Exception as err:
            Label(popup, text="[ Failed to Load Format ]\nOnly standard .png or .gif formats supported.", fg="red", bg="white").pack(pady=40)

        # Profile metadata cards text block layout details base
        Label(popup, text=f"Name: {student_name}", font=("Arial", 11, "bold"), bg="white", fg="#2f3640").pack(pady=2)
        Label(popup, text=f"ID Code: {student_id}", font=("Arial", 10), bg="white", fg="#718093").pack(pady=2)
        
        Button(popup, text="Close Profile", font=("Arial", 9), bg="#eb3b5a", fg="white", bd=0, padx=10, pady=4, command=popup.destroy).pack(pady=15)

    # ================= AUXILIARY FORM FUNCTIONS =================
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo Image",
            filetypes=[("Image Files (PNG/GIF)", "*.png *.gif"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_photo_path = file_path
            filename = os.path.basename(file_path)
            self.lbl_photo_status.config(text=filename[:15] + "..." if len(filename) > 15 else filename, fg="green")

    def refresh_all(self):
        self.clear_fields()
        self.txt_search.delete(0, END)
        self.show_data()
        self.calculate_stats()

    def clear_fields(self):
        self.txt_id.delete(0, END)
        self.txt_name.delete(0, END)
        self.status_var.set("Present")
        self.selected_photo_path = ""
        self.lbl_photo_status.config(text="No image selected", fg="gray")

    def add_record(self):
        s_id = self.txt_id.get().strip()
        s_name = self.txt_name.get().strip()
        s_date = self.txt_date.get().strip()
        s_status = self.status_var.get()
        s_photo = self.selected_photo_path if self.selected_photo_path else "No Image File"

        if s_id == "" or s_name == "" or s_date == "":
            messagebox.showerror("Validation Error", "All primary form rows marked with * must be filled.")
            return

        try:
            datetime.strptime(s_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Date Format Error", "Please use YYYY-MM-DD formatting style.")
            return

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO attendance(date, student_id, student_name, status, photo_path)
                VALUES (?, ?, ?, ?, ?)
            """, (s_date, s_id, s_name, s_status, s_photo))
            conn.commit()

        messagebox.showinfo("Success", f"Attendance & Photo reference captured for {s_name}!")
        self.refresh_all()

    def show_data(self, specific_rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if specific_rows is None:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT id, date, student_id, student_name, status, photo_path FROM attendance ORDER BY id DESC")
                specific_rows = c.fetchall()

        for row in specific_rows:
            self.tree.insert("", END, values=row)

    def search_data(self):
        keyword = self.txt_search.get().strip()
        target_date = self.txt_date.get().strip()

        query = "SELECT id, date, student_id, student_name, status, photo_path FROM attendance WHERE 1=1"
        params = []

        if keyword:
            query += " AND student_id LIKE ?"
            params.append(f"%{keyword}%")
        if target_date:
            query += " AND date = ?"
            params.append(target_date)

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()
            
        self.show_data(specific_rows=rows)

    def delete_record(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a data entry row to remove first.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record entry?")
        if not confirm:
            return

        row_data = self.tree.item(selected)["values"]
        record_id = row_data[0]

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
            conn.commit()

        messagebox.showinfo("Deleted", "Entry removed from storage successfully.")
        self.refresh_all()

    def calculate_stats(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM attendance")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
            present = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM attendance WHERE status='Late'")
            late = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM attendance WHERE status='Absent'")
            absent = c.fetchone()[0]

        rate = ((present + late) / total * 100) if total > 0 else 0.0

        self.lbl_total.config(text=f"Total Records\n{total}")
        self.lbl_present.config(text=f"Present\n{present}")
        self.lbl_late.config(text=f"Late\n{late}")
        self.lbl_absent.config(text=f"Absent\n{absent}")
        self.lbl_percentage.config(text=f"Attendance Rate: {rate:.2f}%")

    def export_csv(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT id, date, student_id, student_name, status, photo_path FROM attendance")
            rows = c.fetchall()

        if not rows:
            messagebox.showwarning("Export Void", "No records found to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Comma Separated Values", "*.csv")],
            title="Export Records to CSV"
        )
        if file_path:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Record ID", "Date", "Student ID", "Student Name", "Status", "Photo Location Path"])
                writer.writerows(rows)
            messagebox.showinfo("Export Complete", "Data archive written safely!")

if __name__ == "__main__":
    root = Tk()
    app = AttendanceSystem(root)
    root.mainloop()
