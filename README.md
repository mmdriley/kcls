# King County Library System Client

A web application to aggregate and monitor checked-out library books for multiple family accounts from the King County Library System (KCLS).

> [!NOTE]
> This repository was mostly authored by `gemini-cli`.

## Features
-   **Multi-Account**: View books from multiple library cards in one place.
-   **Due Date Grouping**: Books are grouped by due date for easy planning.
-   **Due Soon Alerts**: Dates within the next 7 days are highlighted.
-   **Secure-ish**: Access is protected by a high-entropy URL token (Capability URL).

## Local Development

### Prerequisites
-   Python 3.9+
-   `pipenv`

### Setup

1.  **Install dependencies**:
    ```bash
    pipenv install
    ```

2.  **Set Environment Variables**:
    You need to provide credentials. You can set these in your shell or a `.env` file (gitignored).

    **For a single account:**
    ```bash
    export KCLS_USERNAME="your_username"
    export KCLS_PASSWORD="your_password"
    export KCLS_DISPLAY_NAME="My Books" # Optional
    ```

    **For multiple accounts (JSON string):**
    ```bash
    export KCLS_CREDS='[{"username": "user1", "password": "pw1", "display_name": "Mom"}, {"username": "user2", "password": "pw2", "display_name": "Kid"}]'
    ```

    **App Token (Security):**
    ```bash
    export APP_TOKEN="my-secret-token" # Required
    ```

### Running the App

**Development Mode (Auto-reload):**
```bash
pipenv run python main.py
```

**Production Mode (Gunicorn - Test before deploy):**
```bash
pipenv run gunicorn --bind 0.0.0.0:8080 main:app
```

Then visit: `http://localhost:8080/view/<APP_TOKEN>` (e.g., `http://localhost:8080/view/local-dev-token`)

## Deployment

This application is deployed to **Google Cloud Functions (2nd Gen)** via GitHub Actions.

### Architecture
-   **Platform**: Google Cloud Functions (Python 3.12, HTTP Trigger).
-   **CI/CD**: GitHub Actions workflow (`.github/workflows/deploy.yml`) handles deployment on push to `main`.
-   **Authentication**: Uses Workload Identity Federation (no long-lived service account keys).
-   **Secrets**: Application secrets (`KCLS_CREDS`, `APP_TOKEN`) are loaded securely from a private Google Cloud Storage bucket at runtime.

### Triggering a Deploy
Simply push changes to the `main` branch. The GitHub Action will:
1.  Authenticate with Google Cloud.
2.  Deploy the code as a Cloud Function (Gen 2).
3.  The service URL remains stable (unless deleted/recreated).

## Legacy CLI
The original CLI script is still available:
```bash
pipenv run python3 checkedout.py
```

## References
- https://web.archive.org/web/20120531214002/http://developer.bibliocommons.com/docs
