
import streamlit as st
import streamlit.components.v1 as components
import json
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
    initialize_timetable_table,
    save_timetable,
    get_timetable,
    delete_timetable_entry,
)

def create_timetable_exam_pdf():
    from datetime import datetime, date, timedelta

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()
    story = []

    # Project title
    story.append(Paragraph(
        "AI-Powered Student Assistant",
        styles["Title"]
    ))
    story.append(Paragraph(
        "Smart Timetable and Examination Report",
        styles["Heading2"]
    ))
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 18))

    # Timetable section
    story.append(Paragraph(
        "1. Weekly Class Timetable",
        styles["Heading2"]
    ))

    timetable = get_timetable()

    timetable_data = [[
        "Subject", "Day", "Start", "End", "Classroom"
    ]]

    for item in timetable:
        start = datetime.strptime(
            str(item[3]), "%H:%M"
        ).strftime("%I:%M %p")

        end = datetime.strptime(
            str(item[4]), "%H:%M"
        ).strftime("%I:%M %p")

        timetable_data.append([
            str(item[1]),
            str(item[2]),
            start,
            end,
            str(item[5] or "Not specified"),
        ])

    if not timetable:
        timetable_data.append([
            "No lectures added", "-", "-", "-", "-"
        ])

    timetable_table = Table(
        timetable_data,
        colWidths=[105, 75, 75, 75, 125],
        repeatRows=1,
    )

    timetable_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(timetable_table)
    story.append(Spacer(1, 22))

    # Exam section
    story.append(Paragraph(
        "2. Examination Schedule",
        styles["Heading2"]
    ))

    exams = get_exams()

    exam_data = [[
        "Subject", "Exam Date", "Time", "Venue"
    ]]

    for exam in exams:
        try:
            exam_date = datetime.strptime(
                str(exam[2]), "%Y-%m-%d"
            ).strftime("%d-%m-%Y")
        except ValueError:
            exam_date = str(exam[2])

        exam_data.append([
            str(exam[1]),
            exam_date,
            str(exam[3] or "Not specified"),
            str(exam[4] or "Not specified"),
        ])

    if not exams:
        exam_data.append([
            "No exams scheduled", "-", "-", "-"
        ])

    exam_table = Table(
        exam_data,
        colWidths=[105, 90, 85, 175],
        repeatRows=1,
    )

    exam_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B57")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(exam_table)

    doc.build(story)
    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()


def send_browser_notifications(notifications):
    import json

    payload = json.dumps(notifications)

    components.html(
        f"""
        <script>
        const reminders = {payload};

        async function showReminders() {{
            if (!("Notification" in window)) return;

            let permission = Notification.permission;

            if (permission === "default") {{
                permission = await Notification.requestPermission();
            }}

            if (permission !== "granted") return;

            const key = "student_assistant_notifications";
            const shown = JSON.parse(localStorage.getItem(key) || "[]");

            for (const item of reminders) {{
                if (!shown.includes(item.id)) {{
                    new Notification(item.title, {{ body: item.body }});
                    shown.push(item.id);
                }}
            }}

            localStorage.setItem(key, JSON.stringify(shown));
        }}

        showReminders();
        </script>
        """,
        height=0,
    )


st.set_page_config(
    page_title="AI-Powered Student Assistant",
    page_icon="🎓",
    layout="wide",
)


# BLUE-PURPLE SIDEBAR THEME
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #EEF2FF 0%,
        #EDE9FE 55%,
        #F5F3FF 100%
    );
    border-right: 1px solid #DDD6FE;
}

/* Sidebar heading */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #3730A3;
    font-weight: 700;
}

/* Sidebar text */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #373151;
}

/* Navigation spacing */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 7px;
}

/* Navigation hover effect */
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 7px 9px;
    transition: background-color 0.2s ease;
}

/* Selected navigation item */
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
}

/* Selected item text */
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: white !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #C4B5FD;
}

