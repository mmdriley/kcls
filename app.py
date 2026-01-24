"""
Generic Web Application

Routes:
    /view/<token>: The dashboard. <token> must match APP_TOKEN.
    /:             Returns 404 "Nothing here"


Environment Variables:
    APP_TOKEN:      Secret token required in the URL to access the dashboard.
    KCLS_CREDS:     JSON string containing a list of account credentials.
                    Example: '[{"username": "u1", "password": "p1", "display_name": "Name"}]'
    KCLS_USERNAME:  (Fallback) Single account username if KCLS_CREDS is not set.
    KCLS_PASSWORD:  (Fallback) Single account password if KCLS_CREDS is not set.
"""

import os
import json
from flask import Flask, render_template, abort
from datetime import date, timedelta
import apiclient

app = Flask(__name__)

# Configuration
if 'APP_TOKEN' not in os.environ:
    raise RuntimeError('APP_TOKEN environment variable is required.')
APP_TOKEN = os.environ['APP_TOKEN']


def get_creds():
    if 'KCLS_CREDS' in os.environ:
        return json.loads(os.environ['KCLS_CREDS'])
    # Fallback for local testing if KCLS_CREDS isn't set but individual env vars are
    if 'KCLS_USERNAME' in os.environ and 'KCLS_PASSWORD' in os.environ:
        return [
            {
                'username': os.environ['KCLS_USERNAME'],
                'password': os.environ['KCLS_PASSWORD'],
                'display_name': os.environ.get('KCLS_DISPLAY_NAME', 'My Account'),
            }
        ]
    return []


@app.route('/view/<token>')
def view_checked_out(token):
    if token.lower() != APP_TOKEN.lower():
        abort(403)

    creds = get_creds()
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
