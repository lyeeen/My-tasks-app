from parse_mail import process_scholar_mail_file, extract_papers_from_message
from gmail_client import fetch_scholar_emails

if __name__ == "__main__":
    print("--- Scholar Alert Automation ---")
    
    # モード切り替え（デバッグ用）
    USE_LOCAL_FILE = False
    
    # デバッグ用：既読メールも含めて取得するか？
    # Trueにすると過去のメール（最大limit件）も再取得してテストできる
    DEBUG_FETCH_READ_EMAILS = False
    
    if USE_LOCAL_FILE:
        target_file = "scholar_alert.eml"
        process_scholar_mail_file(target_file)
    else:
        # Gmailから取得 (最新5件)
        # デバッグモードなら既読も許可(only_unread=False)、通常は未読のみ(True)
        fetch_unread_only = not DEBUG_FETCH_READ_EMAILS
        
        print(f"Fetching emails... (Unread Only: {fetch_unread_only})")
        emails = fetch_scholar_emails(limit=5, only_unread=fetch_unread_only)
        
        if not emails:
            print("No emails to process.")
        else:
            print(f"Processing {len(emails)} emails...")
            for i, msg in enumerate(emails):
                print(f"\n--- Processing Email {i+1}/{len(emails)} ---")
                extract_papers_from_message(msg)
    
    print("\nDone!")
