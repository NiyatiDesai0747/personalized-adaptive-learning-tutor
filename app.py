import json
import os
import random
import sqlite3
import textwrap
from datetime import datetime
from pathlib import Path

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "learning_memory.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Personalized Adaptive Learning Tutor", page_icon="🎓", layout="wide")

# -----------------------------
# Persistence
# -----------------------------

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS learners (
        learner_id TEXT PRIMARY KEY,
        profile_json TEXT NOT NULL,
        mastery_json TEXT NOT NULL,
        history_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def learner_key(name, subject):
    return f"{name.strip().lower()}::{subject.strip().lower()}"


def load_memory(name, subject):
    key = learner_key(name, subject)
    with db() as conn:
        row = conn.execute("SELECT * FROM learners WHERE learner_id=?", (key,)).fetchone()
    if not row:
        return {"mastery": {}, "history": [], "profile": {}}
    return {
        "mastery": json.loads(row["mastery_json"]),
        "history": json.loads(row["history_json"]),
        "profile": json.loads(row["profile_json"]),
    }


def save_memory(profile, mastery, history):
    key = learner_key(profile["name"], profile["subject"])
    now = datetime.now().isoformat(timespec="seconds")
    with db() as conn:
        conn.execute("""INSERT INTO learners(learner_id, profile_json, mastery_json, history_json, updated_at)
        VALUES(?,?,?,?,?) ON CONFLICT(learner_id) DO UPDATE SET
        profile_json=excluded.profile_json, mastery_json=excluded.mastery_json,
        history_json=excluded.history_json, updated_at=excluded.updated_at""",
                     (key, json.dumps(profile), json.dumps(mastery), json.dumps(history), now))
        conn.commit()


def trace(agent, summary, payload=None):
    event = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "agent": agent,
        "summary": summary,
        "payload": payload or {},
    }
    st.session_state.trace.append(event)
    return event

# -----------------------------
# Topic knowledge engine
# -----------------------------
PYTHON_CONCEPTS = [
    "Variables", "Data Types", "Conditions", "Loops", "Functions", "Parameters",
    "Return Values", "Scope", "Debugging", "Problem Solving", "Application"
]

