import logging
import sys
import time
import os

try:
    from config import load_config
    from selenium_manager import DiscordSeleniumManager
except ModuleNotFoundError as e:
    if "No module named 'dotenv'" in str(e) or "No module named 'selenium'" in str(e):
        print("必要なパッケージがインストールされていません。")
        print("以下のコマンドを実行してインストールしてください：")
        print("pip install python-dotenv requests selenium webdriver-manager")
        print("\nまたは、")
        print("pip3 install python-dotenv requests selenium webdriver-manager")
        print("\nもしくはセットアップスクリプトを実行してください：")
        print("python3 setup.py")
        sys.exit(1)
    else:
        raise

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_reader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_channel_selenium(config, selenium_manager):
    """Seleniumを使用してチャンネルを処理して既読にする"""
    try:
        server_id = config.get('server_id', '@me')  # サーバーIDがない場合は@meを使用
        channel_id = config['channel_id']
        
        # Seleniumを使用してチャンネルを既読にする
        success = selenium_manager.mark_as_read(server_id, channel_id)
        
        if success:
            logger.info("チャンネルを正常に既読にしました")
            return True
        else:
            logger.error("チャンネルの既読処理に失敗しました")
            return False
            
    except Exception as e:
        logger.error(f"Seleniumチャンネル処理中にエラーが発生しました: {e}")
        return False

def main():
    """Discordチャンネル既読処理のメイン関数"""
    selenium_manager = None
    
    try:
        # 設定の読み込み
        config = load_config()
        channel_id = config['channel_id']
        update_interval = config['update_interval']
        
        # SeleniumマネージャーAPI失敗対策のため使用
        logger.info("ブラウザ自動化モード（Selenium）を使用します")
        selenium_manager = DiscordSeleniumManager(config)
        
        # 初回ログイン
        if not selenium_manager.login():
            logger.error("Discordへのログインに失敗しました")
            sys.exit(1)
        
        # 単発実行または定期実行
        if update_interval <= 0:
            # 単発実行
            process_channel_selenium(config, selenium_manager)
            logger.info("Discordチャンネル既読処理が完了しました")
        else:
            # 定期実行
            logger.info(f"{update_interval}秒ごとに更新を実行します。Ctrl+Cで終了できます。")
            try:
                while True:
                    start_time = time.time()
                    
                    success = process_channel_selenium(config, selenium_manager)
                    if success:
                        logger.info(f"更新が完了しました。次の更新まで待機中...")
                    else:
                        logger.warning("更新に失敗しました。次の更新まで待機中...")
                    
                    # 経過時間を考慮して、次の実行までの待機時間を計算
                    elapsed = time.time() - start_time
                    wait_time = max(0, update_interval - elapsed)
                    
                    if wait_time > 0:
                        time.sleep(wait_time)
            except KeyboardInterrupt:
                logger.info("ユーザーによって処理が中断されました")
        
    except ValueError as e:
        logger.error(f"設定エラー: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Seleniumマネージャーのクリーンアップ
        if selenium_manager:
            selenium_manager.close()

if __name__ == "__main__":
    main()
