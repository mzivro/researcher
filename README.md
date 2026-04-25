# AI Researcher

An end-to-end **LLM-powered research assistant** that plans, executes, and summarizes complex tasks using a multi-stage agent pipeline.

This project demonstrates how to build a modular AI system that:

1. Generates a structured research plan
2. Executes each step using tools and reasoning
3. Produces a clean, structured summary (PDF + Markdown)

---

## Features

* **Automated Planning**

  * Converts a task into a structured, step-by-step plan
* **Tool-Augmented Execution**

  * Uses search, Wikipedia, arXiv, and math tools
* **Step-by-Step Reasoning (ReAct Agent)**

  * Each step is executed independently with context
* **Summarization Pipeline**

  * Outputs GitHub-Flavored Markdown
  * Converts results to PDF
* **Interactive UI**

  * Built with Streamlit
  * Editable plans before execution
* **Logging System**

  * Optional debug logging to file

---

## Architecture Overview

```
User Task
   |
   ▼
Planner (LLM)
   │
   ▼
Plan (steps[])
   │
   ▼
Executor (ReAct Agent + Tools)
   │
   ▼
Plan with Results
   │
   ▼
Summarizer (LLM)
   │
   ▼
Markdown + PDF reports
```

### Components

| Component    | Responsibility                                      |
| ------------ | --------------------------------------------------- |
| `Planner`    | Generates structured plans using LLM                |
| `Executor`   | Executes each step with tools (search, arXiv, etc.) |
| `Summarizer` | Produces final Markdown + PDF                       |
| `Researcher` | Orchestrates UI and workflow                        |
| `Logger`     | Optional debug logging                              |
| `Settings`   | Environment configuration                           |

---

## Tech Stack

* **Python**
* **LangChain**
* **OpenAI API**
* **Streamlit**
* **Pydantic**
* **pypandoc (PDF generation)**

---

## Installation

```bash
git clone https://github.com/mzivro/researcher.git
cd researcher

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in root folder:

```
OPENAI_API_KEY=your_api_key

OPENAI_PLANNER_MODEL=gpt-4.1-mini
OPENAI_EXECUTOR_MODEL=gpt-4.1-mini
OPENAI_SUMMARIZER_MODEL=gpt-4.1-mini
```

Possibly you can set up models temperatures in `.env`:

```
OPENAI_PLANNER_TEMPERATURE=0.2
OPENAI_EXECUTOR_TEMPERATURE=0.8
OPENAI_SUMMARIZER_TEMPERATURE=0.2
```

---

## Usage

```bash
streamlit run src/app.py
```

### Workflow

1. Enter a task
2. Click generate
3. Optionally edit steps
4. Execute the plan
5. Get a summarized PDF report

You can also write your own plan steps without generating them.

---

## Example Use Cases

* Literature research
* Technical topic exploration
* Competitive analysis
* Learning complex subjects step-by-step

---

## Limitations

* No evaluation of answer correctness
* No retry/failure recovery mechanism
* Heavy reliance on external APIs
* Limited control over hallucinations
* Execution depth constrained (max iterations)

---

## Planned Future Improvements

* Scoring/self-reflection system
* Better hallucinations control
* Better logging system (like logging tokens etc.)

---

## License

MIT License. Feel free to use, modify, and build upon this project.
