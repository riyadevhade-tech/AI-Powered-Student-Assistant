
import streamlit as st
from io import BytesIO
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet

from database import (
    initialize_database,
    initialize_academic_tables,
    save_chat,
    get_chat_history,
    delete_chat,
    clear_chat_history,
    save_assignment,
    get_assignments,
    save_submission,
    get_submissions,
    update_submission_status,
    save_exam,
    get_exams,
)

st.set_page_config(
    page_title="AI-Powered Student Assistant",
    page_icon="🎓",
    layout="wide",
)


# Premium UI theme
st.markdown("""
<style>
:root { color-scheme: light; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f5f8ff 0%, #ffffff 45%, #f8fbff 100%);
}
[data-testid="stHeader"] { background: rgba(255,255,255,0.75); }
.block-container { padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1250px; }
h1 { color: #173b6c; letter-spacing: -0.035em; }
h2, h3 { color: #214b7a; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102d52 0%, #1b4776 100%);
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: .45rem .6rem; border-radius: 9px; margin-bottom: .2rem;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,.12);
}
[data-testid="stMetric"] {
    background: #ffffff; border: 1px solid #e0e9f5; padding: 1rem;
    border-radius: 14px; box-shadow: 0 3px 14px rgba(24,58,99,.06);
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    border-radius: 10px; border: 0; background: #215a9a; color: #ffffff;
    font-weight: 600; padding: .55rem 1rem; transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: #153d6d; color: #ffffff; border: 0;
}
[data-testid="stChatMessage"] {
    border: 1px solid #e4ebf5; border-radius: 14px; padding: .8rem;
    margin-bottom: .6rem; background: rgba(255,255,255,.9);
}
[data-testid="stDataFrame"] { border: 1px solid #e1eaf5; border-radius: 10px; }
hr { border-color: #dce6f3; }
.small-note { color: #62758c; font-size: .92rem; }
</style>
""", unsafe_allow_html=True)


def create_academic_pdf(submissions, exams):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("AI-Powered Student Assistant", styles["Title"])
    )
    content.append(
        Paragraph("Academic Planner Report", styles["Heading2"])
    )
    content.append(
        Paragraph(f"Generated on: {date.today()}", styles["Normal"])
    )
    content.append(Spacer(1, 18))

    content.append(Paragraph("Assignment Submissions", styles["Heading2"]))

    assignment_data = [["Assignment Details"]]

    if submissions:
        for item in submissions:
            assignment_data.append([
                " | ".join(str(value) for value in item)
            ])
    else:
        assignment_data.append(["No assignment submissions found."])

    assignment_table = Table(assignment_data, colWidths=[500])
    assignment_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    content.append(assignment_table)
    content.append(Spacer(1, 18))

    content.append(Paragraph("Examination Timetable", styles["Heading2"]))

    exam_data = [["Examination Details"]]

    if exams:
        for item in exams:
            exam_data.append([
                " | ".join(str(value) for value in item)
            ])
    else:
        exam_data.append(["No examinations found."])

    exam_table = Table(exam_data, colWidths=[500])
    exam_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#38761D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    content.append(exam_table)

    doc.build(content)
    buffer.seek(0)

    return buffer.getvalue()

# Initialize database
initialize_database()
initialize_academic_tables()

st.title("🎓 AI-Powered Student Assistant")
st.caption("Your Smart Academic Support Platform")
st.markdown(
    '<div class="small-note">A centralized space for study support, resources, and academic planning.</div>',
    unsafe_allow_html=True,
)

# Sidebar menu
with st.sidebar:
    st.header("Student Menu")
    page = st.radio(
        "Navigate",
        [
            "Home",
            "AI Assistant",
            "Chat History",
            "Assignments & Exams",
            "Study Resources",
            "Academic Planner",
            "About",
        ],
    )

