# Discordチャンネル既読処理プログラム

このプログラムは、指定されたDiscordチャンネル内のメッセージを取得し、ブラウザ自動化（Selenium）を使用してユーザー視点で既読状態にすることを目的としたツールです。

## ⚠️ 注意事項

Discordの自動化やスクレイピングはDiscordの利用規約に抵触する可能性があります。このツールはブラウザ自動化によりDiscordを操作するため、自己bot行為（self-botting）とみなされる可能性があります。実装および運用の前に必ずDiscordの規約を確認し、自己責任でご利用ください。

## セットアップ

### 自動セットアップ（推奨）
```
python3 setup.py
```

### 手動セットアップ
1. 必要なライブラリをインストールします:
   ```
   pip install python-dotenv requests selenium webdriver-manager
   ```

2. `.env`ファイルを編集して、Discordアカウント情報、サーバーID、チャンネルIDを設定します。

## 必要な環境

- Python 3.7以上
- Chrome、Firefox、Edgeのいずれかのブラウザ（Webドライバは自動ダウンロードされます）
- Discordアカウント（メールアドレスとパスワード）

## 設定ファイル（.env）

```
# Discordアカウント情報
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
```

## 使用方法

### 基本的な使用方法:
```
python3 main.py
```

### コマンドラインオプション:
```
python3 main.py --channel-id CHANNEL_ID [--server-id SERVER_ID] [--interval INTERVAL] [--email EMAIL] [--password PASSWORD]
```

- `--channel-id`: 既読にするDiscordチャンネルのID（必須）
- `--server-id`: チャンネルが属するDiscordサーバーのID（オプション、DMの場合は不要）
- `--interval`: 定期実行の間隔（秒）。0または未指定で単発実行
- `--email`: Discordアカウントのメールアドレス
- `--password`: Discordアカウントのパスワード
- `--limit`: 取得するメッセージの数（デフォルト: 100）

### 使用例:

**単発実行:**
```
python3 main.py --channel-id 1234567890123456789 --server-id 9876543210987654321
```

**60秒ごとの定期実行:**
```
python3 main.py --channel-id 1234567890123456789 --interval 60
```

## 既読処理について

このプログラムはSeleniumを使用してWebブラウザを自動化し、実際のユーザーがDiscordを操作するのと同じ方法でチャンネルを既読にします。具体的には：

1. Discordにログイン
2. 指定されたチャンネルに移動
3. 「既読にする」ボタンがあればクリック
4. チャンネルを表示することで既読状態にする

## ブラウザ設定

- **ヘッドレスモード**: `HEADLESS=true`でブラウザウィンドウを表示せずに実行
- **ブラウザ選択**: `BROWSER`でchrome、firefox、edgeから選択可能
- **自動ドライバ管理**: WebDriverは自動的にダウンロード・管理されます

## ログ機能

プログラムの実行ログは以下に記録されます：
- コンソール出力
- `discord_reader.log`ファイル

## トラブルシューティング

### よくある問題

1. **ログインに失敗する**
   - メールアドレスとパスワードが正しいか確認
   - 二段階認証をオンになっている　※ニ段階認証には対応していません※

2. **ブラウザが起動しない**
   - Chrome、Firefox、Edgeのいずれかがインストールされているか確認 ※chromeのみ動作確認済み※
   - セットアップスクリプトを再実行

3. **チャンネルが見つからない**
   - チャンネルIDとサーバーIDが正しいか確認
   - チャンネルへのアクセス権限（閲覧できる状態）があるか確認

## セキュリティ

- 認証情報は`.env`ファイルで管理し、リポジトリにコミットしないでください
- `.env`ファイルは適切なファイル権限で保護してください
- 開発者は何があろうと責任を取りません、本ツールの使用は自己責任で行ってください。
