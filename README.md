
# 🎓 AI-Powered Student Assistant

### Your Smart Academic Support Platform

## 📌 Project Overview

AI-Powered Student Assistant is a student support application
developed using Python and Streamlit. It provides a centralized
platform where students can access basic academic information,
review study notes, track assignments, and view saved chatbot
conversations.

The application uses a rule-based chatbot that responds to
supported questions using predefined answers. SQLite is used
to store chat history and assignment information.

## 🎯 Objectives

- Provide a simple academic support platform.
- Answer common questions related to computer science.
- Save chatbot conversations for future reference.
- Help students organize assignments and exam tasks.
- Provide basic study notes in one place.
- Develop an easy-to-use web interface for students.

## ✨ Key Features

### 1. AI Assistant
- Answers supported questions about Python, NumPy, Pandas,
  Artificial Intelligence, Machine Learning, and NLP.
- Uses predefined responses without requiring paid API credits.
- Displays a helpful message for unsupported questions.

### 2. Chat History
- Saves questions and answers in an SQLite database.
- Displays previously saved conversations.
- Helps students review earlier interactions.

### 3. Assignments & Exams
- Provides an interface for managing assignment and exam tasks.
- Uses the application's assignment storage functionality.

### 4. Study Resources
- Provides basic notes on computer science topics.
- Allows students to select a topic.
- Supports downloading notes as text files.

### 5. About Page
- Displays project information.
- Describes the application's purpose and technologies.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| SQLite | Local database |
| SQL | Database operations |
| Markdown | Project documentation |

## 🏗️ System Architecture

1. The student opens the Streamlit application.
2. The student selects a feature from the sidebar.
3. The selected module processes the request.
4. The chatbot provides a predefined answer for supported questions.
5. Chat and assignment information is stored in SQLite.
6. The application displays the result to the student.

## 📁 Project Structure

AI-Powered Student Assistant Project/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── student_assistant.db
└── .streamlit/
    └── secrets.toml

Note: student_assistant.db is created by the application.
The .streamlit/secrets.toml file is optional for the
current basic chatbot and should not contain public secrets
when sharing the project.

## ⚙️ Requirements

- Python 3.10 or a compatible installed Python version
- pip package manager
- Visual Studio Code (recommended)
- A web browser

## 🚀 Installation and Setup

### Step 1: Open the project folder

Open the project folder in Visual Studio Code.

### Step 2: Open the terminal

Select Terminal → New Terminal.

### Step 3: Activate the virtual environment

On Windows PowerShell, run:

.\venv\Scripts\Activate.ps1

If the virtual environment does not exist, create it:

python -m venv venv

Then activate it using the command above.

### Step 4: Install dependencies

If requirements.txt is available, run:

pip install -r requirements.txt

Otherwise, install Streamlit:

pip install streamlit

### Step 5: Run the application

Run:

streamlit run app.py

### Step 6: Open the application

Open the local URL displayed in the terminal.
For example:

http://localhost:8501

Use the exact URL shown by Streamlit if a different port
is assigned.

## 🧪 Testing

The following features have been tested during development:

| Test Case | Expected Result |
|---|---|
| Ask a supported chatbot question | A predefined answer appears |
| Save a conversation | Question and answer are stored |
| Open Chat History | Saved conversations are displayed |
| Open Assignments & Exams | Assignment interface is displayed |
| Open Study Resources | Study notes are displayed |
| Download notes | A text file is downloaded |
| Open About Page | Project information is displayed |

## 🔐 Privacy and Security

- Chat history is stored in a local SQLite database.
- Keep database files private if they contain personal information.
- Do not upload API keys, passwords, or private credentials.
- Keep secrets.toml out of public repositories.
- Add .streamlit/secrets.toml to .gitignore if it exists.

## ⚠️ Limitations

- The chatbot responds only to supported questions and
  predefined rules.
- It does not generate unrestricted answers like a full
  generative AI model.
- Study notes are basic and may need to be expanded.
- Local SQLite data is not automatically shared between
  different computers.
- Timetable information is not automatically retrieved
  from a college system.

## 🔮 Future Scope

- Integrate a suitable AI language model.
- Add multilingual support for Marathi, Hindi, and English.
- Add voice-based questions and answers.
- Integrate college timetable and syllabus information.
- Add notifications for upcoming assignments and exams.
- Develop a mobile-friendly application.
- Add student login and access controls.

## ✅ Advantages

- Simple and user-friendly interface.
- Centralized access to basic academic resources.
- Local storage of conversation history.
- No paid API credits required for the basic chatbot.
- Useful for learning Python, Streamlit, and SQLite.

## 🎓 Conclusion

The AI-Powered Student Assistant provides a simple platform
for basic academic support. It combines a rule-based chatbot,
saved conversation history, assignment management, and study
resources in one application.

The project demonstrates the practical use of Python,
Streamlit, and SQLite in developing a student-oriented
web application. Future enhancements can make the system
more intelligent and feature-rich.

## 👩‍💻 Project Information

Project Title: AI-Powered Student Assistant

Project Type: Academic Project

Developer: Riya Devhade

## 📚 References

- Python Documentation: https://docs.python.org/3/
- Streamlit Documentation: https://docs.streamlit.io/
- SQLite Documentation: https://www.sqlite.org/docs.html/
- Pandas Documentation: https://pandas.pydata.org/docs/
- NumPy Documentation: https://numpy.org/doc/

---

**Developed as an academic project for student support.**