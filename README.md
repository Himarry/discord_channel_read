# Discordチャンネル既読処理プログラム

このプログラムは、指定されたDiscordチャンネル内のメッセージを取得し、ユーザー視点で既読状態にすることを目的としたツールです。

## ⚠️ 注意事項

Discordの自動化やスクレイピングはDiscordの利用規約に抵触する可能性があります。特にユーザートークンを使用した操作は自己bot行為（self-botting）とみなされる可能性があります。実装および運用の前に必ずDiscordの規約を確認してください。

## セットアップ

1. 必要なライブラリをインストールします:
   ```
   pip install -r requirements.txt
   ```

2. `.env.example`ファイルを`.env`にコピーし、必要な情報を入力します:
   ```
   cp .env.example .env
   ```

3. `.env`ファイルを編集して、Discord APIトークン、サーバーID、チャンネルIDを設定します。

## 使用方法

### 基本的な使用方法:
```
python main.py
```

### コマンドラインオプション:
```
python main.py --channel-id CHANNEL_ID [--server-id SERVER_ID] [--limit LIMIT] [--user-token]
```

- `--channel-id`: 既読にするDiscordチャンネルのID（必須）
- `--server-id`: チャンネルが属するDiscordサーバーのID（オプション）
- `--limit`: 取得するメッセージの数（デフォルト: 50）
- `--user-token`: ユーザートークンを使用する場合に指定（既読処理に必要）

## 既読処理について

既読処理を行うには、ユーザートークンが必要です。Botトークンでは既読処理はできません。ユーザートークンを使用する場合は、`--user-token`フラグを指定するか、`.env`ファイルで`USE_USER_TOKEN=true`を設定してください。

## ロギング

プログラムの実行ログは`discord_reader.log`ファイルに記録されます。
