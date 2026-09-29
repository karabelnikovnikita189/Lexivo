import sqlite3

from datetime import date
from config import DB_PATH, DAILY_FREE_LIMIT


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            requests_today INTEGER DEFAULT 0,
            last_request_date TEXT,
            is_vip INTEGER DEFAULT 0
        )
    """)
    # Создание таблицы истории запросов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transcriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT,
        transcription TEXT,
        summary TEXT,
        translated TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    conn.close()


#------------------------------------------------------------------

def set_vip_status(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO users (user_id, requests_today, last_request_date, is_vip) VALUES (?, 0, ?, 1)",
            (user_id, str(date.today()))
        )
    conn.commit()
    conn.close()

#------------------------------------------------------------------

def check_and_update_limit(user_id: int) -> tuple[bool, int]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = str(date.today())

    cursor.execute("SELECT requests_today, last_request_date, is_vip FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute(
            "INSERT INTO users (user_id, requests_today, last_request_date, is_vip) VALUES (?, 1, ?, 0)",
            (user_id, today_str)
        )
        conn.commit()
        conn.close()
        return True, DAILY_FREE_LIMIT - 1

    requests_today, last_request_date, is_vip = row

    if is_vip == 1:
        conn.close()
        return True, 999

    if last_request_date != today_str:
        requests_today = 0
        last_request_date = today_str

    if requests_today >= DAILY_FREE_LIMIT:
        conn.close()
        return False, 0

    requests_today += 1
    cursor.execute(
        "UPDATE users SET requests_today = ?, last_request_date = ? WHERE user_id = ?",
        (requests_today, last_request_date, user_id)
    )
    conn.commit()
    conn.close()

    left_requests = DAILY_FREE_LIMIT - requests_today
    return True, left_requests

#------------------------------------------------------------------

def get_user_stats(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = str(date.today())

    cursor.execute("SELECT requests_today, last_request_date, is_vip FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"📊 Профиль\n\nДоступно сегодня: {DAILY_FREE_LIMIT} из {DAILY_FREE_LIMIT}\nСтатус: FREE"

    requests_today, last_request_date, is_vip = row

    if is_vip == 1:
        return (
            "👤 Ваш профиль\n\n"
            "👑 Тариф: Lexivo PRO\n\n"
            "♾️ Безлимитные распознавания\n"
            "✅ PDF экспорт\n"
            "✅ Word экспорт\n"
            "✅ История записей\n"
            "✅ Перевод текста\n\n"
            "❤️ Спасибо за поддержку проекта!"
        )
    

    used = 0 if last_request_date != today_str else requests_today
    left = max(0, DAILY_FREE_LIMIT - used)
    return (
        f"👤 Ваш аккаунт\n\n"
        f"📦 Тариф: Free\n\n"
        f"🎁 Использовано сегодня: {used}/{DAILY_FREE_LIMIT}\n"
        f"⚡ Осталось распознаваний: {left}\n\n"
        f"✨ Хотите больше возможностей?\n"
        f"Оформите подписку Lexivo PRO."
    )

#------------------------------------------------------------------

def save_transcription(
    user_id: int,
    title: str,
    transcription: str,
    summary: str
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transcriptions
        (
            user_id,
            title,
            transcription,
            summary
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            title,
            transcription,
            summary
        )
    )

    conn.commit()
    conn.close()

#------------------------------------------------------------------

def get_last_transcriptions(
    user_id: int,
    limit: int = 10
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            created_at
        FROM transcriptions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            user_id,
            limit
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows

#------------------------------------------------------------------


def get_last_transcription(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            transcription,
            summary,
            translated
        FROM transcriptions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_transcription_by_id(
    transcription_id: int
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            title,
            transcription,
            summary,
            translated
        FROM transcriptions
        WHERE id = ?
        """,
        (transcription_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def is_user_vip(user_id: int):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_vip FROM users WHERE user_id = ?",
        (user_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return bool(row and row[0])