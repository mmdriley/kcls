# Project: KCLS

## Purpose

See `README.md`.

## Development guidelines

### Planning
 - The agent is primarily working with the user on an _implementation plan_ ("the plan") in `PLAN.md`.
   - Note `PLAN.md` is `.gitignore`d.
   - If `PLAN.md` doesn't exist, nothing has been planned yet. Create it with sections: Overview; Done; In-progress; and TODO.
     - The "In Progress" section of the plan should to describe steps in implementation that are underway but where the agent is in dialogue with the user on implementation choices. It corresponds roughly to uncommitted changes. Don't continue "In Progress" without the user's assent.
   - **ALL** changes should be limited to `PLAN.md` until the user confirms they want to begin implementation on a specific part of the plan.
 - The user must review and commit all changes. The agent will stage them and ask the user for a review.

### General
 - Where possible, provide endpoints that can be tested locally and check if they are acceptable before deploying to cloud hosts.
 - Update documentation and comments if they are incorrect.

### Python
 - Ensure that Python source files:
   - are formatted with `ruff`
   - follow pep8 and the Google Python style guide
   - include type annotations, except where they can reasonably be inferred
     - cross-module interfaces should be fully annotated
 - Keep `Pipfile` and `requirements.txt` in sync. `requirements.txt` is used for containerization and should avoid strict patch version pinning to minimize noise.
 - Sort lists of dependencies.

### CSS
 - Avoid inline CSS styles. Punt CSS to standalone files in the `static/` directory.