/* Modern Button Styling */
.stButton > button {
    border: 1px solid #C7D2FE;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #4F46E5;
    color: #4338CA;
    background-color: #EEF2FF;
    transform: translateY(-2px);
    box-shadow: 0 5px 14px rgba(79, 70, 229, 0.12);
}

/* Dashboard Layout Polish */
.welcome-banner {
    margin-bottom: 28px;
}

.home-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 155px;
    margin-bottom: 16px;
}

.section-heading {
    line-height: 1.4;
}

.section-subtitle {
    line-height: 1.6;
}

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
initialize_timetable_table()

st.title("🎓 AI-Powered Student Assistant")
st.caption("Your Smart Academic Support Platform")


# Sidebar menu
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "Home"

def go_to_page(target):
    st.session_state["selected_page"] = target

with st.sidebar:
    st.header("Student Menu")
    page = st.radio(
        "Navigate",
        [
            "Home",
            "AI Assistant",
            "AI Quiz Generator",
            "Chat History",
            "Assignments & Exams",
            "Study Resources",
            "Notes Summarizer",
            "Academic Planner",
            "Smart Timetable",
            "About",
        ],
        key="selected_page",
    )


# HOME PAGE
if page == "Home":

    # Blue-Purple Dashboard Styling
    st.markdown("""
    <style>
    .welcome-banner {
        background: linear-gradient(120deg, #312E81, #4F46E5, #7C3AED);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.20);
    }
    
.welcome-banner h1 {
    color: white;
    font-size: 32px;
    font-weight: 700;
    line-height: 1.3;
    margin: 0 0 12px 0;
    letter-spacing: -0.5px;
}

    
.welcome-banner p {
    color: #E0E7FF;
    font-size: 16px;
    line-height: 1.7;
    margin: 0;
}

    .home-card {
        padding: 22px;
        border-radius: 16px;
        color: white;
        min-height: 145px;
        margin-bottom: 12px;
    }
    .home-card .emoji {
        font-size: 28px;
    }
    .home-card .label {
        font-size: 14px;
        margin-top: 12px;
        opacity: 0.95;
    }
    .home-card .value {
        font-size: 25px;
        font-weight: bold;
        margin-top: 5px;
    }
    .home-blue {
        background: linear-gradient(135deg, #2563EB, #4F46E5);
    }
    .home-purple {
        background: linear-gradient(135deg, #7C3AED, #6D28D9);
    }
    .home-cyan {
        background: linear-gradient(135deg, #0891B2, #2563EB);
    }
    
    
    /* Professional Dashboard Improvements */
    .welcome-banner {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    
.home-card {
    padding: 24px;
    border-radius: 18px;
    color: white;
    min-height: 155px;
    margin-bottom: 14px;
    box-shadow: 0 8px 22px rgba(49, 46, 129, 0.16);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

    .home-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 26px rgba(49, 46, 129, 0.24);
    }

    .section-heading {
        color: #4F46E5;
        font-size: 24px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 18px;
    }

    </style>
    """, unsafe_allow_html=True)

    # Welcome Banner
    st.markdown("""
    <div class="welcome-banner">
        <h1>🎓 Welcome to Student Assistant!</h1>
        <p>Your smart academic companion — learn, plan and achieve more.</p>
    </div>
    """, unsafe_allow_html=True)

    # Overview Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="home-card home-blue">
            <div class="emoji">🚀</div>
            <div class="label">Platform</div>
            <div class="value">Student AI</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="home-card home-purple">
            <div class="emoji">🗄️</div>
            <div class="label">Database</div>
            <div class="value">SQLite</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="home-card home-cyan">
            <div class="emoji">🤖</div>
            <div class="label">AI Assistant</div>
            <div class="value">Available</div>
        </div>
        """, unsafe_allow_html=True)

    # Description
    st.markdown("""
    <div style="
        background: rgba(99, 102, 241, 0.07);
        border: 1px solid rgba(99, 102, 241, 0.20);
        border-radius: 14px;
        padding: 20px;
        margin-top: 12px;
    ">
        <h3 style="margin-top:0; color:#6366F1;">
            ✨ Everything you need in one place
        </h3>
        <p>
            Ask academic questions, save conversations, manage assignments,
            explore study resources and plan your studies efficiently.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # QUICK ACTIONS
    
    st.markdown(
        '<div class="section-heading">⚡ Quick Actions</div>'
        '<div class="section-subtitle">'
        'Choose a feature to get started.'
        '</div>',
        unsafe_allow_html=True
    )

    action1, action2, action3 = st.columns(3, gap="medium")

    with action1:
        st.button(
            "🤖 AI Assistant",
            use_container_width=True,
            on_click=go_to_page,
            args=("AI Assistant",),
            key="home_ai_assistant",
        )
        st.button(
            "📝 Assignments & Exams",
            use_container_width=True,
            on_click=go_to_page,
            args=("Assignments & Exams",),
            key="home_assignments",
        )

    with action2:
        st.button(
            "📚 Study Resources",
            use_container_width=True,
            on_click=go_to_page,
            args=("Study Resources",),
            key="home_resources",
        )
        st.button(
            "📅 Smart Timetable",
            use_container_width=True,
            on_click=go_to_page,
            args=("Smart Timetable",),
            key="home_timetable",
        )

    with action3:
        st.button(
            "🧠 AI Quiz Generator",
            use_container_width=True,
            on_click=go_to_page,
            args=("AI Quiz Generator",),
            key="home_quiz",
        )
        st.button(
            "📖 Notes Summarizer",
            use_container_width=True,
            on_click=go_to_page,
            args=("Notes Summarizer",),
            key="home_notes",
        )


