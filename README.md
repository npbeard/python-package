# echochamber

`echochamber` is a Python package for transforming text through stylized digital personas and is designed to demonstrate a wide set of course concepts inside a small, testable library.

## Features

- Transform text through multiple persona voices: noir, sci-fi, and therapy
- Use the library from Python code or from a command-line script
- Apply recursive transformation layers
- Add optional timestamp formatting and regex-based "chaos"
- Stream output in chunks with a generator
- Read input from a file path or use the interactive CLI menu

## Installation

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ echochamber
```

For local development:

```bash
pip install -e .
pytest -q
```

## Quick Start

### Python API

```python
from echochamber import Persona, NoirVoice
from echochamber.utils import EngineConfig

persona = Persona(
    name="Spade",
    voice=NoirVoice(),
    config=EngineConfig(include_time=False, chaos=True),
)

result = persona.echo_once("The weather is rainy.", layers=2, intensity=2)
print(result["result"].transformed)
```

### CLI

Transform text directly:

```bash
echochamber "The weather is rainy." --voice noir --layers 2 --chaos --intensity 2
```

Read input from a file path:

```bash
echochamber --input-file sample.txt --voice scifi --time
```

Launch the simple interactive menu:

```bash
echochamber --interactive
```

## Project Structure

```text
python-package/
├── src/echochamber/
│   ├── __init__.py
│   ├── cli.py
│   ├── personas.py
│   ├── utils.py
│   └── voices.py
├── tests/
│   ├── test_cli.py
│   ├── test_persona.py
│   └── test_utils.py
├── scripts/
│   └── echochamber_cli.py
├── pyproject.toml
└── README.md
```

## Assignment Coverage

This package intentionally covers more than the required ten points from the assignment.

| Requirement | Where it appears |
| --- | --- |
| Classes | `Persona`, `Voice`, `NoirVoice`, `SciFiVoice`, `TherapyVoice`, `EngineConfig` |
| Instances | Creating `Persona(name="Spade", voice=NoirVoice())` |
| Class attributes | `Voice.registry_name`, `Persona.default_chunk_size` |
| Instance attributes | `Persona.name`, `voice`, `tags`, `config` |
| Mutable attributes | `Persona.tags` |
| Immutable attributes | `EngineConfig` is a frozen dataclass |
| Hashable objects | `EngineConfig` can be used as a dict key |
| Magic methods | `Persona.__call__`, `Persona.__repr__`, `Persona.__iter__` |
| Docstrings | Present in all main modules |
| Inheritance | `NoirVoice`, `SciFiVoice`, `TherapyVoice` inherit from `Voice` |
| Composition | `Persona` contains a `Voice` instance |
| `*args` | `Persona.add_tags(*tags)` |
| `**kwargs` | `Persona.echo_once(..., **kwargs)` |
| Default arguments | `layers=1`, `intensity=1`, `chunk_size=None` |
| Positional arguments | CLI `text` argument |
| Keyword arguments | `layers=2`, `intensity=2`, `config=...` |
| Decorators | `@timed` |
| Generators | `Persona.echo()` |
| Scripts | `scripts/echochamber_cli.py`, `[project.scripts]` in `pyproject.toml` |
| Paths | CLI `--input-file` uses `pathlib.Path` |
| Collections | Lists, dictionaries, and dataclasses across the package |
| Iterables | `Persona.__iter__` and generator output |
| Pass by reference vs copy | Utility copy helpers and tests |
| Deep copy vs shallow copy | `deep_copy()` and `shallow_copy()` |
| Menus | Interactive CLI mode with `--interactive` |
| Datetime | `now_string()` |
| String format time | `strftime` in `now_string()` |
| Regular expressions | `apply_chaos()` |
| `argparse` | CLI parser in `src/echochamber/cli.py` |
| `.env` | CLI reads defaults from environment variables via `python-dotenv` |
| `README.md` | This file |
| `pyproject.toml` | Package metadata and build config |
| Object scope | Module constants and local variables in helpers like `now_string()` and the CLI |
| For loops | Tag insertion, chunk generation, regex vowel replacement |
| While loops | Interactive CLI menu |
| Recursion | `recursive_layers()` |

## Testing

The repository includes `pytest` tests, which is not mandatory in the assignment but should help the project score better.

Run the suite with:

```bash
pytest -q
```

The tests currently cover:

- persona behavior and validation
- CLI helper behavior
- regex, recursion, datetime formatting, and copy utilities

## Environment Variables

Optional defaults can be configured with a local `.env` file:

```env
ECHOCHAMBER_DEFAULT_VOICE=noir
ECHOCHAMBER_DEFAULT_LAYERS=1
```

## Group Information

- Group: Group 8
- Members: Bobby Pakenham, Nicolas Beard Naranjo, Yi Long, Sofia Mollon, Bushra Yousuf
- Repository: https://github.com/npbeard/python-package
- TestPyPI: https://test.pypi.org/project/echochamber
