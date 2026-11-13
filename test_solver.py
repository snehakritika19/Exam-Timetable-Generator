
import unittest
from csp_solver import ExamTimetableCSP


class TestTimetable(unittest.TestCase):

    def setUp(self):

        self.exams = [
            {
                "exam_id": "E1",
                "subject": "AI",
                "enrollment": 2,
                "building": "MAIN",
                "students": ["S1", "S2"]
            },
            {
                "exam_id": "E2",
                "subject": "DBMS",
                "enrollment": 2,
                "building": "MAIN",
                "students": ["S2", "S3"]
            }
        ]

        self.rooms = [
            {
                "room_id": "R1",
                "room_name": "Room 101",
                "capacity": 3,
                "building": "MAIN"
            }
        ]

        self.slots = [
            {
                "slot_id": "T1",
                "date": "2026-12-01",
                "time": "09:00-12:00"
            },
            {
                "slot_id": "T2",
                "date": "2026-12-01",
                "time": "13:00-16:00"
            }
        ]

    def test_valid_timetable(self):

        solver = ExamTimetableCSP(
            self.exams, self.rooms, self.slots
        )

        result = solver.solve()

        self.assertIsNotNone(result)

        self.assertEqual(
            solver.count_violations(result), 0
        )

    def test_impossible_timetable(self):

        solver = ExamTimetableCSP(
            self.exams, self.rooms, self.slots[:1]
        )

        result = solver.solve()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