PYTHON_DETAILS = {
    "Variables": {
        "meaning": "A variable is a name that refers to a value. In Python, assignment binds a name to an object; the value can later be replaced with another object.",
        "why": "Variables let a program remember information and give meaningful names to values instead of repeating raw data.",
        "syntax": "age = 21\nname = 'Niyati'",
        "examples": ["Store a student's marks", "Keep a running total", "Store a user's name before displaying a message"],
        "misconceptions": ["A variable is not a box with a permanent type in Python.", "Assignment does not mean comparison; = assigns while == compares."],
        "debug": "If a variable seems wrong, print its value and type, then check where it was last assigned.",
        "application": "In a shopping program, total_price can store the current bill while the program adds item prices.",
    },
    "Data Types": {
        "meaning": "A data type describes the kind of value a program is working with and the operations that make sense for that value.",
        "why": "Choosing and understanding types prevents invalid operations and helps you model information correctly.",
        "syntax": "count = 10\nprice = 99.5\nname = 'Niyati'\nactive = True",
        "examples": ["int for counts", "float for measurements", "str for text", "bool for yes/no state"],
        "misconceptions": ["A string containing '10' is not the same as the integer 10.", "Type conversion should be intentional because not every conversion is valid."],
        "debug": "Use type(value) and small isolated tests when an operation behaves unexpectedly.",
        "application": "A sensor dashboard might store temperature as float, device_id as str and online status as bool.",
    },
    "Conditions": {
        "meaning": "Conditional statements choose which block of code runs based on whether a Boolean expression is true or false.",
        "why": "They allow programs to make decisions instead of following exactly the same path every time.",
        "syntax": "if marks >= 40:\n    result = 'Pass'\nelse:\n    result = 'Fail'",
        "examples": ["Validate a password", "Check whether a number is positive", "Choose a delivery fee based on order amount"],
        "misconceptions": ["The condition must produce a truth value.", "elif is checked only after previous conditions are false."],
        "debug": "Print the condition's inputs and test boundary values such as 39, 40 and 41 when the rule is marks >= 40.",
        "application": "A cloud monitor can alert when CPU utilization crosses a defined threshold.",
    },
    "Loops": {
        "meaning": "A loop repeats a block of code. A for loop is commonly used to iterate over items or a range; a while loop repeats while a condition remains true.",
        "why": "Loops automate repeated work and are essential for processing collections, retrying operations and traversing data.",
        "syntax": "for item in items:\n    print(item)\n\nwhile attempts < 3:\n    attempts += 1",
        "examples": ["Process every student mark", "Print numbers 1–10", "Retry a task a limited number of times"],
        "misconceptions": ["A for loop does not automatically mean a fixed number of repetitions; it depends on the iterable.", "A while loop needs a condition that eventually becomes false or it may never terminate."],
        "debug": "For an unexpected loop, inspect the iterable/condition, update variables, and test the smallest failing input.",
        "application": "A monitoring service can iterate through devices and check the status of each device.",
    },
    "Functions": {
        "meaning": "A function is a named, reusable block of logic that can receive inputs and optionally return an output.",
        "why": "Functions reduce repetition, isolate responsibilities, improve testing and make larger programs easier to reason about.",
        "syntax": "def add(a, b):\n    return a + b",
        "examples": ["Calculate a bill", "Validate a username", "Convert temperature", "Fetch and format device status"],
        "misconceptions": ["Defining a function does not execute its body; calling it does.", "A parameter is a name in the function definition, while an argument is a value supplied at the call."],
        "debug": "Check whether the function is called, whether arguments match the parameters, and whether the returned value is used.",
        "application": "A web application can use separate functions for authentication, validation, calculation and response formatting.",
    },
    "Parameters": {
        "meaning": "Parameters are names in a function definition that receive values when the function is called.",
        "why": "Parameters make functions reusable with different inputs instead of hard-coding one case.",
        "syntax": "def greet(name, message='Hello'):\n    return f'{message}, {name}'",
        "examples": ["Pass a quantity to a calculation", "Pass a username to a greeting", "Pass a threshold to a monitoring function"],
        "misconceptions": ["Parameter names belong to the function definition; arguments are the supplied values.", "Default parameters are used when the caller does not supply that argument."],
        "debug": "Read the function signature and compare the number, order and names of supplied arguments.",
        "application": "A reusable alert function can accept device_id, metric_value and threshold as parameters.",
    },
    "Return Values": {
        "meaning": "The return statement sends a value from a function back to its caller and immediately exits that function.",
        "why": "Returning values lets one function produce a result that another part of the program can use.",
        "syntax": "def square(x):\n    return x * x\n\nresult = square(5)",
        "examples": ["Return a calculated total", "Return True/False after validation", "Return a formatted result"],
        "misconceptions": ["print() displays a value; return passes a value to the caller.", "A function without an explicit return returns None."],
        "debug": "If a result is None, inspect whether the function actually returns the value on every required path.",
        "application": "A validation function can return a Boolean so another function can decide whether to continue.",
    },
    "Scope": {
        "meaning": "Scope determines where a name can be accessed. Python commonly uses local, enclosing, global and built-in namespaces (LEGB lookup).",
        "why": "Understanding scope prevents accidental name conflicts and explains why a variable may not be available in a particular location.",
        "syntax": "x = 'global'\ndef demo():\n    x = 'local'\n    return x",
        "examples": ["Keep a temporary loop variable local", "Use a function-local calculation", "Avoid changing global state unnecessarily"],
        "misconceptions": ["A local variable created inside a function is not automatically available outside it.", "Using global variables everywhere can make programs harder to test and reason about."],
        "debug": "Read the location where a name is defined and trace Python's LEGB lookup before changing code.",
        "application": "Keeping request-specific state local prevents one user's operation from accidentally changing another's data.",
    },
    "Debugging": {
        "meaning": "Debugging is the systematic process of finding, understanding and fixing the cause of incorrect program behavior.",
        "why": "Good debugging turns vague failures into small, testable hypotheses instead of random code changes.",
        "syntax": "value = calculate_total(items)\nprint('DEBUG:', value)",
        "examples": ["Reproduce the smallest failing case", "Inspect types and values", "Check boundary conditions"],
        "misconceptions": ["Changing many things at once makes the cause harder to identify.", "A program that runs without syntax errors can still be logically wrong."],
        "debug": "Isolate the smallest failing step, inspect inputs and intermediate values, form a hypothesis, change one thing and retest.",
        "application": "When a sensor alert fires incorrectly, inspect raw readings, conversion logic, threshold comparison and final decision separately.",
    },
    "Problem Solving": {
        "meaning": "Problem solving means translating a real requirement into inputs, outputs, constraints, steps and a testable solution.",
        "why": "Strong problem solving prevents writing syntax before understanding what the program must actually do.",
        "syntax": "# 1. define inputs\n# 2. define output\n# 3. choose steps\n# 4. test edge cases",
        "examples": ["Break a billing problem into inputs, calculation and output", "Turn a monitoring requirement into checks and actions"],
        "misconceptions": ["The first solution is not automatically the best one.", "Correct syntax does not guarantee a correct algorithm."],
        "debug": "Compare the implementation against the original requirement and test normal, boundary and invalid cases.",
        "application": "For a student result system, define marks, validation rules, grade boundaries, output and edge cases before coding.",
    },
    "Application": {
        "meaning": "Application is the ability to transfer a concept from a familiar example to a new situation and justify the chosen approach.",
        "why": "Real learning is demonstrated when you can select and adapt a concept rather than only recall its definition.",
        "syntax": "# choose a concept based on the problem, then implement and test it",
        "examples": ["Use loops to process unknown-length input", "Use functions to separate reusable business logic"],
        "misconceptions": ["Memorizing one example does not prove transfer.", "A solution should be justified by requirements, not by habit."],
        "debug": "Explain why your chosen construct fits the problem, then test a changed input or constraint.",
        "application": "Combine variables, conditions, loops and functions to build a small practical program instead of solving isolated syntax exercises.",
    },
}

GENERIC_CONCEPTS = ["Core Concepts", "Terminology", "Components", "Process", "Examples", "Applications", "Advantages", "Limitations", "Problem Solving", "Debugging", "Advanced Application"]


def concepts_for(subject, topic):
    s = f"{subject} {topic}".lower()
    if "python" in s:
        return PYTHON_CONCEPTS.copy()
    if "iot" in s or "cloud" in s:
        return ["IoT Fundamentals", "Cloud Fundamentals", "Device Connectivity", "Data Collection", "Communication Protocols", "Cloud Storage", "Processing & Analytics", "Security", "Scalability", "Applications", "Problem Solving"]
    return GENERIC_CONCEPTS.copy()


def generic_detail(topic, concept):
    return {
        "meaning": f"{concept} is a key part of understanding {topic}. The tutor treats it as a concept to understand, apply and explain rather than something to memorize.",
        "why": f"Understanding {concept} helps you reason about {topic}, connect related ideas and choose an appropriate approach in unfamiliar problems.",
        "syntax": f"For {topic}, first identify the role of {concept}, then connect it to the problem's inputs, process and expected output.",
        "examples": [f"A simple {topic} example involving {concept}", f"A practical situation where {concept} changes the solution"],
        "misconceptions": [f"Knowing the definition of {concept} is not enough; you should also know when and why it is used.", f"Do not assume one example represents every case of {concept}."],
        "debug": f"When {concept} behaves unexpectedly, isolate the smallest failing case, inspect assumptions and compare the result with the requirement.",
        "application": f"Apply {concept} to a new {topic} scenario and explain why your chosen approach fits the requirements.",
    }


def detail(subject, topic, concept):
    if concept in PYTHON_DETAILS:
        return PYTHON_DETAILS[concept]
    return generic_detail(topic, concept)

# -----------------------------
# Agents
# -----------------------------

