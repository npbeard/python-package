# 🌌 echochamber (Group 8)
"The Digital Mirror: A Narrative Sentiment & Chaos Engine."echochamber is a specialized Python library developed by Group 8 for the Python for Data Analysis II project. It deconstructs user input and reconstructs it through the lens of distinct digital personas using advanced Object-Oriented Programming (OOP) and functional paradigms.🚀
# Installation
Install the library directly from TestPyPi:
pip install --index-url https://test.pypi.org/simple/ echochamber-group8

# 🛠️ Technical Requirements Covered
This library implements 15+ of the required technical points:
Category,Implemented Feature
OOP,"Classes, Instances, Inheritance, Composition, Magic Methods"
Attributes,"Class attributes, Instance attributes, Mutable vs Immutable"
Logic,"Generators, Regular Expressions, Recursion"
Functions,"*args, **kwargs, Default arguments, Decorators"
Data/Time,"Datetime, string format time, Collections"
Packaging,"Readme.md, pyproject.toml, .env, argparse"

# 1. Initialize a persona using Composition
detective = Persona(name="Spade", voice=NoirVoice())

# 2. Generate a stylized response using a Generator
for chunk in detective.echo("The weather is quite rainy today."):
    print(chunk, end="")

# 📂 Repository Structure
src/echochamber/: Core library logic.

tests/: Unit testing suite using pytest (Extra points!).

scripts/: CLI entry points using argparse.

pyproject.toml: Build system and dependency management.

.env: Environment variable configuration.

# 👥 Group 8 Members
[Member 1 Name][Member 2 Name][Member 3 Name][Member 4 Name]
Submission Date: 16 March 2026