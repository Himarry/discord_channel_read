import requests
import json
import os
import logging
import time

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# トークンキャッシュファイル
TOKEN_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.token_cache')

def login_to_discord(email, password):
    """
    Discordにメールアドレスとパスワードでログインし、トークンを取得する
    
    Args:
        email (str): Discordアカウントのメールアドレス
        password (str): Discordアカウントのパスワード
        
    Returns:
        str: 認証トークン
    """
    logger.info("Discordへのログインを試みています...")
    
    # キャッシュからトークンを取得
    cached_token = get_cached_token()
    if cached_token:
        logger.info("キャッシュされたトークンを使用します")
        # トークンの有効性を確認
        if verify_token(cached_token):
            logger.info("キャッシュされたトークンは有効です")
            return cached_token
        logger.warning("キャッシュされたトークンは無効です。再ログインします")
    
    url = "https://discord.com/api/v9/auth/login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        "login": email,
        "password": password,
        "undelete": False,
        "captcha_key": None,
        "login_source": None,
        "gift_code_sku_id": None
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        token = data.get('token')
        
        if not token:
            logger.error("ログインに成功しましたが、トークンを取得できませんでした")
            if 'mfa' in data and data['mfa']:
                logger.error("このアカウントは二段階認証が有効になっています。二段階認証には対応していません")
            raise ValueError("トークンを取得できませんでした")
        
        # トークンをキャッシュに保存
        cache_token(token)
        
        logger.info("Discordへのログインに成功しました")
        return token
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            logger.error("ログインに失敗しました。メールアドレスまたはパスワードが間違っています")
        else:
            logger.error(f"ログイン中にHTTPエラーが発生しました: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"ログイン中にエラーが発生しました: {e}")
        raise

def verify_token(token):
    """トークンが有効かどうかを確認する"""
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        return response.status_code == 200
    except:
        return False

def get_cached_token():
    """キャッシュからトークンを取得する"""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                # 有効期限をチェック (24時間とする)
                if time.time() - data.get('timestamp', 0) < 24 * 60 * 60:
                    return data.get('token')
    except Exception as e:
        logger.warning(f"キャッシュからトークンを読み込めませんでした: {e}")
    
    return None

def cache_token(token):
    """トークンをキャッシュに保存する"""
    try:
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump({
                'token': token,
                'timestamp': time.time()
            }, f)
        # ファイルのアクセス権を制限
        os.chmod(TOKEN_CACHE_FILE, 0o600)
    except Exception as e:
        logger.warning(f"トークンをキャッシュに保存できませんでした: {e}")

def get_token(config):
    """設定からトークンを取得する"""
    try:
        # メールとパスワードからログイン
        token = login_to_discord(config['email'], config['password'])
        return token
    except Exception as e:
        logger.error(f"認証エラー: {e}")
        raise
