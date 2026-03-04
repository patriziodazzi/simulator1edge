# simulator1edge

Cloud/Edge simulator prototype.

## Status

This repository appears to be an older research/prototype codebase.
It can still be executed, but it had no packaging metadata and no dependency list,
which made it fail out-of-the-box.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python test/main.py
```

The demo script builds a multi-cloud continuum and runs a simple deployment simulation.

Note: the repository now includes lightweight local fallbacks for `simpy`, `networkx` and `matplotlib` APIs used by this prototype, so the demo can run even in offline/restricted environments.
