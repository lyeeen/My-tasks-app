import email
from email.header import decode_header
from email import policy
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from notion_client import add_paper_to_notion
from paper_fetcher import get_paper_abstract

# ...
# nlp関連やrequests, reなどは不要になったので削除してOK

def extract_papers_from_message(msg):
    # ... (Subject抽出やHTML取得部分はそのまま)
    # ... (BeautifulSoupパースもそのまま)
    
            # ... (タイトル、URL、著者、メール内Abstract抽出までそのまま)
            
            print(f"Title: {title}")
            print(f"URL: {real_url}")
            
            final_abstract = abstract_from_mail

            # --- Refactored Block Start ---
            # 外部サイトからAbstractを取得
            fetched_abstract = get_paper_abstract(real_url)
            if fetched_abstract:
                final_abstract = fetched_abstract
            else:
                print("Using abstract from email (or none).")
            # --- Refactored Block End ---

            # 日本語翻訳
            # ... (翻訳ロジックはそのままだけど、対象ドメイン判定はpaper_fetcherに任せてもいいが一旦そのまま)

# ... imports ...
import email
from email import policy
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from newspaper import Article, Config
import nltk
import requests
from notion_client import add_paper_to_notion

# nlp()を使うために必要なデータをダウンロード（初回のみでOKだけど念のため）
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

def extract_papers_from_message(msg):
    """
    email.message.Message オブジェクトから論文を抽出してNotionに追加する
    """
    # SubjectからTopicを抽出
    subject = msg.get("Subject", "")
    topic = "Unknown"
    
    if subject:
        # デコード処理
        decoded_list = decode_header(subject)
        topic_parts = []
        for content, encoding in decoded_list:
             if isinstance(content, bytes):
                 topic_parts.append(content.decode(encoding or "utf-8"))
             else:
                 topic_parts.append(content)
        full_subject = "".join(topic_parts)
        
        # " - new results" を削除してトピック名にする
        topic = full_subject.replace(" - new results", "").strip()
        print(f"Topic: {topic}")

    # メール本文（HTML部分）を取り出す
    html_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    html_content = payload.decode(errors="ignore")
                break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            html_content = payload.decode(errors="ignore")

    if not html_content:
        print("No HTML content found in email.")
        return

    # BeautifulSoupでパース
    soup = BeautifulSoup(html_content, "html.parser")

    # 構造を確認するためにタイトルっぽいところ(h3など)を抽出
    print("--- Start Extraction ---")
    papers_found = 0
    
    for h3 in soup.find_all("h3"):
        title_link = h3.find("a")
        if title_link:
            papers_found += 1
            title = title_link.get_text().strip()
            raw_url = title_link['href']
            
            # Google ScholarのリダイレクトURLから本来のURLを抽出
            parsed = urlparse(raw_url)
            qs = parse_qs(parsed.query)
            
            real_url = qs['url'][0] if 'url' in qs else raw_url
            
            # 著者情報の抽出
            author_div = h3.find_next_sibling("div", style=lambda s: s and "color:#006621" in s)
            authors = author_div.get_text(strip=True) if author_div else "No Authors"

            # Abstractの抽出
            abstract_div = h3.find_next_sibling("div", class_="gse_alrt_sni")
            abstract_from_mail = abstract_div.get_text(strip=True) if abstract_div else "No Abstract"

            print(f"Title: {title}")
            print(f"URL: {real_url}")
            
            final_abstract = abstract_from_mail

            # 外部サイトからAbstractを取得
            fetched_abstract = get_paper_abstract(real_url)
            if fetched_abstract:
                final_abstract = fetched_abstract
                print(f"Using fetched abstract: {final_abstract[:50]}...")
            else:
                 print("Using abstract from email (or none).")

            # 日本語翻訳
            abstract_jp = ""
            
            # Abstractがあれば（Web由来でもメール由来でも）翻訳を実行する
            if final_abstract and final_abstract != "No Abstract":
                try:
                    # deep_translatorを使って翻訳
                    translator = GoogleTranslator(source='auto', target='ja')
                    # 長すぎると翻訳エラーになりやすいので4500文字で制限しておく
                    translated = translator.translate(final_abstract[:4500]) 
                    if translated:
                        abstract_jp = translated
                        print(f"Translated Abstract (JP): {abstract_jp[:30]}...")
                except Exception as e:
                    print(f"Translation failed: {e}")

            # Notionに追加
            print("Adding to Notion...")
            add_paper_to_notion(title, real_url, authors, final_abstract, abstract_jp, topic)
            print("-" * 20)
            
    if papers_found == 0:
        print("No papers found in this email.")

def process_scholar_mail_file(file_path):
    """
    (互換性用) ファイルパスから読み込んで処理する
    """
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        extract_papers_from_message(msg)
    except FileNotFoundError:
        print(f"Error: File not found ({file_path})")
