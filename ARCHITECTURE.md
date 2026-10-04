# Architecture — Personalized Adaptive Learning Tutor

```text
                         ┌─────────────────────────┐
                         │     Learner Profile     │
                         │ level • goal • topic    │
                         │ knowledge • confidence  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Assessment Agent     │
                         │ diagnose strengths/gaps │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Mastery Model      │
                         │ concept-level memory    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Learning Path Agent   │
                         │ adaptive 9-stage path   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Teaching Agent     │
                         │ deep, structured lesson │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Practice Agent     │
                         │ guided → independent    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Quiz Agent — 20 Qs      │
                         │ adaptive + concept tags │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Evaluation & Feedback   │
                         │ score + error analysis  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Adaptation Agent     │
                         │ remediate/practice/     │
                         │ accelerate              │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Persistent Learning     │
                         │ Memory (SQLite)         │
                         └────────────┬────────────┘
                                      │
                                      └────► Continue Learning
```

## Agent responsibilities

| Agent | Responsibility | Main evidence |
|---|---|---|
| Assessment | Diagnose learner state | strengths, gaps, prerequisites, readiness |
| Learning Path | Select an adaptive sequence | priority concepts + 9 stages |
| Teaching | Teach deeply | structured lesson + examples + debugging |
| Practice | Build skill through scaffolding | guided/independent/challenge tasks |
| Quiz | Measure learning | exactly 20 tagged questions |
| Evaluation | Interpret performance | score + concept metrics + errors |
| Adaptation | Decide what happens next | remediation / targeted practice / acceleration |
| Memory | Preserve continuity | SQLite mastery + history |
| Trace | Make agent communication visible | timestamped events + payloads |
