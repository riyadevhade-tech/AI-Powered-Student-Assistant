
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "student_assistant.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                task_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_chat(question, answer):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (question, answer) VALUES (?, ?)",
            (question, answer)
        )


def get_chat_history():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, question, answer, created_at
            FROM chat_history
            ORDER BY id DESC
        """).fetchall()


def save_assignment(task_name, due_date, task_type):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assignments (task_name, due_date, task_type)
            VALUES (?, ?, ?)
        """, (task_name, due_date, task_type))


def get_assignments():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, task_name, due_date, task_type
            FROM assignments
            ORDER BY due_date
        """).fetchall()

        
# Advanced assignment and exam reminder features

def initialize_academic_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submission_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS exam_timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                exam_time TEXT NOT NULL,
                venue TEXT NOT NULL DEFAULT ''
            )
        """)


def save_submission(title, subject, due_date):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO submission_reminders
            (title, subject, due_date, status)
            VALUES (?, ?, ?, 'Pending')
        """, (title, subject, due_date))


def get_submissions():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, title, subject, due_date, status
            FROM submission_reminders
            ORDER BY due_date
        """).fetchall()


def update_submission_status(task_id, status):
    with get_connection() as conn:
        conn.execute("""
            UPDATE submission_reminders
            SET status = ?
            WHERE id = ?
        """, (status, task_id))


def save_exam(subject, exam_date, exam_time, venue):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO exam_timetable
            (subject, exam_date, exam_time, venue)
            VALUES (?, ?, ?, ?)
        """, (subject, exam_date, exam_time, venue))


def get_exams():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, subject, exam_date, exam_time, venue
            FROM exam_timetable
            ORDER BY exam_date, exam_time
        """).fetchall()

def delete_chat(chat_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM chat_history WHERE id = ?",
            (chat_id,)
        )


def clear_chat_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history")
        
def initialize_timetable_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS smart_timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            classroom TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_timetable(subject, day, start_time, end_time, classroom):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO smart_timetable
        (subject, day, start_time, end_time, classroom)
        VALUES (?, ?, ?, ?, ?)
    """, (subject, day, start_time, end_time, classroom))

    conn.commit()
    conn.close()


def get_timetable():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject, day, start_time, end_time, classroom
        FROM smart_timetable
        ORDER BY
            CASE day
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END,
            start_time
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_timetable_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM smart_timetable WHERE id = ?",
        (entry_id,)
    )

    conn.commit()
    conn.close()
