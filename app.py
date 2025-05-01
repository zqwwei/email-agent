from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import pickle
import os
from dotenv import load_dotenv
import email_helper
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime

# Load environment variables from .env file if present
load_dotenv()

app = Flask(__name__)

def load_summaries():
    summaries = []
    try:
        with open('summaries.json', 'r') as f:
            for line in f:
                summaries.append(json.loads(line))
    except FileNotFoundError:
        pass
    return summaries

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', 
                                                           ['https://www.googleapis.com/auth/gmail.modify'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_last_updated_time():
    try:
        # Get the modification time of summaries.json
        timestamp = os.path.getmtime('summaries.json')
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (FileNotFoundError, OSError):
        return "Never"

@app.route('/')
def index():
    category_filter = request.args.get('category')
    summaries = load_summaries()
    
    if category_filter:
        summaries = [s for s in summaries if s['category'].lower() == category_filter.lower()]
    
    # Split emails by importance while preserving original order
    important_list = [s for s in summaries if s['importance'].lower() == 'important']
    not_important_list = [s for s in summaries if s['importance'].lower() != 'important']
    
    last_updated = get_last_updated_time()
    
    return render_template('index.html', 
                          important_list=important_list, 
                          not_important_list=not_important_list,
                          last_updated=last_updated)

@app.route('/revert', methods=['POST'])
def revert():
    message_id = request.form.get('message_id')
    if message_id:
        # Re-authorize and mark as unread
        service = get_gmail_service()
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': ['UNREAD']}
        ).execute()
    return redirect('/')

@app.route('/refresh')
def refresh():
    email_helper.fetch_and_process_emails()
    return redirect(url_for('index'))

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    try:
        email_helper.fetch_and_process_emails()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
