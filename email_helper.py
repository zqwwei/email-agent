# email_helper.py

import os
import base64
from openai import OpenAI
from email import message_from_bytes
from email.header import decode_header
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import pickle
import json

# 🚀 正式版，DEBUG关掉
DEBUG = False

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Gmail API Scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def decode_mime_words(s):
    if not s:
        return ""
    parts = decode_header(s)
    return ''.join([
        part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
        for part, charset in parts
    ])

def extract_text_from_html(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator='\n')
    except Exception:
        return "[HTML 解析失败]"

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_recent_emails(service, max_results=10):
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX', 'UNREAD'],  # ✅ 正式拉取未读邮件
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_msg = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        email_msg = message_from_bytes(raw_msg)
        subject = decode_mime_words(email_msg.get('Subject', '(No Subject)'))
        from_email = email_msg.get('From', '(No Sender)')
        body = ''
        if email_msg.is_multipart():
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    continue
                payload = part.get_payload(decode=True)
                if content_type == "text/plain" and payload:
                    body = payload.decode(errors='ignore')
                    break
                elif content_type == "text/html" and not body and payload:
                    body = extract_text_from_html(payload.decode(errors='ignore'))
        else:
            payload = email_msg.get_payload(decode=True)
            if email_msg.get_content_type() == "text/plain":
                body = payload.decode(errors='ignore')
            elif email_msg.get_content_type() == "text/html":
                body = extract_text_from_html(payload.decode(errors='ignore'))

        emails.append({'id': msg['id'], 'subject': subject, 'from': from_email, 'body': body})
    return emails

def summarize_email(email):
    prompt = f"""
You are an intelligent email assistant. Please help process the following email.

Tasks:
1. Determine importance ("Important" or "Not Important").
2. Categorize into one of: ["Job", "Event", "Newsletter", "System", "Social", "Other"].
3. Summarize in 1-2 concise sentences.

Format your output strictly like this:
Importance: <Important or Not Important>
Category: <one of Job/Event/Newsletter/System/Social/Other>
Summary: <your summary here>

---
From: {email['from']}
Subject: {email['subject']}
Body:
{email['body'][:2000]}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def parse_summary_response(response_text):
    lines = response_text.strip().splitlines()
    importance = lines[0].split(":", 1)[1].strip()
    category = lines[1].split(":", 1)[1].strip()
    summary = lines[2].split(":", 1)[1].strip()
    return importance, category, summary

def save_summary(email, importance, category, summary_text):
    record = {
        "id": email['id'],
        "from": email['from'],
        "subject": email['subject'],
        "importance": importance,
        "category": category,
        "summary": summary_text
    }
    with open('summaries.json', 'a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def mark_email_as_read(service, message_id):
    if DEBUG:
        print(f"[DEBUG] Would mark email {message_id} as read.")
    else:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

def main():
    fetch_and_process_emails()

def fetch_and_process_emails():
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()
    print("✅ Current authorized account:", profile['emailAddress'])

    emails = get_recent_emails(service, max_results=10)
    for i, email in enumerate(emails):
        print(f"\n📩 Email {i+1}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        response_text = summarize_email(email)
        print(f"🤖 GPT Response:\n{response_text}")

        importance, category, summary_text = parse_summary_response(response_text)
        
        # Save all emails regardless of importance
        save_summary(email, importance, category, summary_text)
        
        # Mark non-important emails as read
        if importance.lower() != "important":
            mark_email_as_read(service, email['id'])

if __name__ == '__main__':
    main()