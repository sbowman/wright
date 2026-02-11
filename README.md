# Wright Build Tool

This is a simple tool used to build applications in our monorepo.  It's really 
two things:  a library of functions that wrap shell commands that can be 
executed to build, test, run, and deploy applications, and a binary that helps 
facilitate these processes.

## Installing

## BUILD.py

## The `wright` Tool

## Using the `wright` Packages

## Developing the `wright` Functionality

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