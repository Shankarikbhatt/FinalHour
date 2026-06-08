# ⏰ FinalHour

> *A smart last-minute study planner for the night before your exam.*

Built entirely from scratch in Python — no AI assistance, no templates, no shortcuts.

**[Jump to Run Instructions](#-How-to-run)**

---

## What it does

FinalHour takes your situation at midnight and builds a personalised, hour-by-hour study schedule around it. No generic advice. No guesswork. Just a clean plan you can actually follow.

You tell it:
- Which units and parts are still pending
- Whether you're pulling an all nighter, waking up early, or splitting your sleep
- Your current prep level

It gives you:
- A smart timetable with study slots, breaks, nap time and revision
- Part-based time allocation — Part B gets 60 mins because it deserves it
- Dynamic nap duration based on how heavy your workload is
- A beautiful dark-themed HTML page that auto-opens in your browser

---

## Features

- Smart schedule generation across 3 sleep modes — All Nighter, Early Wake, Sleep Split
- Interactive HTML output with progress tracking and mark-as-done
- Cyan-to-purple progress bar that fills as you complete topics
- Completion timestamps for each topic
- VITALS panel — your plan stats always visible on screen
- Dark / Light theme toggle
- Print-ready layout with floating action buttons
- Combo-specific headers and motivational lines for every scenario (9 unique combinations)
- Packaged as a standalone `.exe` — no Python installation needed

---

## How to run


Download the night scheduler.exe file from this repository.

Double-click the .exe file to launch the planner interface.

Fill in your sleep plan and topics to generate your interactive schedule instantly.

## Sleep Modes

| Mode | How it works |
|---|---|
| All Nighter | Studies from now until 2:30AM, 90-min power nap, revision until 6AM |
| Early Wake | Sleeps now, wakes at your chosen time, studies until 6AM |
| Sleep Split | Studies until 2AM, sleeps 2-5AM, revision 5-6AM |

---

## Study Time by Part

| Part | Time Allocated |
|---|---|
| Part A | 30 minutes |
| Part B | 60 minutes |
| Part C | 35 minutes |

---

## Built with

- Python 3
- HTML + CSS + JavaScript (output page)
- No external AI tools — every line written and debugged manually

---

## About

Built during my first year engineering holidays as a real solution to a problem every student faces the night before an exam. Deployed as a standalone executable so anyone can use it without any technical setup.

*First year CS student — Easwari Engineering College, Chennai*
