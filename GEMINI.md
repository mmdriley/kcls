# Project: KCLS

## Purpose

See `README.md`.

## Development guidelines
 - Ensure that Python source files:
   - are formatted with `ruff`
   - follow pep8 and the Google Python style guide
   - include type annotations, except where they can reasonably be inferred
     - cross-module interfaces should be fully annotated
 - Avoid inline CSS styles. Punt CSS to standalone files in the `static/` directory.
 - Keep `Pipfile` and `requirements.txt` in sync. `requirements.txt` is used for containerization and should avoid strict patch version pinning to minimize noise.
 - Lists of dependencies must be kept in alphabetical order.
 - Where possible, provide endpoints that can be tested locally and check if they are acceptable before deploying to cloud hosts.
 - Update documentation and comments if they are incorrect.