def assessment_agent(profile, mastery):
    concepts = concepts_for(profile["subject"], profile["topic"])
    gaps = []
    strengths = []
    for c in concepts:
        score = float(mastery.get(c, {}).get("mastery", 0))
        if score >= 75:
            strengths.append(c)
        elif score > 0:
            gaps.append(c)
        else:
            gaps.append(c)
    text = profile.get("knowledge", "").lower()
    if "not confident" in text or "struggle" in text or "weak" in text:
        confidence_note = "The learner reports difficulty applying knowledge independently; the tutor should use more guided examples and checks."
    elif profile.get("confidence") == "Low":
        confidence_note = "Confidence is low; the tutor should reduce cognitive load and build success through guided practice."
    else:
        confidence_note = "Confidence is sufficient for progressive practice, while mastery evidence will determine advancement."
    avg = sum(float(mastery.get(c, {}).get("mastery", 0)) for c in concepts) / len(concepts) if concepts else 0
    if avg == 0:
        readiness = 45
    else:
        readiness = round(avg)
    recommended = next((c for c in concepts if float(mastery.get(c, {}).get("mastery", 0)) < 60), concepts[0] if concepts else "Core Concepts")
    result = {
        "declared_level": profile["level"],
        "readiness": readiness,
        "strengths": strengths[:8] or ["Basic topic awareness"],
        "gaps": gaps[:10],
        "prerequisites": concepts[:3],
        "confidence_note": confidence_note,
        "recommended_start": recommended,
    }
    trace("Assessment Agent", "Learner diagnosis completed", result)
    return result


def learning_path_agent(profile, assessment, mastery):
    concepts = concepts_for(profile["subject"], profile["topic"])
    ordered = sorted(concepts, key=lambda c: float(mastery.get(c, {}).get("mastery", 0)))
    priority = ordered[:5]
    stages = [
        ("Diagnostic Foundation", "Verify prerequisites and identify exactly what is already mastered.", 10, "diagnostic"),
        ("Prerequisite Repair", "Teach only missing prerequisites required for the target topic.", 15, "remediation"),
        ("Deep Concept Teaching", f"Teach {profile['topic']} from intuition to formal structure, examples, edge cases and practical use.", 30, "teaching"),
        ("Worked Examples", "Study multiple examples and explain why each step is chosen.", 20, "application"),
        ("Guided Practice", "Solve progressively harder problems with hints and feedback.", 20, "practice"),
        ("Independent Application", "Transfer the concept to an unfamiliar scenario without step-by-step support.", 20, "application"),
        ("Adaptive 20-Question Quiz", "Measure recall, understanding, application, debugging and higher-order transfer.", 25, "assessment"),
        ("Error Analysis & Reteaching", "Map wrong answers to concepts and reteach the exact weakness with a new explanation and example.", 15, "adaptation"),
        ("Mastery Check", "Retest weak concepts and increase difficulty only when mastery is sustained.", 15, "mastery"),
    ]
    path = [{"step": i+1, "title": t, "description": d, "minutes": m, "stage": s} for i, (t,d,m,s) in enumerate(stages)]
    result = {"path": path, "priority_concepts": priority, "reason": "The order is driven by learner evidence and stored concept mastery rather than a fixed one-size-fits-all sequence."}
    trace("Learning Path Agent", "Personalized learning path generated", {"priority_concepts": priority, "steps": path})
    return result


def teaching_agent(profile, assessment, concept=None, depth=None):
    concept = concept or assessment["recommended_start"]
    depth = depth or profile.get("level", "Beginner")
    d = detail(profile["subject"], profile["topic"], concept)

    # The same concept is deliberately taught differently at each learner level.
    # This is deterministic so the lab works even without an LLM/API key.
    if depth == "Beginner":
        meaning = f"In simple terms: {d['meaning']}"
        why = f"Why you need it now: {d['why']}"
        examples = [f"Start with this basic example: {x}" for x in d["examples"][:3]]
        misconceptions = d["misconceptions"][:2]
        check = [
            f"Explain {concept} in your own simple words.",
            f"Give one basic example of {concept}.",
            f"Identify one common mistake with {concept}."
        ]
        transfer = f"Solve a small {profile['topic']} problem using {concept}. Explain each step before moving to the next one."
    elif depth == "Intermediate":
        meaning = f"Core idea: {d['meaning']}\n\nIntermediate perspective: connect this concept to program structure, reuse and practical problem solving rather than treating it as isolated syntax."
        why = f"Why it matters: {d['why']}\n\nFocus: choose the construct based on the requirement and explain the trade-off behind your choice."
        examples = [f"Practical example: {x}" for x in d["examples"]] + [f"Combine {concept} with another Python concept and explain the interaction."]
        misconceptions = d["misconceptions"] + [f"Do not choose {concept} only because it appeared in a previous example; justify it from the problem requirements."]
        check = [
            f"Explain when {concept} is preferable to an alternative approach.",
            f"Modify an example of {concept} for a changed requirement.",
            f"Identify an edge case and explain how you would test it."
        ]
        transfer = f"Take an unfamiliar {profile['topic']} requirement, select whether {concept} is appropriate, implement a solution and justify the design."
    else:
        meaning = f"Advanced view: {d['meaning']}\n\nEngineering perspective: reason about correctness, edge cases, maintainability and how this concept interacts with other constructs."
        why = f"Advanced use: {d['why']}\n\nEvaluate the implications of your choice under changed constraints, unusual inputs and larger problem size."
        examples = [f"Advanced scenario: {x}" for x in d["examples"]] + [f"Analyze an edge case involving {concept} and explain how the implementation should respond.", f"Refactor a solution using {concept} for clarity, correctness or reuse."]
        misconceptions = d["misconceptions"] + [f"A syntactically valid use of {concept} can still be a poor design choice when the constraints change."]
        check = [
            f"Analyze an edge case where a naive use of {concept} fails.",
            f"Compare two approaches involving {concept} and justify your choice.",
            f"Design a test that could expose a subtle bug involving {concept}."
        ]
        transfer = f"Solve a challenging {profile['topic']} problem with changed constraints. Use {concept}, justify the design, discuss edge cases and explain how you would test the result."

    lesson = {
        "concept": concept,
        "depth": depth,
        "objective": f"By the end of this {depth.lower()} lesson, you should be able to explain {concept}, apply it at the {depth.lower()} level, debug common mistakes and transfer it to an unfamiliar problem.",
        "what_it_means": meaning,
        "why_it_matters": why,
        "prerequisites": assessment["prerequisites"],
        "core_explanation": meaning,
        "syntax_or_structure": d["syntax"],
        "worked_examples": examples,
        "common_misconceptions": misconceptions,
        "debugging": d["debug"],
        "real_world_application": d["application"],
        "check_for_understanding": check,
        "transfer_challenge": transfer,
    }
    trace("Teaching Agent", "Level-adapted lesson generated", {"concept": concept, "depth": depth, "level": profile["level"], "sections": list(lesson.keys())})
    return lesson


