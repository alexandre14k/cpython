# myFRpy — Test AppImage Pre-Release

This is an early **test release** of the myFRpy interpreter, a language runtime derived from the CPython 3.12 codebase.
The goal of this pre-release is to provide a portable, self‑contained AppImage for experimentation and validation.

## Overview

myFRpy is a standalone interpreter with its own identity and runtime behavior.
This AppImage allows testing without installing anything system‑wide.

This build includes:

- The myFRpy interpreter
- Standard library (compatible with CPython 3.12)
- Updated README
- The myFRpy license
- Original upstream license text (as required)

This build does **not** include:

- pip
- venv
- ensurepip
- packaging tools
- system‑level integration

These components are intentionally disabled or incomplete in this test version.

## Status

- Interpreter runs normally
- AppImage launches correctly
- Core standard library modules load
- Embedded Tkinter can be used for UI design
- Some test suite failures remain (operator, pprint, set, statistics, etc.)
- Compatibility layer is still under development
- Packaging ecosystem is not yet supported
- Complementary keywords (spaces forbidden inside keywords) :
  - if    |  si
  - elif  |  autrement
  - else  |  sinon
  - for   |  pour
  - while |  tantque

## Usage

Make the AppImage executable:

```bash
chmod +x myFRpy3.12-x86_64.AppImage
```

Run the interpreter:
```bash
./myFRpy3.12-x86_64.AppImage
```

Run with the `test.py` script (reguires os with GUI):
```bash
./myFRpy3.12-x86_64.AppImage test.py
```
or from inside the interpreter
```bash
./myFRpy3.12-x86_64.AppImage
myFRpy 3.12.3 (heads/main-dirty:581db9e, May 30 2026, 13:36:16) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exec(open("test.py").read())
```

## Notes

This pre-release is intended only for testing and feedback.
Do not use in production environments.
Internal compatibility identifiers may exist for technical reasons, but the interpreter’s public identity is myFRpy.

## Licensing
This pre-release includes:

- The original upstream license text
- The new myFRpy license
- These **release notes**
- Attribution as required
- All licensing requirements have been preserved

Feedback

This is an early experimental build.
Feedback, bug reports, and suggestions are welcome as myFRpy evolves.