# HOME PAGE
if page == "Home":
    st.markdown("## Welcome to your academic workspace")
    st.markdown(
        '<div style="background:linear-gradient(120deg,#173b6c,#2877b9);'
        'padding:1.35rem 1.5rem;border-radius:16px;color:white;margin-bottom:1.2rem;">'
        '<div style="font-size:1.55rem;font-weight:700;color:white;">Learn smarter. Stay organized.</div>'
        '<div style="font-size:1rem;color:#eef6ff;margin-top:.35rem;">'
        'Ask study questions, keep track of assignments, and plan upcoming exams in one place.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Platform", "Student AI")
    col2.metric("Database", "SQLite")
    col3.metric("AI Assistant", "Available")

    st.write(
        "Ask academic questions, save conversations, "
        "manage assignments, and explore study resources."
    )



# AI ASSISTANT PAGE
elif page == "AI Assistant":
    st.subheader("🤖 AI Chatbot")
    st.write(
        "Ask questions about Python, NumPy, Pandas, AI, "
        "programming, or your studies."
    )

    def get_local_answer(question):
        q = question.lower().strip()

        if "numpy" in q:
            return (
                "NumPy is a Python library used for numerical "
                "calculations and working with arrays. "
                "It is useful for scientific computing and data analysis."
            )

        elif "pandas" in q:
            return (
                "Pandas is a Python library used to organize, "
                "analyze, and manipulate data. It provides "
                "DataFrames and Series."
            )

        elif "python" in q:
            return (
                "Python is a popular programming language. "
                "It is used in web development, automation, "
                "data analysis, AI, and machine learning."
            )

        elif "artificial intelligence" in q or "what is ai" in q:
            return (
                "Artificial Intelligence (AI) is a technology "
                "that enables computers to perform tasks that "
                "normally require human intelligence."
            )

        elif "machine learning" in q:
            return (
                "Machine Learning is a branch of AI in which "
                "computers learn patterns from data to make "
                "predictions or decisions."
            )

        elif "nlp" in q or "natural language processing" in q:
            return (
                "NLP stands for Natural Language Processing. "
                "It helps computers understand and process "
                "human language."
            )

        elif "chatbot" in q:
            return (
                "A chatbot is a computer program that interacts "
                "with users through text or speech. This project "
                "uses predefined answers for common questions."
            )

        elif "project" in q or "student assistant" in q:
            return (
                "AI-Powered Student Assistant is an academic "
                "support project that helps students find basic "
                "study information through a chatbot interface."
            )

        elif "hello" in q or "hi" == q or "hey" in q:
            return (
                "Hello! Welcome to AI-Powered Student Assistant. "
                "Ask me about Python, NumPy, Pandas, AI, or NLP."
            )

        elif "help" in q:
            return (
                "I can answer basic questions about Python, "
                "NumPy, Pandas, Artificial Intelligence, "
                "Machine Learning, NLP, and this student project."
            )

        else:
            return (
                "Sorry, I don't have a predefined answer for "
                "that question yet. Try asking about Python, "
                "NumPy, Pandas, AI, Machine Learning, or NLP."
            )

    # Display saved conversations
    for row in reversed(get_chat_history()):
        with st.chat_message("user"):
            st.write(row[1])

        with st.chat_message("assistant"):
            st.write(row[2])

    # Ask a new question
    question = st.chat_input("Ask your academic question...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        answer = get_local_answer(question)

        with st.chat_message("assistant"):
            st.write(answer)

        save_chat(question, answer)
        st.success("Chat saved successfully!")

# CHAT HISTORY PAGE
elif page == "Chat History":
    st.subheader("💬 Saved Chat History")

    history = get_chat_history()

    if history:
        st.warning("Deleted conversations cannot be restored.")

        if st.button("🗑️ Clear All History", key="clear_all_history"):
            st.session_state["confirm_clear_history"] = True

        if st.session_state.get("confirm_clear_history", False):
            st.write("Are you sure you want to delete all saved chats?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Yes, Delete All", key="confirm_delete_all"):
                    clear_chat_history()
                    st.session_state["confirm_clear_history"] = False
                    st.success("All chat history deleted.")
                    st.rerun()

            with col2:
                if st.button("Cancel", key="cancel_delete_all"):
                    st.session_state["confirm_clear_history"] = False
                    st.rerun()

        for row in history:
            with st.expander(f"Question: {row[1]}"):
                st.write("**Answer:**")
                st.write(row[2])
                st.caption(f"Saved on: {row[3]}")

                if st.button("🗑️ Delete This Chat", key=f"delete_chat_{row[0]}"):
                    delete_chat(row[0])
                    st.success("Chat deleted.")
                    st.rerun()

        st.success(f"Total saved conversations: {len(history)}")

    else:
        st.info("No conversations saved yet.")
# ASSIGNMENTS AND EXAMS PAGE
elif page == "Assignments & Exams":
    st.subheader("📝 Assignment and Exam Planner")

    with st.form("assignment_form"):
        task = st.text_input("Assignment or exam name")
        due_date = st.date_input("Due date")

        task_type = st.selectbox(
            "Task type",
            ["Assignment", "Exam", "Project"],
        )

        submitted = st.form_submit_button("Save Task")

    if submitted:
        if task.strip():
            save_assignment(
                task.strip(),
                due_date.isoformat(),
                task_type,
            )
            st.success("Task saved successfully!")
        else:
            st.warning("Please enter a task name.")

    tasks = get_assignments()

    st.subheader("Saved Tasks")

    if tasks:
        st.dataframe(
            [
                {
                    "ID": row[0],
                    "Task": row[1],
                    "Due Date": row[2],
                    "Type": row[3],
                }
                for row in tasks
            ],
            use_container_width=True,
        )
    else:
        st.info("No assignments or exams saved yet.")


# STUDY RESOURCES PAGE
elif page == "Study Resources":
    st.subheader("📚 Study Resources")
    st.write("Search for tutorials and official documentation.")

    resources = [
        {
            "topic": "Python",
            "title": "Python Official Tutorial",
            "url": "https://docs.python.org/3/tutorial/",
            "description": "Learn Python basics, functions, loops, and modules."
        },
        {
            "topic": "Pandas",
            "title": "Pandas Documentation",
            "url": "https://pandas.pydata.org/docs/",
            "description": "Learn data analysis using DataFrames and Series."
        },
        {
            "topic": "NumPy",
            "title": "NumPy Documentation",
            "url": "https://numpy.org/doc/",
            "description": "Learn numerical computing and arrays."
        },
        {
            "topic": "Streamlit",
            "title": "Streamlit Documentation",
            "url": "https://docs.streamlit.io/",
            "description": "Learn to build interactive Python web applications."
        },
        {
            "topic": "AI",
            "title": "Google Machine Learning Education",
            "url": "https://developers.google.com/machine-learning",
            "description": "Explore machine learning concepts and tutorials."
        },
        {
            "topic": "NLP",
            "title": "NLTK Documentation",
            "url": "https://www.nltk.org/",
            "description": "Explore natural language processing tools for Python."
        },
        {
            "topic": "Database",
            "title": "SQLite Documentation",
            "url": "https://www.sqlite.org/docs.html",
            "description": "Learn database basics and SQL operations."
        }
    ]

    search_query = st.text_input(
        "🔍 Search Study Topics",
        placeholder="Example: Python, AI, database..."
    )

    selected_topic = st.selectbox(
        "Filter by Topic",
        ["All Topics", "Python", "Pandas", "NumPy",
         "Streamlit", "AI", "NLP", "Database"]
    )

    filtered_resources = []

    for resource in resources:
        matches_search = (
            search_query.strip().lower() in
            (
                resource["topic"] + " " +
                resource["title"] + " " +
                resource["description"]
            ).lower()
        )

        matches_topic = (
            selected_topic == "All Topics"
            or resource["topic"] == selected_topic
        )

        if matches_search and matches_topic:
            filtered_resources.append(resource)

    st.markdown(
        f"### 📖 Available Resources: {len(filtered_resources)}"
    )

    if filtered_resources:
        for resource in filtered_resources:
            with st.container(border=True):
                st.markdown(f"#### 📘 {resource['title']}")
                st.write(resource["description"])
                st.caption(f"Topic: {resource['topic']}")
                st.markdown(f"[Open Resource ↗]({resource['url']})")
    else:
        st.warning(
            "No resources found. Try another keyword or topic."
        )

# ACADEMIC PLANNER PAGE
elif page == "Academic Planner":
    from datetime import date, datetime, timedelta

    st.subheader("🎓 Academic Planner")
    st.caption("Manage assignment submissions, exams, and upcoming deadlines.")

    today = date.today()
               
    
    # MONTHLY ACADEMIC CALENDAR
    import calendar

    st.markdown("### 🗓️ Monthly Academic Calendar")

    selected_date = st.date_input(
        "Select month and year",
        value=today,
        key="academic_calendar_date"
    )

    year = selected_date.year
    month = selected_date.month

    calendar_submissions = get_submissions()
    calendar_exams = get_exams()

    events_by_date = {}

    for item in calendar_submissions:
        task_id, title, subject, due, status = item
        events_by_date.setdefault(due, []).append(
            f"📝 {title} ({status})"
        )

    for exam in calendar_exams:
        exam_id, subject, exam_date, exam_time, venue = exam
        events_by_date.setdefault(exam_date, []).append(
            f"📚 {subject} Exam"
        )

    st.markdown(
        f"#### {calendar.month_name[month]} {year}"
    )

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns(7)

    for col, day_name in zip(header_cols, weekdays):
        col.markdown(f"**{day_name}**")

    month_weeks = calendar.monthcalendar(year, month)

    for week in month_weeks:
        week_cols = st.columns(7)

        for col, day in zip(week_cols, week):
            if day == 0:
                col.write(" ")
            else:
                col.markdown(f"**{day}**")

                event_date = (
                    f"{year:04d}-{month:02d}-{day:02d}"
                )

                for event in events_by_date.get(event_date, []):
                    col.caption(event)

    st.divider()           
    
    # ACADEMIC DASHBOARD CARDS
    st.markdown("### 📊 Academic Dashboard")

    dashboard_submissions = get_submissions()
    dashboard_exams = get_exams()

    total_assignments = len(dashboard_submissions)

    submitted_assignments = sum(
        1 for item in dashboard_submissions
        if item[4] == "Submitted"
    )

    pending_assignments = sum(
        1 for item in dashboard_submissions
        if item[4] != "Submitted"
    )

    today = date.today()

    upcoming_deadlines = 0

    for item in dashboard_submissions:
        task_id, title, subject, due, status = item

        if status != "Submitted":
            try:
                if date.fromisoformat(due) >= today:
                    upcoming_deadlines += 1
            except ValueError:
                pass

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("📝 Total Assignments", total_assignments)
    col2.metric("✅ Submitted", submitted_assignments)
    col3.metric("⏳ Pending", pending_assignments)
    col4.metric("📚 Total Exams", len(dashboard_exams))
    col5.metric("📅 Upcoming Deadlines", upcoming_deadlines)

    st.divider()

    
    # SMART DEADLINE REMINDERS
    st.markdown("### 🔔 Smart Deadline Reminders")

    submissions = get_submissions()
    exams = get_exams()

    overdue = []
    due_today = []
    due_soon = []
    upcoming_exam_reminders = []

    for item in submissions:
        task_id, title, subject, due, status = item

        if status == "Submitted":
            continue

        try:
            due_day = date.fromisoformat(due)
            days_left = (due_day - today).days

            if days_left < 0:
                overdue.append(
                    f"⚠️ **{title}** ({subject}) — "
                    f"{abs(days_left)} day(s) overdue"
                )
            elif days_left == 0:
                due_today.append(
                    f"🟠 **{title}** ({subject}) — Due today!"
                )
            elif days_left <= 7:
                due_soon.append(
                    f"📝 **{title}** ({subject}) — "
                    f"Due in {days_left} day(s)"
                )
        except (ValueError, TypeError):
            continue

    for exam in exams:
        exam_id, subject, exam_date, exam_time, venue = exam

        try:
            exam_day = date.fromisoformat(exam_date)
            days_left = (exam_day - today).days

            if 0 <= days_left <= 7:
                upcoming_exam_reminders.append(
                    f"📚 **{subject}** — {exam_date}, "
                    f"{exam_time}, in {days_left} day(s)"
                )
        except (ValueError, TypeError):
            continue

    st.markdown("#### 🔴 Overdue Assignments")
    if overdue:
        for message in overdue:
            st.error(message)
    else:
        st.success("No overdue assignments.")

    st.markdown("#### 🟠 Due Today")
    if due_today:
        for message in due_today:
            st.warning(message)
    else:
        st.info("No assignments due today.")

    st.markdown("#### 🟡 Due Within 7 Days")
    if due_soon:
        for message in due_soon:
            st.warning(message)
    else:
        st.info("No upcoming assignment deadlines.")

    st.markdown("#### 📚 Upcoming Exams")
    if upcoming_exam_reminders:
        for message in upcoming_exam_reminders:
            st.info(message)
    else:
        st.info("No exams scheduled in the next 7 days.")

    st.divider()

    
    
    # Add assignment submission
    st.markdown("### 📝 Add Assignment Submission")

    with st.form("academic_submission_form", clear_on_submit=True):
        title = st.text_input("Assignment Title")
        subject = st.text_input("Subject")
        due_date = st.date_input(
            "Submission Deadline",
            value=today + timedelta(days=7),
            min_value=today,
            key="academic_due_date"
        )

        submitted = st.form_submit_button("Save Submission")

        if submitted:
            if title.strip() and subject.strip():
                save_submission(
                    title.strip(),
                    subject.strip(),
                    due_date.isoformat()
                )
                st.success("Assignment deadline saved!")
                st.rerun()
            else:
                st.warning("Please enter the assignment title and subject.")

    # Assignment status
    st.markdown("### 📋 Assignment Submission Status")

    submissions = get_submissions()

    if submissions:
        for item in submissions:
            task_id, title, subject, due, status = item

            st.write(f"**{title}** — {subject}")
            st.write(f"Deadline: {due} | Current status: {status}")

            new_status = st.selectbox(
                "Update Status",
                ["Pending", "Submitted"],
                index=0 if status == "Pending" else 1,
                key=f"academic_status_{task_id}"
            )

            if new_status != status:
                update_submission_status(task_id, new_status)
                st.rerun()

            st.divider()
    else:
        st.write("No assignment submissions added yet.")

        
    
    
    # ADVANCED ACADEMIC ANALYTICS
    st.markdown("### 📊 Advanced Academic Analytics")

    import pandas as pd

    analytics_submissions = get_submissions()
    analytics_exams = get_exams()

    total_assignments = len(analytics_submissions)

    submitted_assignments = sum(
        1 for item in analytics_submissions
        if item[4] == "Submitted"
    )

    pending_assignments = total_assignments - submitted_assignments

    completion_rate = (
        submitted_assignments / total_assignments * 100
        if total_assignments > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📝 Total Assignments", total_assignments)
    col2.metric("✅ Submitted", submitted_assignments)
    col3.metric("⏳ Pending", pending_assignments)
    col4.metric("📈 Completion Rate", f"{completion_rate:.1f}%")

    st.progress(completion_rate / 100)

    # Assignment Status Chart
    st.markdown("#### 📊 Assignment Status")

    if total_assignments > 0:
        status_data = pd.DataFrame({
            "Status": ["Submitted", "Pending"],
            "Count": [
                submitted_assignments,
                pending_assignments
            ]
        })

        st.bar_chart(
            status_data,
            x="Status",
            y="Count"
        )
    else:
        st.info("Add assignments to view assignment analytics.")

    # Subject-wise Assignment Analytics
    st.markdown("#### 📚 Subject-wise Assignments")

    if analytics_submissions:
        subject_data = pd.DataFrame([
            {
                "Subject": item[2],
                "Assignment": item[1],
                "Status": item[4]
            }
            for item in analytics_submissions
        ])

        subject_counts = (
            subject_data.groupby("Subject")
            .size()
            .reset_index(name="Assignments")
        )

        st.bar_chart(
            subject_counts,
            x="Subject",
            y="Assignments"
        )

        st.dataframe(
            subject_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No assignment data available yet.")

    # Exam Statistics
    st.markdown("#### 🗓️ Exam Statistics")

    today = date.today()
    upcoming_exam_count = 0

    for exam in analytics_exams:
        try:
            exam_day = date.fromisoformat(exam[2])

            if exam_day >= today:
                upcoming_exam_count += 1
        except (ValueError, TypeError):
            pass

    exam_col1, exam_col2 = st.columns(2)

    exam_col1.metric("📚 Total Exams", len(analytics_exams))
    exam_col2.metric("🗓️ Upcoming Exams", upcoming_exam_count)

    st.divider()

    # Add exam
    st.markdown("### 🗓️ Add Examination to Timetable")

    with st.form("academic_exam_form", clear_on_submit=True):
        exam_subject = st.text_input("Exam Subject")
        exam_date = st.date_input(
            "Exam Date",
            value=today + timedelta(days=7),
            min_value=today,
            key="academic_exam_date"
        )
        exam_time = st.time_input(
            "Exam Time",
            value=datetime.strptime("10:00", "%H:%M").time()
        )
        venue = st.text_input("Exam Venue / Room")

        exam_submitted = st.form_submit_button("Save Exam")

        if exam_submitted:
            if exam_subject.strip():
                save_exam(
                    exam_subject.strip(),
                    exam_date.isoformat(),
                    exam_time.strftime("%H:%M"),
                    venue.strip()
                )
                st.success("Exam added to timetable!")
                st.rerun()
            else:
                st.warning("Please enter the exam subject.")

    
    # EXAM SUMMARY DASHBOARD
    st.markdown("### 📊 Exam Summary Dashboard")

    exams = get_exams()
    today = date.today()

    if exams:
        upcoming_exams = []

        for exam in exams:
            exam_id, subject, exam_date, exam_time, venue = exam

            try:
                exam_day = date.fromisoformat(exam_date)

                if exam_day >= today:
                    upcoming_exams.append(exam)
            except (ValueError, TypeError):
                pass

        col1, col2, col3 = st.columns(3)

        col1.metric("📚 Total Exams", len(exams))
        col2.metric("🗓️ Upcoming Exams", len(upcoming_exams))

        if upcoming_exams:
            next_exam = min(
                upcoming_exams,
                key=lambda exam: date.fromisoformat(exam[2])
            )

            col3.metric("⏰ Next Exam", next_exam[2])

            st.info(
                f"Next exam: {next_exam[1]} "
                f"on {next_exam[2]} at {next_exam[3]}"
            )
        else:
            col3.metric("⏰ Next Exam", "None")
            st.info("No upcoming exams scheduled.")

        st.markdown("#### 📋 Subject-wise Exam Summary")

        for exam in sorted(exams, key=lambda item: item[2]):
            exam_id, subject, exam_date, exam_time, venue = exam

            st.write(
                f"📘 **{subject}** — {exam_date} "
                f"at {exam_time} | {venue or 'Venue not specified'}"
            )
    else:
        st.info("No exams added yet. Add an exam to view the summary.")

    st.divider()            

    # Display exam timetable
    st.markdown("### 📚 Examination Timetable")

    exams = get_exams()

    if exams:
        for exam in exams:
            exam_id, subject, exam_date, exam_time, venue = exam

            st.write(f"**{subject}**")
            st.write(f"Date: {exam_date}")
            st.write(f"Time: {exam_time}")
            st.write(f"Venue: {venue or 'Not specified'}")
            st.divider()
    else:
        st.write("No examinations added yet.")


    st.divider()

    # DOWNLOAD ACADEMIC PDF REPORT
    st.markdown("### 📄 Download Academic Planner Report")

    if st.button("Generate PDF Report"):
        pdf_data = create_academic_pdf(
            get_submissions(),
            get_exams()
        )

        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_data,
            file_name="Academic_Planner_Report.pdf",
            mime="application/pdf",
        )    

# ABOUT PAGE
elif page == "About":
    st.subheader("About the Project")

    st.write("""
    **Project:** AI-Powered Student Assistant

    **Objective:** Provide students with centralized academic support.

    **Technologies:** Python, Streamlit, OpenAI API and SQLite.

    **Features:**
    - AI chatbot for academic questions
    - Automatic chat history storage
    - Assignment and exam planner
    - Study resource links

    **Future Scope:**
    - Multilingual support
    - Voice assistant
    - College timetable integration
    - College Learning Management System integration
    """)