from parse_mail import process_scholar_mail_file, extract_papers_from_message
from gmail_client import fetch_scholar_emails

if __name__ == "__main__":
    print("--- Scholar Alert Automation ---")
    
    # モード切り替え（デバッグ用）
    USE_LOCAL_FILE = False
    
    if USE_LOCAL_FILE:
        target_file = "scholar_alert.eml"
        process_scholar_mail_file(target_file)
    else:
        # Gmailから取得 (最新5件)
        emails = fetch_scholar_emails(limit=5, only_unread=False)
        
        if not emails:
            print("No emails to process.")
        else:
            print(f"Processing {len(emails)} emails...")
            for i, msg in enumerate(emails):
                print(f"\n--- Processing Email {i+1}/{len(emails)} ---")
                extract_papers_from_message(msg)
    
    print("\nDone!")
