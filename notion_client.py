import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# 環境変数を読み込む
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def add_paper_to_notion(title, url, authors, abstract, abstract_jp="", topic=""):
    # ... (エラーチェック)
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

    # JST (UTC+9) のタイムゾーンを作成
    JST = timezone(timedelta(hours=9), 'JST')
    
    # 日付をJSTで取得 (YYYY-MM-DD)
    today_str = datetime.now(JST).strftime('%Y-%m-%d')

    # Notionのプロパティに合わせてデータを作る
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Read": {
                "checkbox": False
            },
            "Date": {
                "date": {"start": today_str}
            },
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Topic": {
                "rich_text": [{"text": {"content": topic if topic else ""}}]
            },
            "Abstract_JP": {
                "rich_text": [{"text": {"content": abstract_jp[:2000] if abstract_jp else ""}}]
            },
            "Abstract": {
                "rich_text": [{"text": {"content": abstract[:2000] if abstract else ""}}]
            },
            "Authors": {
                "rich_text": [{"text": {"content": authors[:2000] if authors else ""}}]
            },
            "URL": {
                "url": url
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
