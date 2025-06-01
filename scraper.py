import requests
import logging
import time
from auth import get_token

# ロギング設定
logger = logging.getLogger(__name__)

BASE_URL = "https://discord.com/api/v9"

def get_channel_messages(channel_id, limit=50, config=None):
    """
    Discordチャンネルからメッセージを取得する
    
    Args:
        channel_id (str): メッセージを取得するチャンネルのID
        limit (int): 取得するメッセージの最大数
        config (dict): 設定情報
        
    Returns:
        list: メッセージオブジェクトのリスト
    """
    token = get_token(config)
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    url = f"{BASE_URL}/channels/{channel_id}/messages?limit={limit}"
    
    logger.info(f"チャンネル {channel_id} からメッセージを取得しています")
    
    try:
        response = requests.get(url, headers=headers)
        
        # レートリミット対応
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            logger.warning(f"レート制限に達しました。{retry_after}秒後に再試行します")
            time.sleep(retry_after)
            return get_channel_messages(channel_id, limit, config)
        
        response.raise_for_status()
        
        messages = response.json()
        logger.info(f"チャンネル {channel_id} から {len(messages)} 件のメッセージを取得しました")
        return messages
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"メッセージ取得中にHTTPエラーが発生しました: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"メッセージ取得中にエラーが発生しました: {e}")
        raise