def practice_agent(profile, concept, mastery):
    d = detail(profile["subject"], profile["topic"], concept)
    m = float(mastery.get(concept, {}).get("mastery", 0))
    questions = [
        {"level": "Guided", "prompt": f"In your own words, explain {concept} and identify the main purpose it serves in {profile['topic']}.", "hint": f"Start with the problem that {concept} helps solve. Think about the role described in the lesson."},
        {"level": "Guided", "prompt": f"Give a simple example of {concept} and explain each important step.", "hint": "Use a small example first. Name the input, operation and expected result."},
        {"level": "Independent", "prompt": f"Solve a new {profile['topic']} situation where {concept} is useful. Explain why you selected it.", "hint": "Identify the requirement before choosing the construct."},
        {"level": "Challenge", "prompt": f"A solution using {concept} works for a normal case but fails at an edge case. How would you debug and improve it?", "hint": d["debug"]},
    ]
    trace("Practice Agent", "Personalized guided-to-independent practice generated", {"concept": concept, "mastery": m, "count": len(questions)})
    return questions

# -----------------------------
# Quiz engine: always 20 questions
# -----------------------------

def python_quiz_bank():
    return [
        ("Variables", "What is the main purpose of a variable in Python?", ["Give a name to a value so it can be used and updated", "Install Python", "Stop the interpreter", "Delete all memory"], 0, "Easy", "Recall"),
        ("Data Types", "Which value is a Boolean?", ["True", "'True'", "10", "3.14"], 0, "Easy", "Recall"),
        ("Conditions", "Which construct is used to choose between alternative paths?", ["if/elif/else", "for only", "import only", "def only"], 0, "Easy", "Understanding"),
        ("Loops", "Which loop is commonly used to iterate through a list?", ["for", "if", "def", "return"], 0, "Easy", "Recall"),
        ("Functions", "What is the main purpose of a function?", ["Encapsulate reusable logic", "Always print output", "Create a database", "Stop a loop"], 0, "Easy", "Understanding"),
        ("Parameters", "In def add(a, b), what are a and b?", ["Parameters", "Modules", "Loops", "Exceptions"], 0, "Easy", "Recall"),
        ("Return Values", "What does return do inside a function?", ["Sends a value back to the caller and exits the function", "Prints the value only", "Repeats the function", "Imports a module"], 0, "Medium", "Understanding"),
        ("Scope", "A variable created inside a function is normally available where?", ["Inside that function's local scope", "Everywhere automatically", "Only in imported modules", "Only after the program ends"], 0, "Medium", "Understanding"),
        ("Debugging", "What is a good first debugging step when a calculation is wrong?", ["Reproduce the smallest failing case and inspect inputs/intermediate values", "Change every line", "Ignore the error", "Rewrite the whole program"], 0, "Medium", "Debugging"),
        ("Problem Solving", "What should you clarify before writing a solution?", ["Inputs, outputs, constraints and required behavior", "Only the final variable name", "Only the hardest case", "Only the syntax"], 0, "Medium", "Problem Solving"),
        ("Variables", "What is the difference between = and ==?", ["= assigns; == compares", "Both compare", "= compares; == assigns", "Neither is valid"], 0, "Medium", "Understanding"),
        ("Data Types", "What is the type of the value 10?", ["int", "str", "bool", "float"], 0, "Easy", "Recall"),
        ("Conditions", "If marks >= 40, what happens when marks is 40?", ["The condition is true", "The condition is false", "A loop starts", "The program must crash"], 0, "Medium", "Application"),
        ("Loops", "What is a major risk of a while loop?", ["The condition may never become false, causing an infinite loop", "It cannot use variables", "It always runs exactly once", "It cannot contain calculations"], 0, "Medium", "Debugging"),
        ("Functions", "Does defining a function execute its body immediately?", ["No; the function normally runs when it is called", "Yes, always", "Only if it has parameters", "Only if it returns a value"], 0, "Medium", "Understanding"),
        ("Parameters", "What is an argument?", ["A value supplied to a function call", "The function name", "The return keyword", "A loop condition"], 0, "Medium", "Recall"),
        ("Return Values", "What does a function return when it reaches the end without return?", ["None", "0", "False always", "The function name"], 0, "Hard", "Understanding"),
        ("Scope", "Which lookup order is commonly summarized by LEGB?", ["Local, Enclosing, Global, Built-in", "Loop, Example, Global, Boolean", "Local, External, General, Basic", "List, Expression, Group, Block"], 0, "Hard", "Recall"),
        ("Application", "You must process every item in an unknown-length list. Which approach fits best?", ["Iterate over the list with a loop", "Write one statement per item", "Use only an if statement", "Avoid repetition completely"], 0, "Hard", "Application"),
        ("Problem Solving", "Which approach best demonstrates transfer of learning?", ["Solve a new problem and justify why the chosen concepts fit", "Repeat a definition", "Copy one example exactly", "Memorize syntax only"], 0, "Hard", "Problem Solving"),
    ]


def generic_quiz(topic, concepts):
    q = []
    for i in range(20):
        c = concepts[i % len(concepts)]
        q.append((c, f"Which statement best demonstrates understanding of {c} in {topic}?",
                  [f"Explain its meaning, when it is used, and apply it to a new situation",
                   "Memorize the term without examples",
                   "Copy one fixed example",
                   "Skip related concepts"], 0,
                  "Easy" if i < 7 else "Medium" if i < 14 else "Hard",
                  "Understanding" if i % 3 else "Application"))
    return q


