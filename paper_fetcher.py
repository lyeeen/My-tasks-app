import requests
from bs4 import BeautifulSoup
import re

def fetch_arxiv_abstract(url):
    """
    ArXiv / bioRxiv からAbstractを取得する
    """
    try:
        # PDFリンクならAbstractページに変換
        if "/pdf/" in url:
            url = url.replace("/pdf/", "/abs/")
            if url.endswith(".pdf"):
                url = url[:-4]
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # ArXivの構造
            abs_quote = soup.find("blockquote", class_="abstract")
            if abs_quote:
                full_abstract = abs_quote.get_text().replace("Abstract:", "").strip()
                print(f"Fetched (arXiv): {full_abstract[:30]}...")
                return full_abstract
            
            # bioRxivなどのメタタグ
            meta_desc = soup.find("meta", attrs={"name": "DC.Description"})
            if meta_desc:
                print(f"Fetched (Meta): {meta_desc['content'][:30]}...")
                return meta_desc['content']
                
        print(f"Failed to fetch arXiv: {res.status_code}")
        return None
        
    except Exception as e:
        print(f"ArXiv fetch error: {e}")
        return None

def get_paper_abstract(url):
    """
    URLに応じて適切な取得関数を呼び出す
    """
    if not url:
        return None

    if "arxiv.org" in url or "biorxiv.org" in url:
        return fetch_arxiv_abstract(url)
    
    # 他のサイトは未対応なのでNoneを返す
    return None
