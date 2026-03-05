# 🌌 echochamber (Group 8)

> "The Digital Mirror: A Narrative Sentiment & Chaos Engine."

echochamber is a Python library developed by Group 8 for the Python for Data Analysis II project. It deconstructs user input and reconstructs it through the lens of distinct digital personas using Object-Oriented Programming (OOP) and functional paradigms.

---

## 📦 Installation

Install directly from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ echochamber-group8
```

---

## 🚀 Quick Start

```python
from echochamber import Persona, NoirVoice

# 1. Initialize a persona using Composition
detective = Persona(name="Spade", voice=NoirVoice())

# 2. Generate a stylized response using a Generator
for chunk in detective.echo("The weather is quite rainy today."):
    print(chunk, end="")
```

---

## 🛠️ Technical Requirements Covered

This library implements 15+ of the required technical points:

| Category | Implemented Features |
|---|---|
| OOP | Classes, Instances, Inheritance, Composition, Magic Methods |
| Attributes | Class attributes, Instance attributes, Mutable vs Immutable |
| Logic | Generators, Regular Expressions, Recursion |
| Functions | `*args`, `**kwargs`, Default arguments, Decorators |
| Data/Time | Datetime, string format time, Collections |
| Packaging | `README.md`, `pyproject.toml`, `.env`, `argparse` |

---

## 📂 Repository Structure

```
.
├── pyproject.toml          # Build system and dependency management
├── README.md               # Project documentation
├── .env.example            # Environment variable configuration
├── src/
│   └── echochamber/
│       ├── __init__.py     # Public API exports
│       ├── personas.py     # Persona and EchoResult classes
│       ├── voices.py       # Voice base class and subclasses
│       ├── utils.py        # Utilities, decorators, helpers
│       └── cli.py          # argparse CLI entry point
├── scripts/
│   └── echochamber_cli.py  # CLI runner script
└── tests/
    ├── test_persona.py     # Persona tests
    └── test_utils.py       # Utility tests
```

---

## 👥 Group 8 Members

- Bobby Pakenham
- Nico Beard Naranjo
- Sofia Mollon
- Yi Long
- Bushra Yousuf

**Submission Date:** 16 March 2026