def generate_quiz(profile, mastery):
    raw = python_quiz_bank() if "python" in profile["subject"].lower() else generic_quiz(profile["topic"], concepts_for(profile["subject"], profile["topic"]))
    weak = sorted(concepts_for(profile["subject"], profile["topic"]), key=lambda c: float(mastery.get(c, {}).get("mastery", 0)))
    # Stable prioritization: weak concepts appear earlier, while all concepts remain covered.
    raw.sort(key=lambda item: (weak.index(item[0]) if item[0] in weak else 999, {"Easy":0,"Medium":1,"Hard":2}[item[4]]))
    questions = []
    for i, item in enumerate(raw[:20], 1):
        c, prompt, options, correct, difficulty, skill = item
        questions.append({"id": i, "concept": c, "question": prompt, "options": options, "correct": correct, "difficulty": difficulty, "skill": skill})
    trace("Quiz Agent", "Generated 20-question adaptive quiz", {"topic": profile["topic"], "weak_concepts_prioritized": weak[:5]})
    return questions


def evaluate_quiz(questions, answers, mastery):
    score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct"])
    concept_stats = {}
    errors = []
    for i, q in enumerate(questions):
        c = q["concept"]
        concept_stats.setdefault(c, {"correct":0, "total":0, "wrong_questions":[]})
        concept_stats[c]["total"] += 1
        if answers.get(i) == q["correct"]:
            concept_stats[c]["correct"] += 1
        else:
            concept_stats[c]["wrong_questions"].append(q["id"])
            errors.append({"question": q["id"], "concept": c, "selected": answers.get(i), "correct": q["correct"], "difficulty": q["difficulty"], "skill": q["skill"]})
    weak = []
    for c, s in concept_stats.items():
        pct = round(100 * s["correct"] / s["total"])
        old = float(mastery.get(c, {}).get("mastery", 0))
        # Quiz evidence is blended with prior evidence instead of erasing history.
        new = round(0.55 * old + 0.45 * pct)
        mastery[c] = {"mastery": new, "attempts": int(mastery.get(c, {}).get("attempts", 0)) + 1, "last_score": pct, "updated": datetime.now().isoformat(timespec="seconds")}
        if pct < 70:
            weak.append(c)
        s["percentage"] = pct
    percentage = round(100 * score / len(questions)) if questions else 0
    if percentage < 50:
        decision = "Remediation"
        adaptation = "Return to foundations, reteach weak concepts deeply, complete guided practice, then retest."
    elif percentage < 80 or weak:
        decision = "Targeted Practice"
        adaptation = "Practice the weak concepts with additional examples and application problems before advancing."
    else:
        decision = "Accelerate"
        adaptation = "Advance to more complex scenarios, edge cases and independent problem solving."
    result = {"score": score, "total": len(questions), "percentage": percentage, "decision": decision, "adaptation": adaptation, "concept_stats": concept_stats, "weak_concepts": weak, "errors": errors}
    trace("Evaluation & Feedback Agent", f"Quiz evaluated: {score}/{len(questions)} → {decision}", {"score":score,"total":len(questions),"decision":decision,"weak_concepts":weak})
    return result


def apply_adaptation(result, profile, mastery):
    concepts = concepts_for(profile["subject"], profile["topic"])
    if result["decision"] == "Remediation":
        focus = result["weak_concepts"] or concepts[:3]
        next_action = "Reteach the weakest concepts from first principles, then use guided practice and a fresh 20-question reassessment."
        stage = "Teaching / Remediation"
    elif result["decision"] == "Targeted Practice":
        focus = result["weak_concepts"] or concepts[:2]
        next_action = "Use targeted examples and practice on the identified weak concepts, then reassess transfer."
        stage = "Practice / Targeted Practice"
    else:
        # Once the current concepts are strong, move to the next concept in the
        # ordered curriculum rather than returning to an already-mastered concept.
        focus = [c for c in concepts if float(mastery.get(c, {}).get("mastery", 0)) < 85]
        if not focus:
            focus = concepts[-1:]
        next_action = "Advance to the next concept with more complex scenarios, edge cases and independent problem solving."
        stage = "Teaching / Acceleration"

    next_concept = focus[0] if focus else concepts[0]
    result2 = {
        "decision": result["decision"],
        "next_action": next_action,
        "focus_concepts": focus,
        "next_concept": next_concept,
        "next_stage": stage,
        "level": profile.get("level", "Beginner"),
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }
    trace("Adaptation Agent", "Next personalized plan selected", result2)
    return result2


# -----------------------------
# UI helpers
# -----------------------------

def render_nav():
    labels = ["🏠 Dashboard", "🧠 Assessment", "🗺️ Learning Path", "🧑‍🏫 Teaching", "💻 Practice", "📝 20-Question Quiz", "🎯 Evaluation & Feedback", "🔄 Adaptation", "💾 Learning History", "🔗 Agent Trace"]
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = labels[0]
    return st.radio("", labels, key="nav_page", horizontal=True, label_visibility="collapsed")


def load_state():
    if "trace" not in st.session_state:
        st.session_state.trace = []
    if "profile" not in st.session_state:
        st.session_state.profile = {"name":"Niyati", "subject":"Python Programming", "level":"Beginner", "goal":"Understand topics deeply, apply them to practical problems, and improve problem-solving.", "knowledge":"I know basic Python syntax, variables, data types, and conditional statements. I struggle with loops, functions, parameters, return values, and applying concepts to problem-solving.", "confidence":"Moderate", "topic":"Python Loops and Functions"}
    if "mastery" not in st.session_state:
        mem = load_memory(st.session_state.profile["name"], st.session_state.profile["subject"])
        st.session_state.mastery = mem["mastery"]
        st.session_state.history = mem["history"]
        if mem.get("profile"):
            st.session_state.profile.update(mem["profile"])
    for k, default in {
        "assessment": None, "path": None, "lesson": None, "practice": None,
        "quiz": None, "answers": {}, "evaluation": None, "adaptation": None,
        "quiz_submitted": False, "last_balloon_signature": None, "pending_page": None
    }.items():
        if k not in st.session_state:
            st.session_state[k] = default


