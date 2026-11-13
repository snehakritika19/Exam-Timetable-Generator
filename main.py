
import csv
import time
from pathlib import Path

from csp_solver import ExamTimetableCSP


# Get project folder location
BASE = Path(__file__).resolve().parent


# Read CSV files
def read_csv(filename):

    with open(
        filename,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file has no column headers.")

        # Remove unwanted spaces from column names
        reader.fieldnames = [
            name.strip().lower()
            for name in reader.fieldnames
        ]

        data = []

        for row in reader:

            clean_row = {
                key.strip().lower(): value.strip()
                for key, value in row.items()
                if key is not None and value is not None
            }

            data.append(clean_row)

        return data


# Check required CSV columns
def check_columns(data, required, filename):

    if not data:
        raise ValueError(filename + " contains no records.")

    missing = set(required) - set(data[0].keys())

    if missing:

        raise ValueError(
            filename + " is missing columns: "
            + ", ".join(sorted(missing))
        )


# Main function
def main():

    try:

        # Load input files
        exams = read_csv(BASE / "data" / "exams.csv")

        rooms = read_csv(BASE / "data" / "rooms.csv")

        slots = read_csv(BASE / "data" / "slots.csv")

        # Validate CSV headers
        check_columns(
            exams,
            ["exam_id", "subject", "enrollment",
             "building", "students"],
            "exams.csv"
        )

        check_columns(
            rooms,
            ["room_id", "room_name", "capacity", "building"],
            "rooms.csv"
        )

        check_columns(
            slots,
            ["slot_id", "date", "time"],
            "slots.csv"
        )

        # Convert examination data
        for exam in exams:

            exam["enrollment"] = int(
                exam["enrollment"]
            )

            exam["students"] = [
                student.strip()
                for student in exam["students"].split(";")
                if student.strip()
            ]

        # Convert room capacity
        for room in rooms:

            room["capacity"] = int(
                room["capacity"]
            )

        # Create CSP object
        solver = ExamTimetableCSP(
            exams,
            rooms,
            slots
        )

        print("\nGenerating examination timetable...")

        # Measure execution time
        start_time = time.perf_counter()

        result = solver.solve()

        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Check whether a solution exists
        if result is None:

            print("\nNo valid timetable could be generated.")

            print("Search Nodes:", solver.nodes)
            print("Backtracks:", solver.backtracks)

            return

        # Display generated timetable
        print("\nGENERATED EXAMINATION TIMETABLE")

        print("-" * 78)

        print(
            f"{'Subject':25}"
            f"{'Date':15}"
            f"{'Time':18}"
            f"{'Room':15}"
        )

        print("-" * 78)

        for exam_id, (slot, room) in result.items():

            subject = solver.exams[exam_id]["subject"]

            print(
                f"{subject:25}"
                f"{slot['date']:15}"
                f"{slot['time']:18}"
                f"{room['room_name']:15}"
            )

        print("-" * 78)

        # Validate timetable
        violations = solver.count_violations(result)

        print("\nPERFORMANCE RESULTS")

        print("Search Nodes:", solver.nodes)

        print("Backtracks:", solver.backtracks)

        print("Constraint Violations:", violations)

        print(
            "Execution Time:",
            round(execution_time, 6),
            "seconds"
        )

        if violations == 0:

            print("\nTimetable generated successfully!")

        # Export timetable into CSV
        output_file = BASE / "generated_timetable.csv"

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Subject",
                "Date",
                "Time",
                "Room",
                "Enrollment",
                "Capacity"
            ])

            for exam_id, (slot, room) in result.items():

                exam = solver.exams[exam_id]

                writer.writerow([
                    exam["subject"],
                    slot["date"],
                    slot["time"],
                    room["room_name"],
                    exam["enrollment"],
                    room["capacity"]
                ])

        print("\nTimetable saved successfully!")

        print("Output file:", output_file.name)

    except (OSError, ValueError, KeyError) as error:

        print("\nError:", error)


# Program execution starts here
if __name__ == "__main__":

    main()
