import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

GMAIL_USER = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
IMAP_URL = "imap.gmail.com"

def fetch_scholar_emails(limit=5, only_unread=True, query=None):
    """
    GmailからGoogle Scholarのアラートメールを取得する
    only_unread=True の場合は未読のみ取得し、取得後に既読にするかは制御可能
    query: IMAP検索クエリ (指定がなければデフォルトのScholar条件を使用)
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Error: GMAIL_ADDRESS or GMAIL_APP_PASSWORD is not set in .env")
        return []

    print(f"Connecting to Gmail as {GMAIL_USER}...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_URL)
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")

        # 検索条件の構築
        if query:
            search_criteria = query
        else:
            criteria = ['(FROM "scholaralerts-noreply@google.com")']
            if only_unread:
                criteria.append('(UNSEEN)')
            search_criteria = " ".join(criteria)
        
        print(f"Searching with criteria: {search_criteria}")
        
        status, messages = mail.search(None, search_criteria)
        
        if status != "OK":
            print("Search failed or no messages found.")
            return []

        email_ids = messages[0].split()
        
        if not email_ids:
            print("No matching emails found.")
            return []

        # 最新のものから取得
        latest_email_ids = email_ids[-limit:]
        
        fetched_emails = []

        print(f"Found {len(email_ids)} emails. Fetching last {len(latest_email_ids)}...")

        for e_id in reversed(latest_email_ids):
            # メール本体を取得
            # RFC822で取得すると自動で既読になる場合が多い（サーバー設定による）が
            # 基本は `body` を取ると既読になる。
            # 今回は処理したいので既読になってもOKかな？
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # emailモジュールでパース
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 件名の取得（デコード処理）
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    print(f"Fetched Email: {subject}")
                    fetched_emails.append(msg)
        
        return fetched_emails
        
    except Exception as e:
        print(f"Login or Fetch Error: {e}")
        return []
    finally:
        try:
            mail.logout()
        except:
            pass

if __name__ == "__main__":
    print("--- Gmail Connection Test ---")
    # テストとして「全てのメール」から最新3件を取得してみる
    emails = fetch_scholar_emails(limit=3, only_unread=False, query="ALL")
    
    if emails:
        print("Success! Connection established.")
    else:
        print("No emails found (Login might be successful but inbox is empty?)")