def save_all():
    save_memory(st.session_state.profile, st.session_state.mastery, st.session_state.history)


def dashboard():
    p = st.session_state.profile
    concepts = concepts_for(p["subject"], p["topic"])
    vals = [float(st.session_state.mastery.get(c, {}).get("mastery", 0)) for c in concepts]
    overall = round(sum(vals)/len(vals)) if vals else 0
    attempts = sum(int(v.get("attempts",0)) for v in st.session_state.mastery.values())
    answered = sum(1 for h in st.session_state.history if h.get("type") == "quiz" for _ in h.get("answers", []))
    st.title("🎓 Personalized Adaptive Learning Tutor")
    st.caption("CE509 Agentic AI • Computer DLOC Lab-I • PS No. 4 • Assess → Teach Deeply → Practice → Quiz → Diagnose → Adapt → Remember → Continue")
    st.markdown("### Learner Dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Overall Mastery", f"{overall}%")
    b.metric("Concepts Tracked", len(st.session_state.mastery))
    c.metric("Quiz Attempts", attempts)
    d.metric("Questions Answered", answered)
    if st.session_state.adaptation:
        st.info(f"**Continue:** {st.session_state.adaptation['next_action']}")
    else:
        st.warning("No adaptive decision yet. Start with Assessment.")
    st.markdown("### How the tutor adapts")
    st.write("Assess → Diagnose → Personalize → Teach deeply → Practice → 20-question quiz → Evaluate → Reteach/Accelerate → Remember → Continue")
    st.markdown("### Current learner profile")
    st.json(p)


def sidebar_profile():
    with st.sidebar:
        st.header("👤 Learner Profile")
        name = st.text_input("Student Name", value=st.session_state.profile["name"])
        subject = st.selectbox("Subject", ["Python Programming", "Cloud Computing", "Agentic AI", "Cybersecurity", "IoT", "Data Science", "Other"], index=["Python Programming","Cloud Computing","Agentic AI","Cybersecurity","IoT","Data Science","Other"].index(st.session_state.profile["subject"]) if st.session_state.profile["subject"] in ["Python Programming","Cloud Computing","Agentic AI","Cybersecurity","IoT","Data Science","Other"] else 0)
        level = st.selectbox("Current Level", ["Beginner","Intermediate","Advanced"], index=["Beginner","Intermediate","Advanced"].index(st.session_state.profile["level"]))
        goal = st.text_area("Learning Goal", value=st.session_state.profile["goal"])
        knowledge = st.text_area("What do you already know / struggle with?", value=st.session_state.profile["knowledge"], height=120)
        confidence = st.selectbox("Confidence", ["Low","Moderate","High"], index=["Low","Moderate","High"].index(st.session_state.profile.get("confidence","Moderate")))
        topic = st.text_input("Topic to Learn", value=st.session_state.profile["topic"])
        if st.button("💾 Save Profile", use_container_width=True):
            old_profile = dict(st.session_state.profile)
            new_profile = {"name":name.strip() or "Learner", "subject":subject, "level":level, "goal":goal, "knowledge":knowledge, "confidence":confidence, "topic":topic.strip() or subject}
            level_changed = old_profile.get("level") != new_profile["level"]
            subject_or_topic_changed = (old_profile.get("subject") != new_profile["subject"] or old_profile.get("topic") != new_profile["topic"])
            st.session_state.profile.update(new_profile)
            mem = load_memory(st.session_state.profile["name"], st.session_state.profile["subject"])
            st.session_state.mastery = mem["mastery"]
            st.session_state.history = mem["history"]
            # A level/topic change must invalidate previously generated teaching content.
            if level_changed or subject_or_topic_changed:
                st.session_state.assessment = None
                st.session_state.path = None
                st.session_state.lesson = None
                st.session_state.practice = None
                st.session_state.quiz = None
                st.session_state.evaluation = None
                st.session_state.adaptation = None
            save_all()
            st.success("Profile saved. The tutor will regenerate content for the selected learner level.")

# -----------------------------
# Pages
# -----------------------------

def assessment_page():
    p = st.session_state.profile
    st.header("🧠 Assessment Agent — Deep Learner Diagnosis")
    st.write("The assessment uses your stated level, goal, confidence, current knowledge and stored concept mastery. It identifies strengths, gaps, prerequisites and the best starting point.")
    topic = st.text_input("Topic to learn", value=p["topic"], key="assessment_topic")
    if st.button("🚀 Run Personalized Assessment", type="primary"):
        p["topic"] = topic.strip() or p["topic"]
        st.session_state.assessment = assessment_agent(p, st.session_state.mastery)
        st.session_state.path = None
        st.session_state.lesson = None
        st.session_state.practice = None
        st.session_state.quiz = None
        st.session_state.evaluation = None
        st.session_state.adaptation = None
        save_all()
    if st.session_state.assessment:
        a = st.session_state.assessment
        x,y,z = st.columns(3)
        x.metric("Declared Level", a["declared_level"])
        y.metric("Readiness", f"{a['readiness']}%")
        z.metric("Recommended Start", a["recommended_start"])
        st.subheader("Strengths")
        st.success(" • ".join(a["strengths"]))
        st.subheader("Knowledge Gaps")
        for g in a["gaps"]: st.warning(g)
        st.subheader("Prerequisites")
        st.write(" • ".join(a["prerequisites"]))
        st.subheader("Potential Misconception / Risk")
        st.write(a["confidence_note"])
        st.subheader("Diagnostic Recommendation")
        st.info(f"Start with **{a['recommended_start']}**. Build the missing foundation, teach it deeply, practice it, then verify mastery with the adaptive 20-question quiz before progressing.")


