"""
Generic Web Application

Routes:
    /view/<token>: The dashboard. <token> must match APP_TOKEN.
    /:             Returns 404 "Nothing here"


Environment Variables:
    KCLS_SECRETS_BUCKET: Optional. Name of GCS bucket containing .env file.
    APP_TOKEN:      Secret token required in the URL to access the dashboard.
    KCLS_CREDS:     JSON string containing a list of account credentials.
                    Example: '[{"username": "u1", "password": "p1", "display_name": "Name"}]'
    KCLS_USERNAME:  (Fallback) Single account username if KCLS_CREDS is not set.
    KCLS_PASSWORD:  (Fallback) Single account password if KCLS_CREDS is not set.
"""

import os
import json
import io
from flask import Flask, render_template, abort
from datetime import date, timedelta
import apiclient
from dotenv import load_dotenv, dotenv_values
from google.cloud import storage

load_dotenv()

app = Flask(__name__)


def get_config():
    """
    Retrieves configuration from GCS if KCLS_SECRETS_BUCKET is set,
    otherwise falls back to os.environ.
    """
    bucket_name = os.environ.get('KCLS_SECRETS_BUCKET')
    config = {}

    if bucket_name:
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob('.env')
            content = blob.download_as_text()
            config = dotenv_values(stream=io.StringIO(content))
        except Exception as e:
            print(f"Error loading secrets from GCS: {e}")
            # Fallback or re-raise? For now, we might want to fall back to env
            # or return empty config which will fail validations below.
            pass
    
    # Merge with os.environ, preferring GCS config if present (or vice-versa?)
    # Usually GCS secrets > local env.
    # But we need to handle cases where keys are missing in GCS.
    
    # Let's treat 'config' as the primary source if bucket is set.
    # If not set, use os.environ.
    
    final_config = os.environ.copy()
    if config:
        final_config.update(config)
        
    return final_config


def get_creds(config):
    if 'KCLS_CREDS' in config:
        return json.loads(config['KCLS_CREDS'])
    # Fallback for local testing if KCLS_CREDS isn't set but individual env vars are
    if 'KCLS_USERNAME' in config and 'KCLS_PASSWORD' in config:
        return [
            {
                'username': config['KCLS_USERNAME'],
                'password': config['KCLS_PASSWORD'],
                'display_name': config.get('KCLS_DISPLAY_NAME', 'My Account'),
            }
        ]
    return []


@app.route('/view/<token>')
def view_checked_out(token):
    config = get_config()
    app_token = config.get('APP_TOKEN')
    
    if not app_token:
        # Configuration error
        return "Server misconfigured: APP_TOKEN missing", 500

    if token.lower() != app_token.lower():
        abort(403)

    creds = get_creds(config)
    all_data = []
    today = date.today()
    soon_threshold = today + timedelta(days=7)

    for cred in creds:
        try:
            client = apiclient.KCLSClient(cred['username'], cred['password'])
            items = client.get_checked_out_items()

            # Group by due date
            items.sort(key=lambda x: x.due_date)
            grouped_books = []
            if items:
                current_date = items[0].due_date
                current_group = []
                for item in items:
                    if item.due_date != current_date:
                        grouped_books.append(
                            {
                                'date': current_date,
                                'books': current_group,
                                'is_due_soon': current_date <= soon_threshold,
                            }
                        )
                        current_date = item.due_date
                        current_group = []
                    current_group.append(item)
                grouped_books.append(
                    {
                        'date': current_date,
                        'books': current_group,
                        'is_due_soon': current_date <= soon_threshold,
                    }
                )

            all_data.append(
                {
                    'display_name': cred.get('display_name', cred['username']),
                    'grouped_books': grouped_books,
                    'error': None,
                }
            )
        except Exception as e:
            all_data.append(
                {
                    'display_name': cred.get('display_name', cred['username']),
                    'grouped_books': [],
                    'error': str(e),
                }
            )

    return render_template('index.html', accounts=all_data)


@app.route('/')
def index():
    return 'Nothing here', 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
