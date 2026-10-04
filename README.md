# 🎓 Personalized Adaptive Learning Tutor — FINAL CLEAN BUILD

**CE509 Agentic AI • Computer DLOC Lab-I • PS No. 4**

This project implements a Personalized Adaptive Learning Tutor using a multi-agent approach. The tutor assesses the learner, creates a personalized learning path, provides teaching and practice activities, evaluates quiz performance, and selects the next learning step based on the learner's performance and stored mastery.

## Windows setup — easiest method

1. Extract the ZIP.
2. Open the extracted **Tutor** folder.
3. Double-click **SETUP_AND_RUN.bat**.
4. The script automatically detects `python` (and falls back to `py` if available), creates the clean environment at `%USERPROFILE%\TutorVenv`, installs the requirements, and starts Streamlit.

You do **not** need to create or activate a virtual environment manually.

## Final learner profile

- **Student Name:** Niyati
- **Subject:** Python Programming
- **Current Level:** Beginner
- **Learning Goal:** Understand Python concepts deeply, apply them to practical problems, and improve problem-solving.
- **Current knowledge / struggle:** I know basic Python syntax, variables, data types, and conditional statements. I struggle with loops, functions, parameters, return values, and applying concepts to problem-solving.
- **Confidence:** Moderate
- **Topic:** Python Loops and Functions

## Complete workflow

**Learner Profile → Assessment → Personalized 9-Stage Path → Level-Adaptive Teaching → Guided/Independent/Challenge Practice → 20-Question Quiz → Evaluation & Feedback → Adaptation → Automatic Next Plan → Persistent Memory → Agent Trace → Continue**

## Included features

- Learner profile with Beginner / Intermediate / Advanced levels
- Assessment Agent with strengths, gaps, prerequisites, readiness and recommended start
- Personalized 9-stage Learning Path Agent driven by stored mastery
- **Real level-adaptive teaching content**
  - Beginner: simple explanations, basic examples, guided checks
  - Intermediate: deeper concepts, practical combinations, trade-offs and edge cases
  - Advanced: engineering reasoning, edge cases, alternative approaches and challenging transfer
- Changing learner level regenerates teaching content instead of reusing the old lesson
- Guided → Independent → Challenge Practice Agent
- Exactly 20-question adaptive Quiz Agent
- Evaluation & Feedback Agent
- Concept-level mastery updates and question-wise error analysis
- Adaptation Agent
- **Automatic next-plan selection from stored mastery**
- Mastered concepts are deprioritized; weaker concepts are selected for remediation/practice
- **Automatic routing after Apply Adaptive Decision**
  - Remediation / Acceleration → Teaching Agent for the next concept
  - Targeted Practice → Practice Agent
- Teaching page automatically opens the selected adaptive concept and current learner level
- Persistent SQLite Learning Memory
- Learning History
- Multi-Agent Communication & Decision Trace
- JSON learning-state export
- Optional OpenAI API enhancement with deterministic fallback
- No API key required for the deterministic lab demonstration

## Manual run

If you prefer CMD and already have Python installed:

```bat
cd /d C:\path\to\Tutor
python -m venv "%USERPROFILE%\TutorVenv"
"%USERPROFILE%\TutorVenv\Scripts\python.exe" -m pip install -r requirements.txt
"%USERPROFILE%\TutorVenv\Scripts\python.exe" -m streamlit run app.py
```

## Important

Do not include a real API key in the ZIP or commit one to GitHub.
