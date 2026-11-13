
import traceback
import csv
import time
from pathlib import Path
from flask import Flask, render_template, send_file
from csp_solver import ExamTimetableCSP

app = Flask(__name__)

BASE = Path(__file__).resolve().parent


# Read CSV files safely
def read_csv(filename):

    with open(
        filename,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        # Ignore blank lines
        lines = [line for line in file if line.strip()]

        if not lines:
            raise ValueError(f"{filename.name} is empty.")

        reader = csv.DictReader(lines)

        if not reader.fieldnames:
            raise ValueError(f"Headers missing in {filename.name}.")

        # Clean column names
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

        if not data:
            raise ValueError(f"No records found in {filename.name}.")

        return data


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Generate examination timetable
@app.route("/generate", methods=["POST"])
def generate():

    try:

        # Load datasets
        exams = read_csv(BASE / "data" / "exams.csv")
        rooms = read_csv(BASE / "data" / "rooms.csv")
        slots = read_csv(BASE / "data" / "slots.csv")

        # Check examination columns
        required_exam_columns = {
            "exam_id", "subject", "enrollment",
            "building", "students"
        }

        if not required_exam_columns.issubset(exams[0].keys()):
            raise ValueError(
                "Invalid columns in exams.csv. "
                "Check the CSV header."
            )

        # Check room columns
        required_room_columns = {
            "room_id", "room_name", "capacity", "building"
        }

        if not required_room_columns.issubset(rooms[0].keys()):
            raise ValueError(
                "Invalid columns in rooms.csv. "
                "Check the CSV header."
            )

        # Check slot columns
        required_slot_columns = {
            "slot_id", "date", "time"
        }

        if not required_slot_columns.issubset(slots[0].keys()):
            raise ValueError(
                "Invalid columns in slots.csv. "
                "Check the CSV header."
            )

        # Convert examination data
        for exam in exams:

            exam["enrollment"] = int(exam["enrollment"])

            exam["students"] = [
                student.strip()
                for student in exam["students"].split(";")
                if student.strip()
            ]

        # Convert room capacity
        for room in rooms:
            room["capacity"] = int(room["capacity"])

        # Initialize CSP solver
        solver = ExamTimetableCSP(
            exams,
            rooms,
            slots
        )

        # Generate timetable
        start_time = time.perf_counter()

        result = solver.solve()

        execution_time = time.perf_counter() - start_time

        if result is None:

            return render_template(
                "index.html",
                error="No valid timetable could be generated."
            )

        # Prepare timetable output
        timetable = []

        for exam_id, (slot, room) in result.items():

            exam = solver.exams[exam_id]

            timetable.append({
                "subject": exam["subject"],
                "date": slot["date"],
                "time": slot["time"],
                "room": room["room_name"],
                "enrollment": exam["enrollment"],
                "capacity": room["capacity"]
            })

        # Validate constraints
        violations = solver.count_violations(result)

        # Export timetable to CSV
        output_file = BASE / "generated_timetable.csv"

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "subject", "date", "time",
                    "room", "enrollment", "capacity"
                ]
            )

            writer.writeheader()
            writer.writerows(timetable)

        # Display results
        return render_template(
            "index.html",
            timetable=timetable,
            violations=violations,
            nodes=solver.nodes,
            backtracks=solver.backtracks,
            execution_time=round(execution_time, 6)
        )

    except Exception as error:

        traceback.print_exc()

        return render_template(
            "index.html",
            error=str(error)
        )


# Download generated timetable
@app.route("/download")
def download():

    output_file = BASE / "generated_timetable.csv"

    if not output_file.exists():
        return "Generate a timetable first."

    return send_file(
        output_file,
        as_attachment=True
    )


# Run Flask application
if __name__ == "__main__":

    app.run(debug=True)
