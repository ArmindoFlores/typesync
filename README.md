# Typesync

This project aims to automatically generate TypeScript types and client-side request helpers directly from a Flask application. It is heavily inspired by [JS Flask URLs](https://github.com/indico/js-flask-urls).

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
- [x] Vite support
- [x] Handling of Flask converters (custom and built-in)
- [x] Support for multiple HTTP methods (GET, POST, PUT, DELETE, etc.)
- [x] Support for JSON request bodies with typed parameters
    - [ ] Support validators such as pydantic
- [ ] Support for `typing.Annotated` to:
    - [ ] Ignore specific routes
    - [ ] Customize generation behavior (naming, visibility, etc.)
- [ ] Improved error reporting for unsupported or ambiguous annotations
- [ ] Optional generation modes (types only, requests only)
- [ ] Configuration file support
- [x] Support custom formatting for generated code
- [x] Handle recursive types (such as `type RecursiveType = tuple[int, RecursiveType]`)*
- [x] Support returning with `jsonify(...)`
- [x] Support extensions via translators

\* Not all cases are supported.


## Installation

You can install typesync using `pip install typesync`. Alternatively, you can do it directly from source, preferably using `uv`, by cloning the repository and installing dependencies:

```bash
git clone https://github.com/ArmindoFlores/typesync
cd typesync
uv sync --dev
uv pip install -e .
```

## Usage
### TypeScript generation
The tool is exposed as a Flask CLI command. Inside your Flask application environment, run:

```bash
flask typesync generate OUT_DIR
```

This command will load the Flask app, inspect the URL map and registered view functions, and generate the corresponding TypeScript files (types and request helpers), placing them inside `OUT_DIR`. The names of the generated files, types, and functions can be customized using command line options. For more information about these options, use `flask typesync generate --help`.

### Using the generated code
The main output of typesync is a `makeAPI()` function that is used to instantiate an object containing a function per HTTP method per endpoint. An example on how to use this function is provided in [example/frontend/src/api.ts](example/frontend/src/api.ts).

### Rollup Plugin
Typesync has a rollup plugin that can be used to integrate with Rollup/Vite projects. Additional documentation is provided in [rollup-plugin-typesync/README.md](rollup-plugin-typesync/README.md).


## Inference

Typesync is capable of some basic type inference. This can be helpful when trying to incrementally adopt this package in an existing codebase, or for unconventional Flask setups. This functionality is optional, and needs to be enabled using the `--inference` flag. Additionally, the inference module may need to use `eval()` for evaluating some types; this is disabled by default, but can be enabled using `--inference-can-eval`.


## Running Tests

Tests can be run using pytest:

```bash
pytest
```
