import os
import requests
import json
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def add_paper_to_notion(title, url, authors, abstract):
    """
    論文情報をNotionデータベースに追加する関数
    """
    if not NOTION_API_KEY:
        print("Error: NOTION_API_KEY is not set.")
        return
    if not NOTION_DATABASE_ID:
        print("Error: NOTION_DATABASE_ID is not set.")
        return

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Notionのプロパティに合わせてデータを作る
    # Title (title), URL (url), Authors (rich_text), Abstract (rich_text)
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "URL": {
                "url": url
            },
            "Authors": {
                "rich_text": [{"text": {"content": authors[:2000] if authors else ""}}]
            },
            "Abstract": {
                "rich_text": [{"text": {"content": abstract[:2000] if abstract else ""}}]
            }
        }
    }
    
    try:
        response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Successfully added to Notion: {title[:30]}...")
        else:
            print(f"Failed to add to Notion: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error connecting to Notion: {e}")
