# TypeScript Flask URLs

This project aims to automatically generate TypeScript types and client-side request helpers directly from a Flask application. IT is heavily inspired by [JS Flask URLs](https://github.com/indico/js-flask-urls).

By inspecting Flask routes and their Python type annotations, it produces strongly typed TypeScript definitions and functions that can call those endpoints with correct argument and return types. The project is currently incomplete, but the core idea and basic functionality are already in place.

The main goal is to reduce duplication and type mismatches between backend and frontend codebases by treating the Flask app as the single source of truth for API structure and typing.

## Intended and Existing Features

Some features are already implemented, others are planned.

- [x] Parse Flask routes and URL rules  
- [x] Parse route argument types from annotations  
- [x] Parse return types from annotated view functions  
- [x] Generate TypeScript type definitions  
- [x] Generate TypeScript request/helper functions for endpoints  
- [x] CLI integration with Flask via a custom command  
- [x] Handling of Flask converters (custom and built-in)  
- [ ] Support for multiple HTTP methods (GET, POST, PUT, DELETE, etc.)  
- [ ] Support for JSON request bodies with typed parameters  
- [ ] Support for `typing.Annotated` to:
    - [ ] Ignore specific routes  
    - [ ] Customize generation behavior (naming, visibility, etc.)  
- [ ] Improved error reporting for unsupported or ambiguous annotations  
- [ ] Optional generation modes (types only, requests only)  
- [ ] Configuration file support  
- [ ] Handle recursive types (such as `type RecursiveType = tuple[int, RecursiveType]`)
- [x] Support returning with `jsonify(...)`
- [x] Support extensions via translators

## Installation

The project is not yet published on PyPI. Installation is currently done directly from source, preferably using `uv`.

Clone the repository and install dependencies:

```bash
git clone https://github.com/ArmindoFlores/ts-flask-urls
cd ts-flask-urls
uv sync --dev
uv pip install -e .
```

## Running Tests

Tests can be run using pytest:

```bash
pytest
```

## Usage

The tool is exposed as a Flask CLI command. At the moment, usage is manual.

Inside your Flask application environment, run:

```bash
flask ts-flask-urls map-urls
```

This command will:

- Load the Flask app
- Inspect the URL map and registered view functions
- Generate the corresponding TypeScript files (types and request helpers)

Output paths and structure are currently minimally configurable and may change as the project evolves.

## High-Level Overview

The tool operates as follows:

1. Flask application discovery

    The Flask CLI command loads the application context and accesses the Flask `url_map`.

2. Route inspection

    Each route rule is inspected to extract:
    - URL patterns
    - Path parameters and their Flask converters

3. Type extraction

    Python type annotations on view functions are analyzed to infer the argument types (path parameters) and the return type of each endpoint.

4. TypeScript generation

    The collected metadata is transformed into:
    - TypeScript type declarations
    - Typed request functions that build URLs and handle responses
