<div align="center">

# 🧩 Bing Puzzle Solver

**Automated 8-puzzle solver with A\* algorithm and PyAutoGUI click automation**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
&nbsp;
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-FF6B35?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
&nbsp;
[![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-Automation-4f46e5?style=for-the-badge)](https://pyautogui.readthedocs.io)
&nbsp;
[![Algorithm](https://img.shields.io/badge/A*-Search-3ddc84?style=for-the-badge)](https://en.wikipedia.org/wiki/A*_search_algorithm)

<br/>

> _"Let the algorithm do the clicking."_

</div>

---

## ✨ About

**Bing Puzzle Solver** is a desktop application that automatically solves the **8-puzzle (3×3 sliding puzzle)** and clicks the tiles on screen for you. It uses the **A\* search algorithm** with Manhattan Distance heuristic to find the optimal solution, then executes it via **PyAutoGUI** — either blazing fast or with human-like behavior.

> Made by **Stephan** — PyAutoGUI Edition

---

## 🌟 Features

- 🔍 **A\* Solver** — Finds the shortest solution using Manhattan Distance heuristic
- 🖱️ **Auto-click** — Moves & clicks tiles on screen automatically via PyAutoGUI
- 📍 **Smart coordinate capture** — Hover mouse to puzzle corners, no clicking needed
- ✅ **Solvability check** — Validates puzzle state before running (inversion parity)
- 📋 **Live log panel** — Real-time step-by-step execution feedback
- 🎨 **Modern dark UI** — Clean dark-themed interface built with Tkinter

---

## 🛠️ Tech Stack

| Technology                   | Description                                        |
| ---------------------------- | -------------------------------------------------- |
| 🐍 **Python 3.8+**           | Core language                                      |
| 🖼️ **Tkinter**               | GUI framework for the desktop interface            |
| 🖱️ **PyAutoGUI**             | Mouse movement & click automation                  |
| ⭐ **A\* Search**            | Optimal pathfinding algorithm for puzzle solving   |
| 📐 **Manhattan Distance**    | Heuristic function for A\* cost estimation         |
| 🧵 **Threading**             | Non-blocking solver execution in background thread |

---

## ⚡ Execution Modes

| Mode | Description |
|------|-------------|
| ⚡ **God Mode** | Fast clicks with minimal jitter — solves in seconds |
| 🧑 **Human Mode** | Simulates natural behavior: slow mouse, random pauses, hesitation |

---

## 🚀 Getting Started

Want to run this project locally? Follow these steps:

### Prerequisites

- [Python](https://python.org) v3.8 or higher
- [pip](https://pip.pypa.io/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/129msp/bing_puzzle_solver

# 2. Navigate to the project folder
cd bing_puzzle_solver

# 3. Install dependencies
pip install pyautogui
```

> **Linux users** may also need:
> ```bash
> sudo apt install python3-tk python3-xlib
> ```

### Run

```bash
python bing_puzzle_solver.py
```

---

## 🖥️ How to Use

**Step 1 — Enter puzzle state**
Read tiles from **top-left → bottom-right** and fill in the 9 input boxes. Use `0` for the empty tile.

```
5 | 2 | 3
---------
8 | 1 | 6      →   input: 5 2 3 8 1 6 4 7 0
---------
4 | 7 | _
```

**Step 2 — Capture puzzle coordinates**
Click **Capture Top-Left**, hover over the top-left corner of the puzzle on screen *(don't click — just hover)*, and wait 3 seconds. Repeat for the bottom-right corner.

**Step 3 — Choose execution mode**
Select **God Mode** for speed or **Human Mode** for natural-looking behavior.

**Step 4 — Solve!**
Click **Solve Puzzle** and watch the tiles get clicked automatically. Monitor progress in the live log panel.

---

## 📁 Project Structure

```
bing-puzzle-solver/
├── bing_puzzle_solver.py   # All-in-one: solver logic + GUI
└── README.md
```

---

## ⚠️ Important Notes

- **Emergency stop**: Move mouse to the **top-left corner of your screen** to abort execution instantly (`pyautogui.FAILSAFE = True`)
- Make sure the puzzle window is **visible and not minimized** while the solver runs
- **Human Mode is intentionally slow** — that's the point 😄

---

## 📬 Contact

Have a question or want to collaborate? Feel free to reach out!

[![GitHub](https://img.shields.io/badge/GitHub-129msp-181717?style=flat-square&logo=github)](https://github.com/129msp)

---

<div align="center">

Made with ❤️ by **Stephan**

⭐ If you find this useful, consider giving it a star!

</div>
