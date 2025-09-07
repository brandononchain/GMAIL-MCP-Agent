#!/usr/bin/env python3
# (same as before, trimmed header for brevity)
import argparse, base64, csv, mimetypes, os, sys, time, pathlib
from datetime import datetime
from email.message import EmailMessage
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from jinja2 import Template, StrictUndefined

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_service(credentials_path: str = "credentials.json", token_path: str = "token.json"):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise SystemExit(f"Missing {credentials_path}. Create OAuth client (Desktop) in Google Cloud Console and place it here.")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def load_template(template_string: str | None, template_file: str | None):
    if template_string and template_file:
        raise SystemExit("Provide either --body or --body_file, not both.")
    if template_file:
        with open(template_file, "r", encoding="utf-8") as f:
            return Template(f.read(), undefined=StrictUndefined)
    elif template_string:
        return Template(template_string, undefined=StrictUndefined)
    else:
        return None

def split_list(val: str | None) -> List[str]:
    if not val:
        return []
    parts = [p.strip() for p in val.replace(";", ",").split(",")]
    return [p for p in parts if p]

def build_message(sender: str, to: str, subject: str, body: str, cc: str | None = None, bcc: str | None = None, attachments: List[str] | None = None, from_name: str | None = None) -> EmailMessage:
    msg = EmailMessage()
    msg["To"] = to
    if cc: msg["Cc"] = cc
    if bcc: msg["Bcc"] = bcc
    msg["From"] = f"{from_name} <{sender}>" if from_name else sender
    msg["Subject"] = subject
    msg.set_content(body)
    for path in attachments or []:
        if not os.path.exists(path):
            print(f"WARNING: attachment not found: {path}", file=sys.stderr); continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None: ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as fp: data = fp.read()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))
    return msg

def send_message(service, user_id: str, msg: EmailMessage) -> str:
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    res = service.users().messages().send(userId=user_id, body={"raw": encoded}).execute()
    return res.get("id", "")

def main():
    ap = argparse.ArgumentParser(description="Send Gmail messages from a CSV with templating and rate limiting.")
    ap.add_argument("csv_path", nargs="?", default=os.getenv("CSV_FILE", "contacts.csv"))
    ap.add_argument("--from_email", default=os.getenv("FROM_EMAIL"))
    ap.add_argument("--from_name", default=os.getenv("FROM_NAME"))
    ap.add_argument("--subject", default=os.getenv("DEFAULT_SUBJECT"))
    ap.add_argument("--subject_file", default=None)
    ap.add_argument("--body", default=None)
    ap.add_argument("--body_file", default=os.getenv("DEFAULT_BODY_FILE"))
    ap.add_argument("--per_minute", type=int, default=int(os.getenv("PER_MINUTE", "12")))
    ap.add_argument("--resume", action="store_true", default=os.getenv("RESUME", "false").lower() == "true")
    ap.add_argument("--log", default=os.getenv("LOG_FILE", "send_log.csv"))
    ap.add_argument("--credentials", default=os.getenv("CREDENTIALS_FILE", "credentials.json"))
    ap.add_argument("--token", default=os.getenv("TOKEN_FILE", "token.json"))
    args = ap.parse_args()

    subject_tmpl = load_template(args.subject, args.subject_file)
    body_tmpl = load_template(args.body, args.body_file)

    sent_set = set()
    if args.resume and os.path.exists(args.log):
        try:
            import pandas as pd
            df = pd.read_csv(args.log)
            sent_set = set(df.loc[df["status"]=="sent","to"].astype(str).str.lower())
        except Exception:
            with open(args.log, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("status")=="sent":
                        sent_set.add(str(row.get("to","")).lower())

    service = get_service(args.credentials, args.token)
    sender_email = args.from_email or service.users().getProfile(userId="me").execute()["emailAddress"]

    log_exists = os.path.exists(args.log)
    log_f = open(args.log, "a", newline="", encoding="utf-8")
    logger = csv.DictWriter(log_f, fieldnames=["ts","to","subject","message_id","status","error"])
    if not log_exists: logger.writeheader()

    delay = 60.0 / max(1, args.per_minute); last_sent = 0.0; sent_count = 0

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "to" not in (reader.fieldnames or []):
            raise SystemExit(f"CSV must include 'to' column. Found: {reader.fieldnames}")
        for row in reader:
            to = (row.get("to","") or "").strip()
            if not to: continue
            if args.resume and to.lower() in sent_set: continue

            ctx = {k:(v or "") for k,v in row.items()}
            subject = subject_tmpl.render(**ctx) if subject_tmpl else (row.get("subject","") or "").strip()
            body = body_tmpl.render(**ctx) if body_tmpl else (row.get("body","") or "").strip()
            if not subject or not body:
                print(f"Skipping {to}: missing subject/body", file=sys.stderr); continue

            cc = row.get("cc",""); bcc = row.get("bcc",""); atts = split_list(row.get("attachments",""))
            msg = build_message(sender_email, to, subject, body, cc=cc, bcc=bcc, attachments=atts, from_name=args.from_name)

            wait = delay - (time.time() - last_sent)
            if wait > 0: time.sleep(wait)
            try:
                mid = send_message(service, "me", msg)
                logger.writerow({"ts": datetime.utcnow().isoformat(), "to": to, "subject": subject, "message_id": mid, "status":"sent", "error": ""}); log_f.flush(); sent_count += 1
            except Exception as e:
                logger.writerow({"ts": datetime.utcnow().isoformat(), "to": to, "subject": subject, "message_id": "", "status":"error", "error": str(e)}); log_f.flush()
            last_sent = time.time()

    print(f"Done. Sent attempts: {sent_count}. Log: {args.log}")
    log_f.close()

if __name__ == "__main__":
    main()
