import json
from datetime import datetime


DATA_FILE = "study_sessions.json"


def load_sessions():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Saved data could not be read. Starting with an empty plan.")
        return []


def save_sessions(sessions):
    with open(DATA_FILE, "w") as file:
        json.dump(sessions, file, indent=4)


def get_positive_hours(prompt):
    while True:
        try:
            hours = float(input(prompt))

            if hours > 0:
                return hours

            print("Enter a number greater than 0.")

        except ValueError:
            print("Enter a valid number, like 1 or 1.5.")


def get_session_count():
    while True:
        try:
            count = int(input("How many study sessions do you want to add? "))

            if count > 0:
                return count

            print("Enter at least 1 session.")

        except ValueError:
            print("Enter a whole number, like 1 or 2.")


def get_priority():
    while True:
        priority = input("Priority (high/medium/low): ").lower()

        if priority in ["high", "medium", "low"]:
            return priority

        print("Please enter high, medium, or low.")


def get_completed_status():
    while True:
        answer = input("Is this session completed? (yes/no): ").lower()

        if answer == "yes":
            return True
        elif answer == "no":
            return False

        print("Please type yes or no.")


def get_exam_date():
    while True:
        date_text = input("Exam date (DD-MM-YYYY): ")

        try:
            datetime.strptime(date_text, "%d-%m-%Y")
            return date_text
        except ValueError:
            print("Enter a valid date, like 25-12-2026.")


def add_sessions(sessions):
    count = get_session_count()

    for number in range(count):
        print("\nEnter session", number + 1)

        subject = input("Subject: ")
        topic = input("Topic: ")
        hours = get_positive_hours("Study hours: ")
        priority = get_priority()
        completed = get_completed_status()
        exam_date = get_exam_date()

        sessions.append({
            "subject": subject,
            "topic": topic,
            "hours": hours,
            "priority": priority,
            "completed": completed,
            "exam_date": exam_date
        })

    save_sessions(sessions)
    print("\nSessions saved!")


def view_plan(sessions):
    if not sessions:
        print("\nYou don't have any study sessions yet.")
        return

    priority_order = {"high": 1, "medium": 2, "low": 3}
    sorted_sessions = sorted(
        sessions,
        key=lambda session: priority_order[session["priority"]]
    )

    total_hours = sum(session["hours"] for session in sessions)
    completed_count = sum(
        1 for session in sessions if session["completed"]
    )
    remaining_count = len(sessions) - completed_count

    unfinished = [
        session for session in sessions
        if not session["completed"]
    ]

    remaining_hours = sum(
        session["hours"] for session in unfinished
    )

    if unfinished:
        nearest_exam = min(
            datetime.strptime(session["exam_date"], "%d-%m-%Y").date()
            for session in unfinished
        )
        days_left = max(
            (nearest_exam - datetime.now().date()).days,
            1
        )
        daily_hours = remaining_hours / days_left
    else:
        daily_hours = 0

    print("\n--- Your Study Plan ---")

    for number, session in enumerate(sorted_sessions, start=1):
        exam_day = datetime.strptime(
            session["exam_date"], "%d-%m-%Y"
        ).date()
        exam_days_left = (exam_day - datetime.now().date()).days

        print(
            number,
            ".",
            session["subject"],
            "-",
            session["topic"],
            "-",
            session["hours"],
            "hours - Priority:",
            session["priority"],
            "- Completed:",
            session["completed"],
            "- Exam:",
            session["exam_date"],
            "- Days left:",
            exam_days_left
        )

    print("Total study time:", total_hours, "hours")
    print("Completed sessions:", completed_count)
    print("Remaining sessions:", remaining_count)
    print("Remaining study time:", remaining_hours, "hours")
    print("Suggested study time per day:", round(daily_hours, 2), "hours")

    if unfinished:
        print("\n--- Sessions Still To Study ---")

        for session in unfinished:
            exam_day = datetime.strptime(
                session["exam_date"], "%d-%m-%Y"
            ).date()
            session_days_left = max(
                (exam_day - datetime.now().date()).days,
                1
            )
            hours_per_day = session["hours"] / session_days_left

            print(
                session["subject"],
                "-",
                session["topic"],
                "-",
                round(hours_per_day, 2),
                "hours per day"
            )
    else:
        print("\nAll sessions are completed!")

    with open("study_plan.txt", "w") as file:
        file.write("--- Your Study Plan ---\n")

        for session in sorted_sessions:
            file.write(
                f'{session["subject"]} - {session["topic"]} - '
                f'{session["hours"]} hours - '
                f'Priority: {session["priority"]} - '
                f'Completed: {session["completed"]} - '
                f'Exam date: {session["exam_date"]}\n'
            )

        file.write(f"Total study time: {total_hours} hours\n")
        file.write(f"Completed sessions: {completed_count}\n")
        file.write(f"Remaining sessions: {remaining_count}\n")
        file.write(f"Remaining study time: {remaining_hours} hours\n")
        file.write(
            f"Suggested study time per day: "
            f"{round(daily_hours, 2)} hours\n"
        )

    print("\nPlan report saved to study_plan.txt")


def update_completed_status(sessions):
    if not sessions:
        print("\nThere are no sessions to update yet.")
        return

    print("\n--- Choose a Session ---")

    for number, session in enumerate(sessions, start=1):
        print(
            number,
            ".",
            session["subject"],
            "-",
            session["topic"],
            "- Completed:",
            session["completed"]
        )

    while True:
        try:
            choice = int(input("Which session number do you want to update? "))

            if 1 <= choice <= len(sessions):
                break

            print("Choose a number from the list.")
        except ValueError:
            print("Enter a whole number.")

    session = sessions[choice - 1]
    session["completed"] = get_completed_status()

    save_sessions(sessions)
    print("Session status saved!")


def delete_session(sessions):
    if not sessions:
        print("\nThere are no sessions to delete.")
        return

    print("\n--- Choose a Session to Delete ---")

    for number, session in enumerate(sessions, start=1):
        print(
            number,
            ".",
            session["subject"],
            "-",
            session["topic"]
        )

    while True:
        try:
            choice = int(input("Which session number do you want to delete? "))

            if 1 <= choice <= len(sessions):
                break

            print("Choose a number from the list.")
        except ValueError:
            print("Enter a whole number.")

    removed_session = sessions.pop(choice - 1)
    save_sessions(sessions)

    print(
        "Deleted:",
        removed_session["subject"],
        "-",
        removed_session["topic"]
    )


sessions = load_sessions()

while True:
    print("\n=== Smart Study Planner ===")
    print("1. Add study sessions")
    print("2. View study plan")
    print("3. Update a session's completed status")
    print("4. Delete a study session")
    print("5. Exit")

    choice = input("Choose 1, 2, 3, 4, or 5: ")

    if choice == "1":
        add_sessions(sessions)
    elif choice == "2":
        view_plan(sessions)
    elif choice == "3":
        update_completed_status(sessions)
    elif choice == "4":
        delete_session(sessions)
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Please choose 1, 2, 3, 4, or 5.")