import sqlite3
import json
from datetime import datetime
from pathlib import Path
#added
class ProgressDB:
    def __init__(self, db_path="progress.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    topic TEXT,
                    duration INTEGER,
                    word_count INTEGER,
                    wpm REAL,
                    clarity INTEGER,
                    structure INTEGER,
                    filler_words TEXT,
                    top_suggestion TEXT,
                    transcript_preview TEXT
                )
            """)
    
    def save(self, topic: str, duration: int, word_count: int, wpm: float,
             clarity: int, structure: int, filler_words: dict, 
             suggestions: list, transcript: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (timestamp, topic, duration, word_count, wpm, clarity, structure, 
                 filler_words, top_suggestion, transcript_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                topic,
                duration,
                word_count,
                wpm,
                clarity,
                structure,
                json.dumps(filler_words),
                suggestions[0] if suggestions else "",
                transcript[:200] + "..." if len(transcript) > 200 else transcript
            ))
    
    def get_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM sessions ORDER BY timestamp")
            return [dict(row) for row in cursor.fetchall()]