def path_page():
    p = st.session_state.profile
    st.header("🗺️ Learning Path Agent — Personalized 9-Stage Path")
    if not st.session_state.assessment:
        st.warning("Run Assessment first.")
        return
    if st.button("🧭 Build / Rebuild Adaptive Path", type="primary"):
        st.session_state.path = learning_path_agent(p, st.session_state.assessment, st.session_state.mastery)
        save_all()
    if st.session_state.path:
        st.info(st.session_state.path["reason"])
        st.write("**Priority concepts:** " + " • ".join(st.session_state.path["priority_concepts"]))
        for s in st.session_state.path["path"]:
            with st.expander(f"Step {s['step']}: {s['title']}"):
                st.write(s["description"])
                st.caption(f"Estimated time: {s['minutes']} min • Stage: {s['stage']}")


def teaching_page():
    p = st.session_state.profile
    st.header("🧑‍🏫 Teaching Agent — Deep Learning Module")
    if not st.session_state.assessment:
        st.warning("Run Assessment first.")
        return
    concepts = concepts_for(p["subject"], p["topic"])

    # After adaptation, the next weak concept becomes the active teaching plan.
    adaptive_concept = None
    if st.session_state.adaptation:
        adaptive_concept = st.session_state.adaptation.get("next_concept")
    default = adaptive_concept or st.session_state.assessment["recommended_start"]
    if default not in concepts:
        default = concepts[0]
    concept = st.selectbox("What do you want the tutor to teach you next?", concepts, index=concepts.index(default))
    depth = p.get("level", "Beginner")
    st.info(f"**Current learner level:** {depth} • **Next concept:** {concept}")
    if st.session_state.adaptation:
        a = st.session_state.adaptation
        st.success(f"🎯 Adaptive next plan: **{a.get('next_concept', concept)}** • Stage: **{a.get('next_stage', 'Teaching')}** • Selected from stored mastery evidence.")

    # Automatically generate the lesson when this page is reached after adaptation.
    if st.session_state.adaptation and st.session_state.lesson is None:
        st.session_state.lesson = teaching_agent(p, st.session_state.assessment, concept, depth)
        save_all()
    elif st.button("📚 Teach Me Properly", type="primary"):
        st.session_state.lesson = teaching_agent(p, st.session_state.assessment, concept, depth)
        save_all()

    if st.session_state.lesson:
        l = st.session_state.lesson
        st.title(l["concept"])
        st.caption(f"Depth: {l.get('depth', depth)} • Adapted for: {depth}")
        sections = [
            ("1. Learning Objective", l["objective"]),
            ("2. What It Means", l["what_it_means"]),
            ("3. Why It Matters", l["why_it_matters"]),
            ("4. Prerequisites", "\n".join(f"• {x}" for x in l["prerequisites"])),
            ("5. Core Explanation", l["core_explanation"]),
            ("6. Syntax / Structure", f"```python\n{l['syntax_or_structure']}\n```"),
            ("7. Worked Examples", "\n".join(f"• {x}" for x in l["worked_examples"])),
            ("8. Common Misconceptions", "\n".join(f"• {x}" for x in l["common_misconceptions"])),
            ("9. Debugging Strategy", l["debugging"]),
            ("10. Real-World Application", l["real_world_application"]),
            ("11. Check Your Understanding", "\n".join(f"{i+1}. {x}" for i,x in enumerate(l["check_for_understanding"]))),
            ("12. Transfer Challenge", l["transfer_challenge"]),
        ]
        for title, body in sections:
            st.subheader(title)
            if body.startswith("```"):
                st.markdown(body)
            else:
                st.write(body)


def practice_page():
    p = st.session_state.profile
    st.header("💻 Practice Agent — Guided → Independent → Challenge")
    if not st.session_state.lesson:
        st.warning("Teach a concept first.")
        return
    concept = st.session_state.lesson["concept"]
    if st.button("🧩 Generate Practice Set", type="primary"):
        st.session_state.practice = practice_agent(p, concept, st.session_state.mastery)
    if st.session_state.practice:
        for i, q in enumerate(st.session_state.practice,1):
            st.subheader(f"{i}. {q['prompt']}")
            with st.expander("💡 Hint"): st.write(q["hint"])
            with st.expander("✅ Worked solution / reasoning"): st.write("First identify the requirement, then connect it to the concept. A strong answer should explain the choice, show the steps, and mention at least one edge case or debugging check.")


def quiz_page():
    p = st.session_state.profile
    st.header("📝 Quiz Agent — 20-Question Adaptive Assessment")
    if st.button("🎯 Generate 20-Question Adaptive Quiz", type="primary"):
        st.session_state.quiz = generate_quiz(p, st.session_state.mastery)
        st.session_state.answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.evaluation = None
    if not st.session_state.quiz:
        st.info("The quiz always contains exactly 20 questions and covers recall, understanding, application, debugging, problem solving and transfer. Weak concepts are prioritized using stored mastery.")
        return
    st.info("This quiz covers recall, understanding, application, debugging, problem solving and higher-order transfer. Weak concepts are prioritized from stored mastery.")
    for i,q in enumerate(st.session_state.quiz):
        st.markdown(f"### Q{i+1}. {q['question']}")
        st.caption(f"{q['concept']} • {q['difficulty']} • {q['skill']}")
        choice = st.radio("Answer", q["options"], index=None, key=f"quiz_{i}", label_visibility="visible")
        if choice is not None:
            st.session_state.answers[i] = q["options"].index(choice)
    if st.button("✅ Submit & Evaluate 20-Question Quiz", type="primary"):
        if len(st.session_state.answers) < 20:
            st.error(f"Please answer all 20 questions before submitting. {20-len(st.session_state.answers)} remain.")
        else:
            st.session_state.evaluation = evaluate_quiz(st.session_state.quiz, st.session_state.answers, st.session_state.mastery)
            st.session_state.quiz_submitted = True
            signature = json.dumps(st.session_state.answers, sort_keys=True)
            if st.session_state.last_balloon_signature != signature and st.session_state.evaluation["percentage"] >= 80:
                st.balloons()
                st.session_state.last_balloon_signature = signature
            st.session_state.history.append({"type":"quiz", "time":datetime.now().isoformat(timespec="seconds"), "topic":p["topic"], "score":st.session_state.evaluation["score"], "total":20, "answers":list(st.session_state.answers.values()), "decision":st.session_state.evaluation["decision"]})
            save_all()
            st.success("Quiz evaluated and learning evidence saved.")


