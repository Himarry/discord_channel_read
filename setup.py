#!/usr/bin/env python3
"""
Discordチャンネル既読処理プログラムのセットアップスクリプト
"""

import subprocess
import sys
import os
import shutil

def main():
    print("Discordチャンネル既読処理プログラムのセットアップを開始します。")
    
    # pipコマンドのチェック
    pip_command = 'pip'
    if shutil.which('pip3'):
        pip_command = 'pip3'
    elif not shutil.which('pip'):
        print("pipコマンドが見つかりません。Pythonとpipをインストールしてください。")
        sys.exit(1)
    
    # 必要なパッケージのインストール
    print(f"必要なパッケージをインストールしています...")
    try:
        subprocess.check_call([pip_command, 'install', 'python-dotenv', 'requests', 'selenium', 'webdriver-manager'])
        print("インストールに成功しました。")
    except subprocess.CalledProcessError:
        print("パッケージのインストールに失敗しました。")
        print("以下のコマンドを手動で実行してください:")
        print(f"{pip_command} install python-dotenv requests selenium webdriver-manager")
        sys.exit(1)
    
    # Seleniumのウェブドライバの確認
    print("\nSelenium Webドライバの確認中...")
    print("注意: プログラム実行時に自動的にダウンロードされます。")
    print("プログラムはChrome、Firefox、Edgeのいずれかのブラウザがインストールされている必要があります。")
    
    # 環境設定ファイルの確認
    if not os.path.exists('.env'):
        print("\n.envファイルが見つかりません。サンプルファイルからコピーします...")
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print(".envファイルを作成しました。このファイルを編集して設定を行ってください。")
        else:
            print(".env.exampleファイルが見つかりません。新しく.envファイルを作成します。")
            with open('.env', 'w') as f:
                f.write("""# Discordアカウント情報
DISCORD_EMAIL=your_email@example.com
DISCORD_PASSWORD=your_password

# DiscordサーバーとチャンネルのID
DISCORD_SERVER_ID=your_server_id_here
DISCORD_CHANNEL_ID=your_channel_id_here

# メッセージ取得数
MESSAGE_LIMIT=100

# 更新間隔（秒）
UPDATE_INTERVAL=60

# ブラウザ設定 (chrome, firefox, edge のいずれか)
BROWSER=chrome
# ヘッドレスモード (true/false)
HEADLESS=true
""")
            print(".envファイルを作成しました。このファイルを編集して設定を行ってください。")
    
    print("\nセットアップが完了しました。")
    print("プログラムを実行するには次のコマンドを使用してください:")
    print("python3 main.py")

if __name__ == "__main__":
    main()
