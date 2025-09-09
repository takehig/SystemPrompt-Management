# SystemPrompt Management

システムプロンプト管理システム - WealthAI Enterprise Systems

## 📋 概要

AIシステムで使用するシステムプロンプトを一元管理するWebアプリケーション。PostgreSQLデータベースを使用し、完全なCRUD機能を提供。

## 🏗️ システム構成

### アーキテクチャ
```
Web Browser
    ↓
Nginx Proxy (Port 80)
    ↓ /systemprompt/
SystemPrompt Management (Port 8007)
    ↓
PostgreSQL (wealthai database)
```

### 技術スタック
- **Backend**: Python FastAPI 0.104.1
- **Database**: PostgreSQL (wealthai database)
- **Frontend**: HTML5, Bootstrap 5, Font Awesome 6
- **Infrastructure**: systemd, Nginx proxy

## 🗄️ データベース設計

### system_prompts テーブル
```sql
CREATE TABLE system_prompts (
    id SERIAL PRIMARY KEY,
    prompt_key VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 初期データ
- `strategy_planning`: 戦略立案用システムプロンプト
- `integration_response`: 回答統合用システムプロンプト  
- `simple_chat`: シンプルチャット用システムプロンプト

## 🔧 機能一覧

### CRUD機能
- **Create**: 新規プロンプト作成（モーダル）
- **Read**: プロンプト一覧表示（テーブル）
- **Update**: プロンプト編集（モーダル）
- **Delete**: プロンプト削除（確認ダイアログ）

### API機能
- `GET /`: Web画面表示
- `POST /create`: プロンプト新規作成
- `POST /update/{id}`: プロンプト更新
- `POST /delete/{id}`: プロンプト削除
- `GET /api/prompt/{key}`: プロンプト取得API
- `GET /api/status`: サービス状態確認

## 🚀 デプロイ・運用

### サービス管理
```bash
# サービス起動
sudo systemctl start systemprompt

# サービス停止
sudo systemctl stop systemprompt

# サービス状態確認
sudo systemctl status systemprompt

# ログ確認
sudo journalctl -u systemprompt -f
```

### 設定ファイル
- **systemd**: `/etc/systemd/system/systemprompt.service`
- **Nginx**: `/etc/nginx/conf.d/default.conf` (プロキシ設定)
- **アプリケーション**: `/home/ec2-user/SystemPrompt-Management/src/main.py`

## 🌐 アクセス情報

### Web画面
- **URL**: http://44.217.45.24:8007/
- **プロキシ経由**: http://44.217.45.24/systemprompt/ (予定)

### API エンドポイント
```bash
# プロンプト取得
curl http://44.217.45.24:8007/api/prompt/strategy_planning

# サービス状態
curl http://44.217.45.24:8007/api/status
```

## 🔒 セキュリティ

### データベース接続
- **ユーザー**: wealthai_user
- **データベース**: wealthai
- **認証**: パスワード認証

### アクセス制御
- **ポート制限**: 8007番ポートはセキュリティグループで制御
- **プロキシ経由**: Nginx経由でのアクセス推奨

## 🔧 開発・メンテナンス

### 開発環境
```bash
# 依存関係インストール
pip install -r requirements_postgres.txt

# ローカル起動
cd src && python main.py
```

### GitHub管理
- **リポジトリ**: https://github.com/takehig/SystemPrompt-Management
- **ブランチ**: master
- **デプロイ**: GitHub → EC2 git pull

### トラブルシューティング
1. **サービス起動失敗**: PostgreSQL接続確認
2. **画面表示エラー**: ログでPython構文エラー確認
3. **API応答なし**: ポート8007の稼働状況確認

## 📈 今後の拡張予定

### 機能拡張
- **カテゴリ分類**: プロンプトのカテゴリ管理
- **バージョン管理**: プロンプト履歴管理
- **権限管理**: ユーザー別編集権限
- **ログ機能**: 使用履歴記録

### システム統合
- **AIChat統合**: 動的プロンプト切り替え
- **CRM統合**: 顧客対応プロンプト管理
- **MCP統合**: MCP用プロンプト管理

## 📝 更新履歴

- **v1.0.0** (2025-09-09): 初期リリース - PostgreSQL版CRUD機能完成
