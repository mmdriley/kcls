# Project: KCLS

## Purpose

See `README.md`.

## Development guidelines

### Planning
  - The agent is primarily working with the user on an _implementation plan_ ("the plan") in `PLAN.md`.
  - If `PLAN.md` does not exist, stop and ask the user to create it. **Note**: `PLAN.md` is not, and should not be, checked into `git`.
  - **ALL** changes should be limited to `PLAN.md` until the user confirms they want to begin implementation on a specific part of the plan.
  - The user must review and commit all changes. The agent will stage them and ask the user for a review.

### General
  - Where possible, provide endpoints that can be tested locally and check if they are acceptable before deploying to cloud hosts.
  - Update documentation and comments if they are incorrect.
  - Avoid mixing whitespace changes and semantic changes in the same diff.

### Python
  - Ensure that Python source files:
    - are formatted with `ruff format`
    - are linted via `pipenv run ruff check --fix`
    - typecheck with `pipenv run ty check`
    - follow pep8 and the Google Python style guide
    - include type annotations, except where they can reasonably be inferred
      - cross-module interfaces should be fully annotated
  - Keep `Pipfile` updated.
  - Sort lists of dependencies.

### CSS
  - Avoid inline CSS styles. Punt CSS to standalone files in the `static/` directory.
  - Even though it may be more verbose, prefer adding semantic class names rather than using `nth-child` with a constant.
