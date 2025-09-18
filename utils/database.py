# SystemPrompt Management Database Utilities

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """AIChat データベース接続を取得"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

async def get_all_system_prompts():
    """全システムプロンプト取得"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY prompt_key) as id, 
                   prompt_key, 
                   '' as description, 
                   prompt_text, 
                   created_at, 
                   updated_at 
            FROM system_prompts 
            ORDER BY prompt_key
        """)
        
        prompts = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return prompts
        
    except Exception as e:
        logger.error(f"Failed to get system prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

async def get_system_prompt_by_key(prompt_key: str):
    """システムプロンプトをキーで取得"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT prompt_key, prompt_text, created_at, updated_at FROM system_prompts WHERE prompt_key = %s",
            (prompt_key,)
        )
        
        prompt = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return prompt
        
    except Exception as e:
        logger.error(f"Failed to get system prompt {prompt_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

async def update_system_prompt(prompt_key: str, prompt_text: str):
    """システムプロンプト更新"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE system_prompts 
            SET prompt_text = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE prompt_key = %s
        """, (prompt_text, prompt_key))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Failed to update system prompt {prompt_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

async def create_system_prompt(prompt_key: str, prompt_text: str):
    """新規システムプロンプト作成"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO system_prompts (prompt_key, prompt_text) 
            VALUES (%s, %s)
        """, (prompt_key, prompt_text))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create system prompt {prompt_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

async def delete_system_prompt(prompt_key: str):
    """システムプロンプト削除"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM system_prompts WHERE prompt_key = %s", (prompt_key,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Failed to delete system prompt {prompt_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
