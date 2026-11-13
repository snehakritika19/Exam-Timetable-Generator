
class ExamTimetableCSP:

    def __init__(self, exams, rooms, slots):

        self.exams = {e["exam_id"]: e for e in exams}
        self.rooms = rooms
        self.slots = slots

        self.nodes = 0
        self.backtracks = 0

        # Create possible room and time combinations
        self.domains = {}

        for exam in exams:

            choices = []

            for slot in slots:
                for room in rooms:

                    if (room["capacity"] >= exam["enrollment"]
                        and room["building"] == exam["building"]):

                        choices.append((slot, room))

            self.domains[exam["exam_id"]] = choices

    # Check whether an assignment is valid
    def is_valid(self, exam_id, slot, room, assigned):

        exam = self.exams[exam_id]

        for other_id, (other_slot, other_room) in assigned.items():

            same_time = (
                slot["date"] == other_slot["date"]
                and slot["time"] == other_slot["time"]
            )

            if same_time:

                # Check room conflict
                if room["room_id"] == other_room["room_id"]:
                    return False

                # Check student conflict
                other_exam = self.exams[other_id]

                if set(exam["students"]) & set(other_exam["students"]):
                    return False

        return True

    # Get all valid choices for an examination
    def get_valid_values(self, exam_id, assigned):

        choices = []

        for slot, room in self.domains[exam_id]:

            if self.is_valid(exam_id, slot, room, assigned):
                choices.append((slot, room))

        return choices

    # Select the examination with minimum choices (MRV)
    def select_exam(self, assigned):

        remaining = [
            e for e in self.exams
            if e not in assigned
        ]

        return min(
            remaining,
            key=lambda e: len(self.get_valid_values(e, assigned))
        )

    # Backtracking algorithm
    def backtrack(self, assigned):

        if len(assigned) == len(self.exams):
            return assigned

        self.nodes += 1

        exam_id = self.select_exam(assigned)

        choices = self.get_valid_values(exam_id, assigned)

        for slot, room in choices:

            assigned[exam_id] = (slot, room)

            result = self.backtrack(assigned)

            if result is not None:
                return result

            # Backtrack if assignment fails
            del assigned[exam_id]
            self.backtracks += 1

        return None

    # Start timetable generation
    def solve(self):

        for domain in self.domains.values():

            if not domain:
                return None

        return self.backtrack({})

    # Verify the generated timetable
    def count_violations(self, assigned):

        violations = 0

        exam_ids = list(assigned.keys())

        for i in range(len(exam_ids)):

            id1 = exam_ids[i]
            slot1, room1 = assigned[id1]
            exam1 = self.exams[id1]

            for j in range(i + 1, len(exam_ids)):

                id2 = exam_ids[j]
                slot2, room2 = assigned[id2]
                exam2 = self.exams[id2]

                same_time = (
                    slot1["date"] == slot2["date"]
                    and slot1["time"] == slot2["time"]
                )

                if same_time:

                    if room1["room_id"] == room2["room_id"]:
                        violations += 1

                    if set(exam1["students"]) & set(exam2["students"]):
                        violations += 1

        return violations
