import os
import argparse
import logging
import getpass

try:
    from dotenv import load_dotenv
except ImportError:
    # dotenvがインストールされていない場合の代替処理
    def load_dotenv():
        """dotenvがインストールされていない場合の代替関数"""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# ロギング設定
logger = logging.getLogger(__name__)

def load_config():
    """環境変数とコマンドライン引数から設定を読み込む"""
    load_dotenv()
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Discordチャンネル既読処理')
    parser.add_argument('--server-id', help='DiscordサーバーID')
    parser.add_argument('--channel-id', help='DiscordチャンネルID')
    parser.add_argument('--limit', type=int, default=50, help='取得するメッセージ数')
    parser.add_argument('--interval', type=int, help='更新間隔（秒）')
    parser.add_argument('--email', help='Discordアカウントのメールアドレス')
    parser.add_argument('--password', help='Discordアカウントのパスワード')
    
    args = parser.parse_args()
    
    # 優先順位: コマンドライン引数 > 環境変数 > デフォルト値
    config = {
        'server_id': args.server_id or os.getenv('DISCORD_SERVER_ID'),
        'channel_id': args.channel_id or os.getenv('DISCORD_CHANNEL_ID'),
        'limit': args.limit or int(os.getenv('MESSAGE_LIMIT', 50)),
        'update_interval': args.interval or int(os.getenv('UPDATE_INTERVAL', 0)),
        'email': args.email or os.getenv('DISCORD_EMAIL'),
        'password': args.password or os.getenv('DISCORD_PASSWORD')
    }
    
    # 必須設定の検証
    if not config['channel_id']:
        logger.error("チャンネルIDが必要ですが、提供されていません")
        raise ValueError("チャンネルIDが必要です")
    
    # メールアドレスとパスワードの検証と入力要求
    if not config['email']:
        config['email'] = input("Discordのメールアドレスを入力してください: ")
    
    if not config['password']:
        config['password'] = getpass.getpass("Discordのパスワードを入力してください: ")
    
    logger.info(f"設定を読み込みました: server_id={config['server_id']}, channel_id={config['channel_id']}, update_interval={config['update_interval']}秒")
    return config
