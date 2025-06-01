import requests
import logging
import time
from auth import get_token

# ロギング設定
logger = logging.getLogger(__name__)

BASE_URL = "https://discord.com/api/v9"

def mark_channel_as_read(channel_id, last_message_id, config=None):
    """
    特定のメッセージまでDiscordチャンネルを既読にする
    
    Args:
        channel_id (str): 既読にするチャンネルのID
        last_message_id (str): 既読にする最後のメッセージのID
        config (dict): 設定情報
        
    Returns:
        dict: Discord APIからのレスポンス
    """
    token = get_token(config)
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Discord APIの既読エンドポイント
    url = f"{BASE_URL}/channels/{channel_id}/messages/{last_message_id}/ack"
    
    logger.info(f"チャンネル {channel_id} をメッセージ {last_message_id} まで既読にしています")
    
    try:
        response = requests.post(url, headers=headers)
        
        # レートリミット対応
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            logger.warning(f"レート制限に達しました。{retry_after}秒後に再試行します")
            time.sleep(retry_after)
            return mark_channel_as_read(channel_id, last_message_id, config)
        
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"チャンネル {channel_id} を正常に既読にしました")
        return result
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"チャンネルを既読にする際にHTTPエラーが発生しました: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"チャンネルを既読にする際にエラーが発生しました: {e}")
        raise
