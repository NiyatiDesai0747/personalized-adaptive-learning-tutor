# Personalized Adaptive Learning Tutor

**CE509 Agentic AI • Computer DLOC Lab-I • PS No. 4**

This project implements a Personalized Adaptive Learning Tutor using a multi-agent approach. The tutor assesses the learner, creates a personalized learning path, provides teaching and practice activities, evaluates quiz performance, and selects the next learning step based on the learner's performance and stored mastery.

## Windows Setup

1. Extract the ZIP file.
2. Open the extracted **Tutor** folder.
3. Double-click **SETUP_AND_RUN.bat**.
4. The script detects Python, creates a virtual environment at `%USERPROFILE%\TutorVenv`, installs the required packages, and starts the Streamlit application.

There is no need to create or activate the virtual environment manually.

## Learner Profile Used for Testing

- **Student Name:** Niyati
- **Subject:** Python Programming
- **Level:** Beginner
- **Learning Goal:** Understand Python concepts deeply, apply them to practical problems, and improve problem-solving.
- **Existing Knowledge:** Basic Python syntax, variables, data types, and conditional statements.
- **Difficulty Areas:** Loops, functions, parameters, return values, and problem-solving.
- **Confidence:** Moderate
- **Topic:** Python Loops and Functions

## Workflow

**Learner Profile → Assessment → Learning Path → Teaching → Practice → Quiz → Evaluation & Feedback → Adaptation → Next Learning Plan → Persistent Memory → Agent Trace**

## Main Features

- Learner profile with Beginner, Intermediate, and Advanced levels
- Assessment Agent for identifying strengths, gaps, prerequisites, and readiness
- Personalized 9-stage learning path
- Teaching content based on the learner's current level
- Guided, Independent, and Challenge practice
- 20-question quiz
- Evaluation and feedback
- Concept-level mastery and question-wise error analysis
- Adaptation Agent for selecting the next learning action
- Automatic selection of the next concept based on stored mastery
- Mastered concepts are given lower priority while weaker concepts are prioritized
- Automatic routing to Teaching or Practice based on the adaptation decision
- SQLite-based persistent learning memory
- Learning history
- Multi-agent communication and decision trace
- JSON learning-state export
- Optional OpenAI API support
- Deterministic fallback when an API key is not available

## Manual Run

If Python is already installed, the application can also be run from Command Prompt:

```text
cd /d C:\path\to\Tutor
python -m venv "%USERPROFILE%\TutorVenv"
"%USERPROFILE%\TutorVenv\Scripts\python.exe" -m pip install -r requirements.txt
"%USERPROFILE%\TutorVenv\Scripts\python.exe" -m streamlit run app.py
