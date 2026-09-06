import sqlite3
try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:
    tk = None
    messagebox = None
    ttk = None


class StudentDatabase:
    def __init__(self, db_path: str = "students.db") -> None:
        self.connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                roll_no INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                section TEXT NOT NULL,
                phone TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def add_student(self, roll_no: int, name: str, class_name: str, section: str, phone: str) -> None:
        self.connection.execute(
            "INSERT INTO students (roll_no, name, class_name, section, phone) VALUES (?, ?, ?, ?, ?)",
            (roll_no, name, class_name, section, phone),
        )
        self.connection.commit()

    def update_student(self, roll_no: int, name: str, class_name: str, section: str, phone: str) -> bool:
        cursor = self.connection.execute(
            """
            UPDATE students
            SET name = ?, class_name = ?, section = ?, phone = ?
            WHERE roll_no = ?
            """,
            (name, class_name, section, phone, roll_no),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_student(self, roll_no: int) -> bool:
        cursor = self.connection.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        self.connection.commit()
        return cursor.rowcount > 0

    def search_student(self, roll_no: int):
        cursor = self.connection.execute(
            "SELECT roll_no, name, class_name, section, phone FROM students WHERE roll_no = ?",
            (roll_no,),
        )
        return cursor.fetchone()

    def fetch_all(self):
        cursor = self.connection.execute(
            "SELECT roll_no, name, class_name, section, phone FROM students ORDER BY roll_no"
        )
        return cursor.fetchall()

    def close(self) -> None:
        self.connection.close()


class StudentManagementSystem:
    def __init__(self, root: object) -> None:
        if tk is None or ttk is None or messagebox is None:
            raise RuntimeError("Tkinter is required to run the GUI application.")
        self.root = root
        self.root.title("Student Management System (Class 12 CBSE)")
        self.root.geometry("860x520")
        self.database = StudentDatabase()

        self.roll_no = tk.StringVar()
        self.name = tk.StringVar()
        self.class_name = tk.StringVar()
        self.section = tk.StringVar()
        self.phone = tk.StringVar()

        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self.root, text="Student Details")
        form.pack(fill="x", padx=12, pady=10)

        labels = ["Roll No", "Name", "Class", "Section", "Phone"]
        variables = [self.roll_no, self.name, self.class_name, self.section, self.phone]

        for index, (label, variable) in enumerate(zip(labels, variables)):
            ttk.Label(form, text=label).grid(row=index // 3 * 2, column=(index % 3) * 2, padx=6, pady=4, sticky="w")
            ttk.Entry(form, textvariable=variable, width=24).grid(
                row=index // 3 * 2 + 1,
                column=(index % 3) * 2,
                padx=6,
                pady=4,
                sticky="w",
            )

        button_frame = ttk.Frame(form)
        button_frame.grid(row=4, column=0, columnspan=6, pady=8)

        ttk.Button(button_frame, text="Add", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Update", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Delete", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Search", command=self.search_student).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Show All", command=self.refresh_table).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side="left", padx=4)

    def _build_table(self) -> None:
        table_frame = ttk.LabelFrame(self.root, text="Students")
        table_frame.pack(fill="both", expand=True, padx=12, pady=10)

        columns = ("roll_no", "name", "class_name", "section", "phone")
        self.student_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        headings = {
            "roll_no": "Roll No",
            "name": "Name",
            "class_name": "Class",
            "section": "Section",
            "phone": "Phone",
        }

        for column in columns:
            self.student_table.heading(column, text=headings[column])
            self.student_table.column(column, width=150 if column != "name" else 220)

        self.student_table.pack(side="left", fill="both", expand=True)
        self.student_table.bind("<<TreeviewSelect>>", self.on_table_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.student_table.configure(yscrollcommand=scrollbar.set)

    def validate_fields(self) -> tuple[bool, str]:
        if not self.roll_no.get().strip().isdigit():
            return False, "Roll number must be a whole number."
        if not self.name.get().strip():
            return False, "Name is required."
        if not self.class_name.get().strip():
            return False, "Class is required."
        if not self.section.get().strip():
            return False, "Section is required."
        phone_value = self.phone.get().strip()
        if not phone_value.isdigit() or len(phone_value) != 10:
            return False, "Phone number must be 10 digits."
        return True, ""

    def current_values(self):
        return (
            int(self.roll_no.get().strip()),
            self.name.get().strip(),
            self.class_name.get().strip(),
            self.section.get().strip().upper(),
            self.phone.get().strip(),
        )

    def add_student(self) -> None:
        valid, error = self.validate_fields()
        if not valid:
            messagebox.showerror("Invalid Input", error)
            return

        try:
            self.database.add_student(*self.current_values())
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Roll No", "A student with this roll number already exists.")
            return

        messagebox.showinfo("Success", "Student added successfully.")
        self.refresh_table()
        self.clear_fields()

    def update_student(self) -> None:
        valid, error = self.validate_fields()
        if not valid:
            messagebox.showerror("Invalid Input", error)
            return

        updated = self.database.update_student(*self.current_values())
        if not updated:
            messagebox.showerror("Not Found", "No student found for this roll number.")
            return

        messagebox.showinfo("Success", "Student updated successfully.")
        self.refresh_table()

    def delete_student(self) -> None:
        roll_text = self.roll_no.get().strip()
        if not roll_text.isdigit():
            messagebox.showerror("Invalid Input", "Enter a valid roll number to delete.")
            return

        deleted = self.database.delete_student(int(roll_text))
        if not deleted:
            messagebox.showerror("Not Found", "No student found for this roll number.")
            return

        messagebox.showinfo("Success", "Student deleted successfully.")
        self.refresh_table()
        self.clear_fields()

    def search_student(self) -> None:
        roll_text = self.roll_no.get().strip()
        if not roll_text.isdigit():
            messagebox.showerror("Invalid Input", "Enter a valid roll number to search.")
            return

        student = self.database.search_student(int(roll_text))
        self.student_table.delete(*self.student_table.get_children())

        if not student:
            messagebox.showinfo("No Result", "No student found for this roll number.")
            return

        self.student_table.insert("", "end", values=student)

    def refresh_table(self) -> None:
        self.student_table.delete(*self.student_table.get_children())
        for student in self.database.fetch_all():
            self.student_table.insert("", "end", values=student)

    def clear_fields(self) -> None:
        self.roll_no.set("")
        self.name.set("")
        self.class_name.set("")
        self.section.set("")
        self.phone.set("")

    def on_table_select(self, _event=None) -> None:
        selected = self.student_table.focus()
        if not selected:
            return
        values = self.student_table.item(selected, "values")
        if not values:
            return

        self.roll_no.set(values[0])
        self.name.set(values[1])
        self.class_name.set(values[2])
        self.section.set(values[3])
        self.phone.set(values[4])


if __name__ == "__main__":
    if tk is None:
        raise RuntimeError("Tkinter is not available in this Python environment.")
    app_root = tk.Tk()
    StudentManagementSystem(app_root)
    app_root.mainloop()
