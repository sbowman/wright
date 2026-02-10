# Wright Build Tool

This is a simple tool used to build applications in our monorepo.

## Usage

| If you want to...      | 	Run this command         |
|------------------------|---------------------------|
| Test changes instantly | 	uv pip install -e .      |
| Install it permanently | 	uv tool install .        | 
| Remove it later        | 	uv tool uninstall wright |
| Update it              | 	uv tool upgrade wright   |

## Running Wright (dev mode)

1. Create a virual environment
2. Install into environment
3. Change to your project and run with a BUILD.py

```
uv venv
uv pip install -e .
source .venv/bin/activate
```

You can then run `wright` in your project with a BUILD.py.