def evaluation_page():
    st.header("🎯 Evaluation & Feedback Agent")
    e = st.session_state.evaluation
    if not e:
        st.warning("Complete and submit the 20-question quiz first.")
        return
    a,b,c = st.columns(3)
    a.metric("Score", f"{e['score']}/{e['total']}")
    b.metric("Percentage", f"{e['percentage']}%")
    c.metric("Decision", e["decision"])
    st.success(f"You scored **{e['score']}/{e['total']} ({e['percentage']}%)**. Concept-level evidence has been stored for the next learning decision.")
    st.subheader("Concept-Level Performance")
    for concept, s in e["concept_stats"].items():
        st.write(f"**{concept} — {s['percentage']}%**")
        st.progress(s["percentage"] / 100)
    st.subheader("Question-Wise Error Analysis")
    if not e["errors"]:
        st.success("No incorrect answers. The tutor can increase difficulty.")
    else:
        for err in e["errors"]:
            with st.expander(f"❌ Q{err['question']} — {err['concept']} — {err['difficulty']}"):
                st.write(f"Your selected option index: {err['selected']}")
                st.write(f"Correct option index: {err['correct']}")
                st.write(f"Skill: {err['skill']}")
                st.write("The tutor maps this error to the concept so the next teaching/practice step can target the weakness.")
    st.subheader("Adaptive Next Learning Steps")
    if e["decision"] == "Remediation":
        st.write("1. **Targeted reteaching** — reteach the weak concepts with simpler explanations and multiple worked examples.")
        st.write("2. **Guided practice** — complete problems with hints before attempting independent application.")
        st.write("3. **Reassessment** — take another 20-question assessment emphasizing the weak concepts.")
    elif e["decision"] == "Targeted Practice":
        st.write("1. **Targeted practice** — focus on the concepts below the mastery threshold.")
        st.write("2. **Application** — solve new scenarios with reduced scaffolding.")
        st.write("3. **Reassessment** — verify that the improvement transfers to new questions.")
    else:
        st.write("1. **Increase difficulty** — introduce edge cases and more complex scenarios.")
        st.write("2. **Independent application** — solve unfamiliar problems and justify the solution.")
        st.write("3. **Advance** — move to the next concept while retaining periodic mastery checks.")


def adaptation_page():
    st.header("🔄 Adaptation Agent — What Should Happen Next?")
    if not st.session_state.evaluation:
        st.warning("Complete a quiz evaluation first.")
        return
    e = st.session_state.evaluation
    st.write(f"**Decision:** {e['decision']}")
    st.info(e["adaptation"])
    if not st.session_state.adaptation:
        if st.button("🚀 Apply Adaptive Decision", type="primary"):
            st.session_state.adaptation = apply_adaptation(e, st.session_state.profile, st.session_state.mastery)
            save_all()
            # The tutor immediately routes the learner to the selected next plan.
            # Remediation/acceleration starts with teaching; targeted practice goes
            # directly to the Practice Agent.
            next_page = "💻 Practice" if st.session_state.adaptation.get("next_stage", "").startswith("Practice") else "🧑‍🏫 Teaching"
            st.session_state.pending_page = next_page
            st.rerun()
    else:
        a = st.session_state.adaptation
        st.success("Learning state updated. The next personalized plan has been selected.")
        st.subheader("Next Plan")
        st.write(f"**Concept:** {a.get('next_concept', 'Next concept')}")
        st.write(f"**Stage:** {a.get('next_stage', 'Next stage')}")
        st.write(f"**Learner level:** {a.get('level', st.session_state.profile.get('level', 'Beginner'))}")
        st.write(f"**Focus concepts:** {', '.join(a.get('focus_concepts', []))}")


def history_page():
    st.header("💾 Persistent Learning Memory")
    if not st.session_state.history:
        st.info("No learning history yet. Complete an assessment or quiz to create evidence.")
    for i,h in enumerate(reversed(st.session_state.history),1):
        with st.expander(f"{i}. {h.get('time','')} — {h.get('type','event').title()} — {h.get('topic','')}"):
            st.json(h)
    if st.button("⬇️ Export Learning State"):
        payload = {"profile":st.session_state.profile,"mastery":st.session_state.mastery,"history":st.session_state.history,"trace":st.session_state.trace}
        st.download_button("Download JSON", json.dumps(payload, indent=2), file_name="learning_state.json", mime="application/json")


def trace_page():
    st.header("🔗 Multi-Agent Communication & Decision Trace")
    if not st.session_state.trace:
        st.info("No agent events yet. Run the workflow to see communication between agents.")
        return
    for i,event in enumerate(reversed(st.session_state.trace),1):
        with st.expander(f"{i}. {event['agent']} — {event['time']}"):
            st.write(event["summary"])
            st.json(event["payload"])

# -----------------------------
# Optional LLM enhancement note
# -----------------------------

def llm_status():
    if os.getenv("OPENAI_API_KEY"):
        return "LLM enhancement available via OPENAI_API_KEY; deterministic tutor engine remains the fallback."
    return "Running in deterministic tutor mode. Add OPENAI_API_KEY for optional LLM-generated enrichment."

load_state()
sidebar_profile()
if st.session_state.get("pending_page"):
    st.session_state.nav_page = st.session_state.pending_page
    st.session_state.pending_page = None
page = render_nav()

if page == "🏠 Dashboard": dashboard()
elif page == "🧠 Assessment": assessment_page()
elif page == "🗺️ Learning Path": path_page()
elif page == "🧑‍🏫 Teaching": teaching_page()
elif page == "💻 Practice": practice_page()
elif page == "📝 20-Question Quiz": quiz_page()
elif page == "🎯 Evaluation & Feedback": evaluation_page()
elif page == "🔄 Adaptation": adaptation_page()
elif page == "💾 Learning History": history_page()
elif page == "🔗 Agent Trace": trace_page()

with st.sidebar:
    st.divider()
    st.caption(llm_status())