# AI ASSISTANT PAGE
elif page == "AI Assistant":
    st.subheader("🤖 AI Chatbot")
    st.write(
        "Ask questions about Python, NumPy, Pandas, AI, "
        "programming, or your studies."
    )

    language = st.selectbox(
        "Select Answer Language",
        ["मराठी (Marathi)", "English", "हिंदी (Hindi)"]
    )

   
    def get_local_answer(question):
        q = question.lower().strip()

        answers = {
            "python": {
                "English": "Python is a beginner-friendly programming language used for web development, automation, data analysis, and AI. Example:\n\n```python\nprint('Hello, World!')\n```\nOutput: Hello, World!",
                "मराठी (Marathi)": "Python ही शिकायला सोपी programming language आहे. तिचा वापर AI, data analysis आणि automation साठी होतो.\n\n```python\nprint('Hello, World!')\n```\nOutput: Hello, World!",
                "हिंदी (Hindi)": "Python एक आसान programming language है। इसका उपयोग AI, data analysis और automation में होता है।\n\n```python\nprint('Hello, World!')\n```\nOutput: Hello, World!"
            },
            "ai": {
                "English": "Artificial Intelligence (AI) enables computers to perform tasks that normally require human intelligence, such as understanding language, recognizing patterns, and solving problems.",
                "मराठी (Marathi)": "Artificial Intelligence (AI) म्हणजे संगणकाला शिकणे, माहिती समजून घेणे आणि समस्या सोडवणे यांसारखी कामे करण्यास सक्षम करणारे तंत्रज्ञान.",
                "हिंदी (Hindi)": "Artificial Intelligence (AI) ऐसी तकनीक है जो कंप्यूटर को सीखने, भाषा समझने और समस्याएँ हल करने जैसे काम करने में सक्षम बनाती है।"
            },
            "pandas": {
                "English": "Pandas is a Python library used to organize, analyze, and manipulate data in tables called DataFrames.\n\n```python\nimport pandas as pd\ndata = {'Name': ['Riya', 'Asha'], 'Marks': [80, 90]}\ndf = pd.DataFrame(data)\nprint(df)\n```",
                "मराठी (Marathi)": "Pandas ही Python library आहे. तिचा वापर tabular data व्यवस्थित करण्यासाठी आणि त्याचे analysis करण्यासाठी होतो. DataFrame मध्ये data rows आणि columns मध्ये ठेवता येतो.",
                "हिंदी (Hindi)": "Pandas एक Python library है जिसका उपयोग tabular data को व्यवस्थित करने और उसका analysis करने के लिए किया जाता है।"
            },
            "numpy": {
                "English": "NumPy is a Python library used for numerical calculations and working efficiently with arrays.",
                "मराठी (Marathi)": "NumPy ही Python library आहे. तिचा वापर numerical calculations आणि arrays वर जलद प्रक्रिया करण्यासाठी होतो.",
                "हिंदी (Hindi)": "NumPy एक Python library है जिसका उपयोग numerical calculations और arrays पर काम करने के लिए होता है।"
            },
            "nlp": {
                "English": "Natural Language Processing (NLP) helps computers process, understand, and respond to human language. It is used in chatbots and language translation.",
                "मराठी (Marathi)": "Natural Language Processing (NLP) हे तंत्रज्ञान संगणकाला मानवी भाषा समजून घेण्यास आणि त्यावर प्रक्रिया करण्यास मदत करते. Chatbots मध्ये याचा वापर होतो.",
                "हिंदी (Hindi)": "Natural Language Processing (NLP) कंप्यूटर को मानवीय भाषा समझने और उस पर काम करने में मदद करता है। इसका उपयोग chatbots में होता है।"
            },
            "study": {
                "English": "Study tips:\n1. Make a daily study timetable.\n2. Divide topics into small sections.\n3. Practise questions regularly.\n4. Take short breaks.\n5. Revise important concepts before exams.",
                "मराठी (Marathi)": "अभ्यासासाठी टिप्स:\n1. रोजचे study timetable बनवा.\n2. मोठे topics छोट्या भागांत विभागा.\n3. नियमित प्रश्न सोडवा.\n4. मध्ये थोडी विश्रांती घ्या.\n5. परीक्षेपूर्वी महत्त्वाच्या संकल्पनांची उजळणी करा.",
                "हिंदी (Hindi)": "पढ़ाई के लिए सुझाव:\n1. रोज़ का timetable बनाएँ।\n2. बड़े topics को छोटे भागों में बाँटें।\n3. नियमित प्रश्न हल करें।\n4. बीच में छोटे breaks लें।\n5. परीक्षा से पहले revision करें।"
            }
        }


        if "pandas" in q:
            topic = "pandas"
        elif "numpy" in q:
            topic = "numpy"
        elif "nlp" in q or "natural language processing" in q:
            topic = "nlp"
        elif any(word in q for word in [
            "artificial intelligence",
            "what is ai",
            " ai",
            "कृत्रिम बुद्धिमत्ता"
        ]):
            topic = "ai"
        elif any(word in q for word in [
            "study tips", "study plan", "अभ्यास", "पढ़ाई"
        ]):
            topic = "study"
        elif "python" in q or "पायथन" in q:
            topic = "python"
        else:
            if language == "मराठी (Marathi)":
                return "या प्रश्नाचे उत्तर सध्याच्या knowledge base मध्ये नाही. कृपया Python, AI, Pandas, NumPy, NLP किंवा अभ्यासाच्या टिप्स याबद्दल विचारा."
            elif language == "हिंदी (Hindi)":
                return "इस प्रश्न का उत्तर वर्तमान knowledge base में नहीं है। कृपया Python, AI, Pandas, NumPy, NLP या पढ़ाई से संबंधित प्रश्न पूछें।"
            return "I don't have an answer for this question in my current knowledge base. Try asking about Python, AI, Pandas, NumPy, NLP, or study tips."

        return answers[topic].get(language, answers[topic]["English"])


    # Display saved conversations
    for row in reversed(get_chat_history()):
        with st.chat_message("user"):
            st.write(row[1])
        with st.chat_message("assistant"):
            st.write(row[2])

    question = st.chat_input("Ask your academic question...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        answer = get_local_answer(question)

        with st.chat_message("assistant"):
            st.markdown(answer)

        save_chat(question, answer)

# AI QUIZ GENERATOR PAGE
elif page == "AI Quiz Generator":
    import json
    import requests

    st.subheader("📝 AI Quiz Generator")
    st.write("Generate a multiple-choice quiz for your studies.")

    topic = st.text_input(
        "Enter a topic",
        placeholder="Example: Python Basics"
    )

    quiz_language = st.selectbox(
        "Quiz language",
        ["English", "मराठी (Marathi)", "हिंदी (Hindi)"]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    question_count = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("Generate Quiz", key="generate_ai_quiz"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            language_rule = {
                "English": "Write in simple English.",
                "मराठी (Marathi)": (
                    "Write in simple Marathi using Devanagari script."
                ),
                "हिंदी (Hindi)": (
                    "Write in simple Hindi using Devanagari script."
                ),
            }[quiz_language]

            prompt = f"""
Create exactly {question_count} educational multiple-choice questions.
Topic: {topic}
Difficulty: {difficulty}
Language: {language_rule}

Return only valid JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": "Exact correct option",
      "explanation": "Short explanation"
    }}
  ]
}}

Every question must have four options.
The answer must exactly match one option.
Do not repeat questions.
"""


        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                params={"key": api_key},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 1200
                    }
                },
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            answer = (
                data["candidates"][0]["content"]["parts"][0]["text"]
                .strip()
            )
        except KeyError:
            st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
        except Exception as e:
            st.error(f"Quiz generation failed: {e}")
     
    # Display generated quiz
    questions = st.session_state.get("ai_quiz_questions", [])

    if questions:
        st.divider()
        st.subheader(
            f"Quiz: {st.session_state.get('ai_quiz_topic', '')}"
        )

        with st.form("ai_quiz_answer_form"):
            answers = []

            for i, item in enumerate(questions):
                st.markdown(f"**Q{i + 1}. {item.get('question', '')}**")
                options = item.get("options", [])

                if len(options) == 4:
                    selected = st.radio(
                        "Select an answer",
                        options,
                        index=None,
                        key=f"ai_quiz_answer_{i}",
                        label_visibility="collapsed"
                    )
                    answers.append(selected)
                else:
                    st.warning(f"Question {i + 1} has invalid options.")
                    answers.append(None)

            submitted = st.form_submit_button("Submit Answers")

        if submitted:
            score = sum(
                1 for item, selected in zip(questions, answers)
                if selected is not None
                and selected == item.get("answer")
            )
            st.session_state["ai_quiz_score"] = score

        if "ai_quiz_score" in st.session_state:
            score = st.session_state["ai_quiz_score"]
            st.success(f"Your Score: {score} / {len(questions)}")

            for i, item in enumerate(questions):
                st.markdown(f"**Q{i + 1}. Correct Answer:**")
                st.write(item.get("answer", "Not available"))
                st.write(
                    "Explanation: "
                    + item.get("explanation", "No explanation available.")
                )



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


# NOTES UPLOAD AND AI SUMMARIZER PAGE
elif page == "Notes Summarizer":
    import requests
    from pypdf import PdfReader
    from io import BytesIO

    st.subheader("📚 Notes Upload & AI Summarizer")
    st.write(
        "Upload your PDF study notes to generate a summary "
        "and important revision points."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF Notes",
        type=["pdf"],
        key="notes_pdf_upload"
    )

    summary_language = st.selectbox(
        "Select Summary Language",
        ["English", "मराठी (Marathi)", "हिंदी (Hindi)"],
        key="notes_summary_language"
    )

    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("Please upload a PDF smaller than 10 MB.")

        else:
            if st.button("✨ Generate Summary", key="generate_notes_summary"):
                try:
                    with st.spinner("Reading your PDF notes..."):
                        pdf_reader = PdfReader(
                            BytesIO(uploaded_file.getvalue())
                        )

                        if pdf_reader.is_encrypted:
                            st.error(
                                "This PDF is password-protected. "
                                "Please upload an unlocked PDF."
                            )
                        else:
                            pages_text = []

                            for pdf_page in pdf_reader.pages:
                                pages_text.append(
                                    pdf_page.extract_text() or ""
                                )

                            document_text = "\n".join(pages_text).strip()

                            if not document_text:
                                st.error(
                                    "No readable text found. "
                                    "Scanned PDFs may need OCR first."
                                )

                            elif len(document_text) > 20000:
                                st.warning(
                                    "Only the first 20,000 characters "
                                    "will be summarized."
                                )
                                document_text = document_text[:20000]

                            if document_text:
                                language_rule = {
                                    "English": "Write in clear English.",
                                    "मराठी (Marathi)": (
                                        "Write in simple Marathi using "
                                        "Devanagari script."
                                    ),
                                    "हिंदी (Hindi)": (
                                        "Write in simple Hindi using "
                                        "Devanagari script."
                                    ),
                                }[summary_language]

                                prompt = f"""
You are a helpful study assistant.

Summarize the following student notes.
{language_rule}

Use these headings:
1. Short Summary
2. Important Points
3. Key Terms
4. Quick Revision

Use only information supported by the notes.
Do not invent facts. Keep the language simple.

PDF NOTES:
{document_text}

SUMMARY:
"""

                                with st.spinner("AI is summarizing your notes..."):
                                    response = requests.post(
                                        "http://localhost:11434/api/generate",
                                        json={
                                            "model": "llama3.2:latest",
                                            "prompt": prompt,
                                            "stream": False,
                                            "options": {
                                                "temperature": 0.2,
                                                "num_predict": 1000,
                                                "repeat_penalty": 1.2
                                            }
                                        },
                                        timeout=300
                                    )

                                    response.raise_for_status()
                                    summary = response.json().get(
                                        "response", ""
                                    ).strip()

                                if summary:
                                    st.session_state["notes_summary"] = summary
                                    st.session_state["notes_filename"] = (
                                        uploaded_file.name
                                    )
                                else:
                                    st.error(
                                        "No summary generated. Please try again."
                                    )

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Ollama is not running. Please start Ollama."
                    )
                except requests.exceptions.Timeout:
                    st.error(
                        "The AI took too long. Please try again."
                    )
                except Exception as e:
                    st.error(f"Could not process the PDF: {e}")

    if st.session_state.get("notes_summary"):
        st.divider()
        st.subheader("📖 Your Study Summary")
        st.caption(
            "File: "
            + st.session_state.get("notes_filename", "Uploaded PDF")
        )
        st.markdown(st.session_state["notes_summary"])

        st.download_button(
            "⬇️ Download Summary",
            data=st.session_state["notes_summary"],
            file_name="study_summary.txt",
            mime="text/plain",
            key="download_notes_summary"
        )


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
    
    
    # Modern Blue-Purple Academic Dashboard Cards
    st.markdown("""
    <style>
    .academic-card {
        padding: 20px;
        border-radius: 16px;
        color: white;
        min-height: 125px;
        margin-bottom: 14px;
        box-shadow: 0 5px 15px rgba(50,50,100,0.15);
    }
    .academic-label {
        font-size: 14px;
        opacity: 0.95;
    }
    .academic-value {
        font-size: 32px;
        font-weight: bold;
        margin-top: 10px;
    }
    .academic-blue {
        background: linear-gradient(135deg,#2563EB,#4F46E5);
    }
    .academic-purple {
        background: linear-gradient(135deg,#7C3AED,#6D28D9);
    }
    .academic-cyan {
        background: linear-gradient(135deg,#0891B2,#2563EB);
    }
    .academic-pink {
        background: linear-gradient(135deg,#9333EA,#DB2777);
    }
    .academic-indigo {
        background: linear-gradient(135deg,#4338CA,#7C3AED);
    }
    
    </style>
    """, unsafe_allow_html=True)

    total_assignments = 0
    submitted_assignments = 0
    pending_assignments = 0
    upcoming_deadlines = 0

    st.markdown("""
    <h2 style="color:#6366F1;">📊 Academic Overview</h2>
    <p style="color:#64748B;">
        Track your academic progress in one place.
    </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="academic-card academic-blue">
            <div style="font-size:25px;">📝</div>
            <div class="academic-label">Total Assignments</div>
            <div class="academic-value">{total_assignments}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="academic-card academic-purple">
            <div style="font-size:25px;">✅</div>
            <div class="academic-label">Submitted</div>
            <div class="academic-value">{submitted_assignments}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="academic-card academic-cyan">
            <div style="font-size:25px;">⏳</div>
            <div class="academic-label">Pending</div>
            <div class="academic-value">{pending_assignments}</div>
        </div>
        """, unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.markdown(f"""
        <div class="academic-card academic-pink">
            <div style="font-size:25px;">📚</div>
            <div class="academic-label">Total Exams</div>
            <div class="academic-value">{len(get_exams())}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="academic-card academic-indigo">
            <div style="font-size:25px;">📅</div>
            <div class="academic-label">Upcoming Deadlines</div>
            <div class="academic-value">{upcoming_deadlines}</div>
        </div>
        """, unsafe_allow_html=True)

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

     

# SMART TIMETABLE PAGE
elif page == "Smart Timetable":
    import pandas as pd
    from datetime import datetime

    st.title("📅 Smart Timetable")

    st.write("Create and manage your weekly class timetable.")

    with st.form("timetable_form"):
        subject = st.text_input("Subject Name")
        day = st.selectbox(
            "Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
        )

    st.write("Create and manage your weekly class timetable.")


    with st.form("weekly_timetable_form"):
        subject = st.text_input("Subject Name")
        day = st.selectbox(
            "Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
        )

        col1, col2 = st.columns(2)

        with col1:
            start_time = st.time_input(
                "Start Time",
                value=datetime.strptime("09:00", "%H:%M").time()
            )

        with col2:
            end_time = st.time_input(
                "End Time",
                value=datetime.strptime("10:00", "%H:%M").time()
            )

        classroom = st.text_input("Classroom / Lab")

        submitted = st.form_submit_button("➕ Add Lecture")

    if submitted:
        if not subject.strip():
            st.warning("OSY.")
        elif end_time <= start_time:
            st.error("End time must be after start time.")
        else:
            existing = get_timetable()

            overlap = any(
                item[2] == day
                and start_time.strftime("%H:%M") < item[4]
                and end_time.strftime("%H:%M") > item[3]
                for item in existing
            )

            if overlap:
                st.error("⚠️ This lecture overlaps with an existing lecture.")
            else:
                save_timetable(
                    subject.strip(),
                    day,
                    start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M"),
                    classroom.strip()
                )
                st.success("Lecture added successfully!")
                st.rerun()

    st.subheader("📚 Weekly Class Schedule")

    timetable = get_timetable()

    if timetable:
        df = pd.DataFrame(
            timetable,
            columns=[
                "ID", "Subject", "Day",
                "Start Time", "End Time", "Classroom"
            ]
        )

        
        df["Start Time"] = pd.to_datetime(
            df["Start Time"], format="%H:%M"
        ).dt.strftime("%I:%M %p")

        df["End Time"] = pd.to_datetime(
            df["End Time"], format="%H:%M"
        ).dt.strftime("%I:%M %p")

        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.drop(columns=["ID"]).to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Timetable CSV",
            data=csv_data,
            file_name="smart_timetable.csv",
            mime="text/csv"
        )

        lecture_id = st.selectbox(
            "Select lecture to delete",
            df["ID"].tolist(),
            format_func=lambda x: (
                f"{df.loc[df['ID'] == x, 'Subject'].iloc[0]} - "
                f"{df.loc[df['ID'] == x, 'Day'].iloc[0]}"
            )
        )

        if st.button("🗑️ Delete Selected Lecture"):
            delete_timetable_entry(lecture_id)
            st.success("Lecture deleted.")
            st.rerun()
    else:
        st.info("No lectures added yet. Add your first lecture above.")


    # LECTURE AND EXAM REMINDERS
    from datetime import date, timedelta

    st.divider()
    st.subheader("🔔 Lecture & Exam Reminders")

    
    # Today's lectures
    st.markdown("### 📚 Today's Lectures")

    now = datetime.now()
    today_date = date.today()
    today_name = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    all_lectures = get_timetable()
    browser_reminders = []

    today_lectures = [
        lecture for lecture in all_lectures
        if lecture[2] == today_name
    ]

    if today_lectures:
        for lecture in today_lectures:
            start_dt = datetime.combine(
                today_date,
                datetime.strptime(lecture[3], "%H:%M").time()
            )

            end_dt = datetime.combine(
                today_date,
                datetime.strptime(lecture[4], "%H:%M").time()
            )

            seconds_left = (start_dt - now).total_seconds()

            st.write(
                f"📘 **{lecture[1]}** | "
                f"{start_dt.strftime('%I:%M %p')} – "
                f"{end_dt.strftime('%I:%M %p')} | "
                f"Room: {lecture[5] or 'Not specified'}"
            )

            if 0 < seconds_left <= 15 * 60:
                minutes_left = max(1, int(seconds_left // 60))

                st.warning(
                    f"🔔 Reminder: {lecture[1]} starts in "
                    f"{minutes_left} minute(s)!"
                )

                browser_reminders.append({
                    "id": f"lecture-{lecture[0]}-{today_date.isoformat()}",
                    "title": "Lecture Reminder",
                    "body": f"{lecture[1]} starts in "
                            f"{minutes_left} minute(s)."
                })

            elif start_dt <= now < end_dt:
                st.success(f"📖 {lecture[1]} lecture is ongoing.")

    else:
        st.info("No lectures scheduled for today.")

   
    # Upcoming exams
    st.markdown("### 📝 Upcoming Exams")

    today_date = date.today()
    next_week = today_date + timedelta(days=7)
    exams = get_exams()
    found_exam = False

    for exam in exams:
        try:
            exam_date = date.fromisoformat(str(exam[2]))

            # Exam reminder: 3 days before
            if (exam_date - today_date).days == 3:
                browser_reminders.append({
                    "id": f"exam-{exam[0]}-{exam_date.isoformat()}",
                    "title": "Exam Reminder",
                    "body": f"{exam[1]} exam is in 3 days."
                })

            if today_date <= exam_date <= next_week:
                found_exam = True
                days_left = (exam_date - today_date).days

                if days_left == 0:
                    message = "⚠️ Exam is today!"
                elif days_left == 1:
                    message = "⏰ Exam is tomorrow!"
                else:
                    message = f"📅 Exam in {days_left} days."

                st.warning(
                    f"**{exam[1]}** — "
                    f"{exam_date.strftime('%d-%m-%Y')} at {exam[3]} "
                    f"| Venue: {exam[4] or 'Not specified'}\n\n"
                    f"{message}"
                )

        except (ValueError, TypeError):
            st.caption(f"Invalid exam date for {exam[1]}.")




    if not found_exam:
        st.info("No exams scheduled in the next 7 days.")

    send_browser_notifications(browser_reminders)


    st.divider()
    st.subheader("📄 Download PDF Report")

    try:
        pdf_data = create_timetable_exam_pdf()

        st.download_button(
            label="⬇️ Download Timetable & Exams PDF",
            data=pdf_data,
            file_name="Student_Timetable_Exam_Report.pdf",
            mime="application/pdf",
            key="download_timetable_exam_pdf",
        )

        st.caption(
            "Your PDF contains the weekly timetable and exam schedule."
        )

    except Exception as e:
        st.error(f"Could not generate PDF: {e}")

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