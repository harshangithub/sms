import os
import tempfile
import unittest

from student_management_system import StudentDatabase


class StudentDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        self.database = StudentDatabase(self.db_file.name)

    def tearDown(self):
        self.database.close()
        os.unlink(self.db_file.name)

    def test_add_and_fetch_student(self):
        self.database.add_student(1, "Aarav", "12", "A", "9876543210")

        students = self.database.fetch_all()

        self.assertEqual(len(students), 1)
        self.assertEqual(students[0], (1, "Aarav", "12", "A", "9876543210"))

    def test_update_and_delete_student(self):
        self.database.add_student(2, "Diya", "12", "B", "9123456780")

        updated = self.database.update_student(2, "Diya Sharma", "12", "C", "9988776655")
        found = self.database.search_student(2)
        deleted = self.database.delete_student(2)
        not_found_after_delete = self.database.search_student(2)

        self.assertTrue(updated)
        self.assertEqual(found, (2, "Diya Sharma", "12", "C", "9988776655"))
        self.assertTrue(deleted)
        self.assertIsNone(not_found_after_delete)


if __name__ == "__main__":
    unittest.main()
