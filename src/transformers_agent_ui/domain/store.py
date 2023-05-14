"""The Store provides functionality to store the Runs and Assets"""
from __future__ import annotations

import sqlite3
import warnings
from pathlib import Path
from pickle import dump, load
from uuid import uuid4

from PIL.Image import Image as PIL_Image
from PIL.Image import open as open_pil_image

QUERY_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS RESULTS (
	time TEXT NOT NULL,
    agent TEXT NOT NULL,
   	model TEXT NOT NULL,
	query TEXT NOT NULL,
    result TEXT NOT NULL
)
"""
DB_NAME = "TransformersAgent.db"


class Store:
    """A store for runs"""

    # Implemented as a LocalStore using SQLLite and Files
    # Could later be implemented for example using S3 or Azure blob Storage
    def __init__(self, path: str | Path = ".store"):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        self._db_path = path / DB_NAME
        self._conn = sqlite3.connect(self._db_path)
        self._cursor = self._conn.cursor()
        self._create_table()

        self._asset_path = path / "assets"
        self._asset_path.mkdir(parents=True, exist_ok=True)

    def _create_table(self):
        self._conn.execute(QUERY_CREATE_TABLE)

    def _get_unique_path(self, result) -> str:
        prefix = str(uuid4())
        if isinstance(result, PIL_Image):
            return prefix + ".png"
        return prefix + ".pickle"

    def _write_result(self, result, path: str):
        full_path = self._asset_path / path
        if isinstance(result, PIL_Image):
            result.save(full_path)
        elif path.endswith(".pickle"):
            with full_path.open("wb") as file:
                dump(result, file)
            message = f"Saved type {type(result)} as pickle file to {full_path}"
            warnings.warn(message)
        else:
            raise NotImplementedError()

    def _write_to_db(self, agent: str, model: str, query: str, result: str):
        parameters = [
            (agent, model, query, result),
        ]
        self._cursor.executemany(
            "INSERT INTO RESULTS VALUES(datetime('now'), ?, ?, ?, ?)", parameters
        )
        self._conn.commit()

    def write(self, agent: str, model: str, query: str, result):
        """Writes the run to the store"""
        path = self._get_unique_path(result)

        self._write_result(result, path)
        self._write_to_db(agent, model, query, path)

    def read(self, agent: str, model: str, query):
        """Reads the latest run from the store if it exists"""
        res = self._cursor.execute(
            """SELECT result FROM RESULTS where agent=? and model=? and \
                query=? ORDER BY time DESC LIMIT 1""",
            [agent, model, query],
        )
        result = res.fetchone()

        if result:
            path = result[0]
        else:
            return None
        full_path = self._asset_path / path

        if path.endswith(".png"):
            return open_pil_image(full_path)
        if path.endswith(".pickle"):
            with full_path.open("rb") as file:
                return load(file)  # nosec
        raise NotImplementedError()

    def exists(self, agent: str, model: str, query: str):
        """Returns True if a similar run exists"""
        sql = """SELECT EXISTS(SELECT 1 FROM RESULTS WHERE agent=? and model=? \
            and query=?);"""
        res = self._cursor.execute(sql, [agent, model, query])
        result = res.fetchone()[0]
        return bool(result)

    def delete(self, agent: str, model: str, query: str):
        """Deletes all the runs specified"""
        sql = "DELETE FROM RESULTS WHERE agent=? and model=? and query=?"
        self._cursor.execute(sql, [agent, model, query])
        self._conn.commit()
