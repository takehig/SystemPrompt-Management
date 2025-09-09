# SystemPrompt Management API仕様書

## 📋 概要

SystemPrompt Management システムのAPI仕様書

**Base URL**: `http://44.217.45.24:8007`

## 🔌 API エンドポイント

### 1. Web画面表示

#### `GET /`
システムプロンプト管理画面を表示

**Response**: HTML画面
- プロンプト一覧テーブル
- 新規作成・編集・削除機能
- Bootstrap 5 レスポンシブデザイン

---

### 2. プロンプト新規作成

#### `POST /create`
新しいシステムプロンプトを作成

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
```
prompt_key: string (required) - プロンプトキー（英数字・アンダースコア）
description: string (optional) - プロンプト説明
prompt_text: string (required) - プロンプト本文
```

**Response**: 
- **Success**: Redirect to `/` (303)
- **Error**: HTTP 400 (キー重複) / HTTP 500 (サーバーエラー)

**Example**:
```bash
curl -X POST http://44.217.45.24:8007/create \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "prompt_key=test_prompt&description=テスト用&prompt_text=これはテスト用プロンプトです。"
```

---

### 3. プロンプト更新

#### `POST /update/{prompt_id}`
既存のシステムプロンプトを更新

**Path Parameters**:
- `prompt_id`: integer - プロンプトID

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
```
description: string (optional) - プロンプト説明
prompt_text: string (required) - プロンプト本文
```

**Response**: 
- **Success**: Redirect to `/` (303)
- **Error**: HTTP 500 (サーバーエラー)

**Example**:
```bash
curl -X POST http://44.217.45.24:8007/update/1 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "description=更新された説明&prompt_text=更新されたプロンプト文章"
```

---

### 4. プロンプト削除

#### `POST /delete/{prompt_id}`
システムプロンプトを削除

**Path Parameters**:
- `prompt_id`: integer - プロンプトID

**Response**: 
```json
{
  "status": "success"
}
```

**Example**:
```bash
curl -X POST http://44.217.45.24:8007/delete/1
```

---

### 5. プロンプト取得API

#### `GET /api/prompt/{prompt_key}`
指定されたキーのプロンプトを取得

**Path Parameters**:
- `prompt_key`: string - プロンプトキー

**Response**:
```json
{
  "prompt_key": "strategy_planning",
  "prompt_text": "あなたは戦略立案の専門家です。ユーザーリクエストを分析し、必要最小限のツールのみを選択してください。"
}
```

**Error Response**:
```json
{
  "detail": "Prompt not found"
}
```

**Example**:
```bash
curl http://44.217.45.24:8007/api/prompt/strategy_planning
```

---

### 6. サービス状態確認

#### `GET /api/status`
サービスの稼働状態を確認

**Response**:
```json
{
  "status": "running",
  "service": "SystemPrompt Management",
  "version": "1.0.0",
  "database": "PostgreSQL"
}
```

**Example**:
```bash
curl http://44.217.45.24:8007/api/status
```

## 🗄️ データ構造

### SystemPrompt オブジェクト
```json
{
  "id": 1,
  "prompt_key": "strategy_planning",
  "description": "戦略立案用システムプロンプト",
  "prompt_text": "あなたは戦略立案の専門家です...",
  "created_at": "2025-09-09T05:00:00Z",
  "updated_at": "2025-09-09T05:00:00Z"
}
```

## 🚨 エラーコード

| コード | 説明 | 対処方法 |
|--------|------|----------|
| 400 | Bad Request | パラメータ確認・キー重複確認 |
| 404 | Not Found | プロンプトキー存在確認 |
| 500 | Internal Server Error | サーバーログ確認・DB接続確認 |

## 🔒 認証・セキュリティ

### 現在の実装
- **認証**: なし（内部システム用）
- **アクセス制御**: セキュリティグループによるポート制限
- **データ検証**: SQLインジェクション対策（psycopg2使用）

### 今後の拡張予定
- **API Key認証**: 外部システム連携時
- **ユーザー認証**: 権限管理機能追加時
- **HTTPS対応**: 本番環境デプロイ時

## 📊 使用例

### AIChat システムとの連携
```python
import requests

# プロンプト取得
response = requests.get('http://44.217.45.24:8007/api/prompt/strategy_planning')
prompt_data = response.json()
system_prompt = prompt_data['prompt_text']

# AI対話で使用
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "ユーザーの質問"}
]
```

### 動的プロンプト切り替え
```javascript
// フロントエンドでプロンプト切り替え
async function switchPrompt(promptKey) {
    const response = await fetch(`/api/prompt/${promptKey}`);
    const data = await response.json();
    return data.prompt_text;
}
```
