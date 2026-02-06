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

            # Webから記事詳細を取得 (arXivなど)
            # ... (ここから下のロジックは前のままだけど、インデントに注意)
            if "arxiv.org" in real_url or "biorxiv.org" in real_url:
                if "/pdf/" in real_url:
                    real_url = real_url.replace("/pdf/", "/abs/")
                    if real_url.endswith(".pdf"):
                         real_url = real_url[:-4]
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    res = requests.get(real_url, headers=headers)
                    if res.status_code == 200:
                        paper_soup = BeautifulSoup(res.text, "html.parser")
                        abs_quote = paper_soup.find("blockquote", class_="abstract")
                        if abs_quote:
                            full_abstract = abs_quote.get_text().replace("Abstract:", "").strip()
                            print(f"Fetched Full Abstract (arXiv): {full_abstract[:50]}...")
                            final_abstract = full_abstract
                        else:
                            meta_desc = paper_soup.find("meta", attrs={"name": "DC.Description"})
                            if meta_desc:
                                 final_abstract = meta_desc['content']
                    else:
                        print(f"Failed to fetch: Status {res.status_code}")
                except Exception as e:
                    print(f"ArXiv fetch error: {e}")
            else:
                print("Skipping non-arXiv URL.")

            # Notionに追加
            print("Adding to Notion...")
            add_paper_to_notion(title, real_url, authors, final_abstract)
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
