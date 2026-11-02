import json
from datetime import date, datetime

from flask import Flask, redirect, render_template_string, request, url_for


app = Flask(__name__)
DATA_FILE = "study_sessions.json"


def load_sessions():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_sessions(sessions):
    with open(DATA_FILE, "w") as file:
        json.dump(sessions, file, indent=4)


HOME_PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Smart Study Planner</title>
    <style>
        body {
            max-width: 900px;
            margin: 35px auto;
            padding: 0 18px;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #1f2937;
        }
        h1 { color: #173b6c; }
        .card {
            background: white;
            padding: 20px;
            margin: 18px 0;
            border-radius: 12px;
            box-shadow: 0 3px 12px #0000000d;
        }
        .summary {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .summary div {
            background: #edf4ff;
            padding: 12px;
            border-radius: 8px;
        }
        form.add-form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 10px;
        }
        input, select, button {
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            font-size: 15px;
        }
        button, .edit-link {
            border: 0;
            background: #2563eb;
            color: white;
            cursor: pointer;
            text-decoration: none;
            padding: 10px;
            border-radius: 7px;
            display: inline-block;
        }
        button.delete { background: #dc2626; }
        button.done { background: #15803d; }
        button.undo { background: #64748b; }
        .session {
            background: #f8fafc;
            border-left: 5px solid #2563eb;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 12px 0;
        }
        .session.completed { border-left-color: #16a34a; }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .muted { color: #64748b; }
    </style>
</head>
<body>
    <h1>Smart Study Planner</h1>
    <p class="muted">Add topics, track progress, and keep exam dates in one place.</p>

    <section class="card">
        <h2>Progress</h2>
        <div class="summary">
            <div>Total: <strong>{{ total_hours }} hours</strong></div>
            <div>Completed: <strong>{{ completed_count }}</strong></div>
            <div>Remaining: <strong>{{ remaining_count }}</strong></div>
            <div>Remaining time: <strong>{{ remaining_hours }} hours</strong></div>
            <div>Suggested daily time: <strong>{{ daily_hours }} hours</strong></div>
        </div>
    </section>

    <section class="card">
        <h2>Add a study session</h2>
        <form class="add-form" action="{{ url_for('add_session') }}" method="post">
            <input name="subject" placeholder="Subject, e.g. Maths" required>
            <input name="topic" placeholder="Topic, e.g. Algebra" required>
            <input name="hours" type="number" min="0.1" step="0.1"
                   placeholder="Study hours" required>
            <select name="priority">
                <option value="high">High priority</option>
                <option value="medium" selected>Medium priority</option>
                <option value="low">Low priority</option>
            </select>
            <input name="exam_date" placeholder="Exam date: DD-MM-YYYY"
                   pattern="[0-9]{2}-[0-9]{2}-[0-9]{4}" required>
            <button type="submit">Add session</button>
        </form>
    </section>

    <section class="card">
        <h2>Your study sessions</h2>
        {% if sessions %}
            {% for session in sessions %}
                <div class="session {% if session.completed %}completed{% endif %}">
                    <strong>{{ session.subject }} — {{ session.topic }}</strong>
                    <p>
                        {{ session.hours }} hours |
                        Priority: {{ session.priority }} |
                        Exam: {{ session.exam_date }} |
                        Days left: {{ session.days_left }}
                    </p>
                    <p>Status: {{ "Completed" if session.completed else "Not completed" }}</p>

                    <div class="actions">
                        <a class="edit-link"
                           href="{{ url_for('edit_session', index=session.index) }}">
                            Edit
                        </a>

                        <form action="{{ url_for('toggle_session', index=session.index) }}"
                              method="post">
                            <button class="{% if session.completed %}undo{% else %}done{% endif %}">
                                {% if session.completed %}Mark not completed{% else %}Mark completed{% endif %}
                            </button>
                        </form>

                        <form action="{{ url_for('delete_session', index=session.index) }}"
                              method="post"
                              onsubmit="return confirm('Delete this session?');">
                            <button class="delete">Delete</button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <p>No sessions yet. Add one using the form above.</p>
        {% endif %}
    </section>
</body>
</html>
"""


EDIT_PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Edit Study Session</title>
    <style>
        body {
            max-width: 650px;
            margin: 35px auto;
            padding: 0 18px;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #1f2937;
        }
        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 3px 12px #0000000d;
        }
        label { display: block; margin-top: 14px; }
        input, select, button {
            box-sizing: border-box;
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            font-size: 15px;
        }
        button {
            margin-top: 18px;
            background: #2563eb;
            color: white;
            border: 0;
            cursor: pointer;
        }
        a { display: inline-block; margin-top: 16px; }
    </style>
</head>
<body>
    <section class="card">
        <h1>Edit study session</h1>

        <form method="post">
            <label>Subject
                <input name="subject" value="{{ session.subject }}" required>
            </label>

            <label>Topic
                <input name="topic" value="{{ session.topic }}" required>
            </label>

            <label>Study hours
                <input name="hours" type="number" min="0.1" step="0.1"
                       value="{{ session.hours }}" required>
            </label>

            <label>Priority
                <select name="priority">
                    <option value="high" {% if session.priority == "high" %}selected{% endif %}>High</option>
                    <option value="medium" {% if session.priority == "medium" %}selected{% endif %}>Medium</option>
                    <option value="low" {% if session.priority == "low" %}selected{% endif %}>Low</option>
                </select>
            </label>

            <label>Exam date (DD-MM-YYYY)
                <input name="exam_date" value="{{ session.exam_date }}"
                       pattern="[0-9]{2}-[0-9]{2}-[0-9]{4}" required>
            </label>

            <button type="submit">Save changes</button>
        </form>

        <a href="{{ url_for('home') }}">Back to planner</a>
    </section>
</body>
</html>
"""


@app.route("/")
def home():
    sessions = load_sessions()
    today = date.today()
    display_sessions = []

    for index, session in enumerate(sessions):
        exam_day = datetime.strptime(
            session["exam_date"], "%d-%m-%Y"
        ).date()

        display_sessions.append({
            **session,
            "index": index,
            "days_left": (exam_day - today).days
        })

    priority_order = {"high": 1, "medium": 2, "low": 3}
    display_sessions.sort(
        key=lambda session: priority_order.get(session["priority"], 4)
    )

    total_hours = sum(session["hours"] for session in sessions)
    completed_count = sum(
        1 for session in sessions if session["completed"]
    )
    unfinished = [
        session for session in sessions if not session["completed"]
    ]
    remaining_count = len(unfinished)
    remaining_hours = sum(
        session["hours"] for session in unfinished
    )

    if unfinished:
        nearest_exam = min(
            datetime.strptime(session["exam_date"], "%d-%m-%Y").date()
            for session in unfinished
        )
        days_to_exam = max((nearest_exam - today).days, 1)
        daily_hours = remaining_hours / days_to_exam
    else:
        daily_hours = 0

    return render_template_string(
        HOME_PAGE,
        sessions=display_sessions,
        total_hours=round(total_hours, 2),
        completed_count=completed_count,
        remaining_count=remaining_count,
        remaining_hours=round(remaining_hours, 2),
        daily_hours=round(daily_hours, 2)
    )


@app.route("/add", methods=["POST"])
def add_session():
    subject = request.form["subject"].strip()
    topic = request.form["topic"].strip()
    priority = request.form["priority"]
    exam_date = request.form["exam_date"].strip()

    try:
        hours = float(request.form["hours"])
        datetime.strptime(exam_date, "%d-%m-%Y")

        if hours <= 0:
            return "Study hours must be greater than 0.", 400
    except ValueError:
        return "Enter valid hours and a date in DD-MM-YYYY format.", 400

    sessions = load_sessions()
    sessions.append({
        "subject": subject,
        "topic": topic,
        "hours": hours,
        "priority": priority,
        "completed": False,
        "exam_date": exam_date
    })
    save_sessions(sessions)

    return redirect(url_for("home"))


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_session(index):
    sessions = load_sessions()

    if not 0 <= index < len(sessions):
        return "Study session not found.", 404

    if request.method == "POST":
        subject = request.form["subject"].strip()
        topic = request.form["topic"].strip()
        priority = request.form["priority"]
        exam_date = request.form["exam_date"].strip()

        try:
            hours = float(request.form["hours"])
            datetime.strptime(exam_date, "%d-%m-%Y")

            if hours <= 0:
                return "Study hours must be greater than 0.", 400
        except ValueError:
            return "Enter valid hours and a date in DD-MM-YYYY format.", 400

        sessions[index]["subject"] = subject
        sessions[index]["topic"] = topic
        sessions[index]["hours"] = hours
        sessions[index]["priority"] = priority
        sessions[index]["exam_date"] = exam_date

        save_sessions(sessions)
        return redirect(url_for("home"))

    return render_template_string(
        EDIT_PAGE,
        session=sessions[index]
    )


@app.route("/toggle/<int:index>", methods=["POST"])
def toggle_session(index):
    sessions = load_sessions()

    if 0 <= index < len(sessions):
        sessions[index]["completed"] = not sessions[index]["completed"]
        save_sessions(sessions)

    return redirect(url_for("home"))


@app.route("/delete/<int:index>", methods=["POST"])
def delete_session(index):
    sessions = load_sessions()

    if 0 <= index < len(sessions):
        sessions.pop(index)
        save_sessions(sessions)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)