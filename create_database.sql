-- システムプロンプト管理データベース作成
CREATE DATABASE IF NOT EXISTS systemprompt;

USE systemprompt;

-- システムプロンプトテーブル
CREATE TABLE IF NOT EXISTS system_prompts (
    id SERIAL PRIMARY KEY,
    prompt_key VARCHAR(100) UNIQUE NOT NULL COMMENT 'プロンプト識別キー',
    prompt_text TEXT NOT NULL COMMENT 'システムプロンプト本文',
    description VARCHAR(500) COMMENT 'プロンプトの説明',
    category VARCHAR(50) DEFAULT 'general' COMMENT 'カテゴリ（strategy/integration/chat等）',
    is_active BOOLEAN DEFAULT true COMMENT '有効フラグ',
    version INTEGER DEFAULT 1 COMMENT 'バージョン番号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT 'system' COMMENT '作成者',
    updated_by VARCHAR(50) DEFAULT 'system' COMMENT '更新者'
);

-- インデックス作成
CREATE INDEX idx_prompt_key ON system_prompts(prompt_key);
CREATE INDEX idx_category ON system_prompts(category);
CREATE INDEX idx_is_active ON system_prompts(is_active);

-- 初期データ投入
INSERT INTO system_prompts (prompt_key, prompt_text, description, category) VALUES
('strategy_planning', 'あなたは戦略立案の専門家です。ユーザーリクエストを分析し、必要最小限のツールのみを選択してください。', '戦略立案用システムプロンプト', 'strategy'),
('integration_response', '証券会社の社内情報システムとして回答してください。', '回答統合用システムプロンプト', 'integration'),
('simple_chat', 'あなたは親切な金融商品アドバイザーです。ユーザーの質問に対して、親しみやすく分かりやすい回答をしてください。', 'シンプルチャット用システムプロンプト', 'chat');

-- 確認
SELECT * FROM system_prompts;
