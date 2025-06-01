import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

# ロギング設定
logger = logging.getLogger(__name__)

class DiscordSeleniumManager:
    """SeleniumによるDiscordの操作を管理するクラス"""
    
    def __init__(self, config):
        """
        コンストラクタ
        
        Args:
            config (dict): 設定情報
        """
        self.config = config
        self.driver = None
        self.logged_in = False
    
    def init_driver(self):
        """Seleniumドライバを初期化する"""
        browser_name = self.config.get('browser', 'chrome').lower()
        headless = self.config.get('headless', 'true').lower() == 'true'
        
        logger.info(f"{browser_name}ブラウザを初期化しています...")
        
        try:
            if browser_name == 'chrome':
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-infobars')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_argument('--mute-audio')
                
                # Service オブジェクトを作成
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif browser_name == 'firefox':
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                
                # Service オブジェクトを作成
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                
            elif browser_name == 'edge':
                options = webdriver.EdgeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                
                # Service オブジェクトを作成
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
            
            else:
                logger.error(f"サポートされていないブラウザ: {browser_name}")
                raise ValueError(f"サポートされていないブラウザ: {browser_name}")
            
            # ウィンドウサイズを設定
            self.driver.set_window_size(1280, 800)
            
            logger.info(f"ブラウザを正常に初期化しました: {browser_name}")
            return True
            
        except Exception as e:
            logger.error(f"ブラウザの初期化中にエラーが発生しました: {e}")
            return False
    
    def login(self):
        """Discordにログインする"""
        if not self.driver:
            if not self.init_driver():
                return False
        
        try:
            logger.info("Discordログイン処理を開始します...")
            self.driver.get('https://discord.com/login')
            
            # ページの読み込みを待つ
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'email'))
            )
            
            # ログインフォームに入力
            email_input = self.driver.find_element(By.NAME, 'email')
            password_input = self.driver.find_element(By.NAME, 'password')
            
            email_input.clear()
            email_input.send_keys(self.config['email'])
            password_input.clear()
            password_input.send_keys(self.config['password'])
            password_input.send_keys(Keys.RETURN)
            
            # ログイン成功を待つ（ホーム画面に遷移するのを待つ）
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda driver: 'channels/' in driver.current_url
                )
                logger.info("Discordにログインしました")
                self.logged_in = True
                return True
            except TimeoutException:
                # CAPTCHAやその他の認証が必要な場合
                logger.warning("ログイン後の遷移を確認できませんでした。CAPTCHA等の追加認証が必要かもしれません。")
                
                # 手動介入のためにしばらく待機（ヘッドレスモードでない場合）
                if self.config.get('headless', 'true').lower() != 'true':
                    logger.info("手動でのログイン操作を待機しています...（30秒）")
                    time.sleep(30)
                    if 'channels/' in self.driver.current_url:
                        logger.info("手動ログインが検出されました")
                        self.logged_in = True
                        return True
                
                logger.error("ログインに失敗しました。メールアドレスとパスワードを確認してください。")
                return False
                
        except Exception as e:
            logger.error(f"ログイン中にエラーが発生しました: {e}")
            return False
    
    def navigate_to_channel(self, server_id, channel_id):
        """指定したチャンネルに移動する"""
        if not self.logged_in and not self.login():
            return False
        
        try:
            channel_url = f"https://discord.com/channels/{server_id}/{channel_id}"
            logger.info(f"チャンネルに移動しています: {channel_url}")
            
            self.driver.get(channel_url)
            
            # チャンネルの読み込みを待つ
            WebDriverWait(self.driver, 15).until(
                lambda driver: 'channels/' in driver.current_url
            )
            
            # 少し待機してページが完全にロードされるのを待つ
            time.sleep(3)
            
            logger.info("チャンネルに正常に移動しました")
            return True
            
        except TimeoutException:
            logger.error("チャンネルの読み込みに失敗しました。チャンネルIDが正しいか確認してください。")
            return False
        except Exception as e:
            logger.error(f"チャンネル移動中にエラーが発生しました: {e}")
            return False
    
    def find_and_click_read_button(self):
        """既読ボタンを見つけてクリックする"""
        try:
            # 様々な方法でボタンを探す
            wait = WebDriverWait(self.driver, 5)
            
            # 方法1: テキストで検索（XPath）
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "既読にする")]')))
                logger.info("既読ボタン（テキスト検索）を見つけました")
                button.click()
                return True
            except:
                pass
            
            # 方法2: クラス名とテキストの組み合わせ
            try:
                button = self.driver.find_element(By.XPATH, '//button[contains(@class, "barButtonAlt") and contains(text(), "既読にする")]')
                if button.is_displayed() and button.is_enabled():
                    logger.info("既読ボタン（クラス+テキスト検索）を見つけました")
                    button.click()
                    return True
            except:
                pass
            
            # 方法3: SVGアイコンを含むボタンを探す
            try:
                button = self.driver.find_element(By.XPATH, '//button[contains(@class, "barButton") and .//svg]')
                if button.is_displayed() and button.is_enabled() and "既読" in button.text:
                    logger.info("既読ボタン（SVG検索）を見つけました")
                    button.click()
                    return True
            except:
                pass
            
            # 方法4: すべてのボタンを検索してテキストをチェック
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if button.is_displayed() and button.is_enabled() and "既読" in button.text:
                        logger.info("既読ボタン（全ボタン検索）を見つけました")
                        button.click()
                        return True
            except:
                pass
            
            logger.info("既読ボタンが見つかりませんでした")
            return False
            
        except Exception as e:
            logger.error(f"既読ボタンの検索中にエラーが発生しました: {e}")
            return False

    def mark_as_read(self, server_id, channel_id):
        """チャンネルを既読状態にする"""
        try:
            if not self.navigate_to_channel(server_id, channel_id):
                return False
            
            # チャンネルに移動して画面を表示するだけで既読になる
            # 少し待機して既読処理が完了するのを待つ
            time.sleep(3)
            
            # 「既読にする」ボタンを探してクリックする
            button_clicked = self.find_and_click_read_button()
            
            if button_clicked:
                logger.info("既読ボタンをクリックしました")
                time.sleep(2)  # クリック後の処理を待つ
            else:
                logger.info("既読ボタンが見つかりませんでした。チャンネルは既に既読状態の可能性があります。")
            
            # オプション: チャネル名の取得を試みる
            try:
                # チャンネル名を取得（異なるセレクタを試す）
                channel_name_selectors = [
                    'h1[data-text-variant="heading-lg/semibold"]',
                    '[class*="title"]',
                    'h1',
                    '[aria-label*="チャンネル"]'
                ]
                
                channel_name = None
                for selector in channel_name_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            channel_name = element.text.strip()
                            break
                    except:
                        continue
                
                if channel_name:
                    logger.info(f"チャンネル '{channel_name}' を既読にしました")
                else:
                    logger.info(f"チャンネル ID:{channel_id} を既読にしました")
            except:
                logger.info(f"チャンネル ID:{channel_id} を既読にしました")
            
            return True
            
        except Exception as e:
            logger.error(f"既読処理中にエラーが発生しました: {e}")
            return False
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            logger.info("ブラウザを閉じています...")
            try:
                self.driver.quit()
                logger.info("ブラウザを正常に閉じました")
            except Exception as e:
                logger.error(f"ブラウザを閉じる際にエラーが発生しました: {e}")
            finally:
                self.driver = None
                self.logged_in = False
