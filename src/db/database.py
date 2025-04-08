import sqlite3
import uuid
from typing import Dict, Any

from src.models.models import License, LicenseUpdate


class DatabaseManager:
    def __init__(self, db_name: str = "licenses.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id TEXT PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    valid_until TEXT NOT NULL,
                    active BOOLEAN NOT NULL
                )
            """)
            conn.commit()

    def create_license(self, license_data: Dict[str, Any]) -> str:
        license_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO licenses (id, name, type, valid_until, active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                license_id,
                license_data['name'],
                license_data['type'],
                license_data['valid_until'],
                license_data['active']
            ))
            conn.commit()
            if cursor.rowcount == 1:
                return license_id
            else:
                return None

    def get_license_by_id(self, license_id: str) -> License:
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM licenses WHERE id = ?", (license_id,))
            result = cursor.fetchone()
            if result:
                return License(**dict(result))
            else:
                raise ValueError("License not found")


    def update_license(self, license_id: str, update_data:LicenseUpdate) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE licenses 
                SET name = ?, type = ?, valid_until = ?, active = ?
                WHERE id = ?
            """, (
                update_data.name,
                update_data.type,
                update_data.valid_until,
                update_data.active,
                license_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_license(self, license_id: int) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM licenses WHERE id = ?", (license_id,))
            conn.commit()
            return cursor.rowcount > 0