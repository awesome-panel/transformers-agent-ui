"""The Store provides functionality to store the Runs and Assets"""
from __future__ import annotations

import sqlite3
import warnings
from pathlib import Path
from pickle import dump, load
from typing import Dict
from uuid import uuid4

from PIL.Image import Image as PIL_Image
from PIL.Image import open as open_pil_image

# # pylint: disable=unused-argument
# Remove this when we start supporting kwargs
QUERY_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS RESULTS (
	time TEXT NOT NULL,
    agent TEXT NOT NULL,
   	model TEXT NOT NULL,
	task TEXT NOT NULL,
    prompt TEXT NOT NULL,
    explanation TEXT NOT NULL,
    code TEXT NOT NULL,
    value TEXT NOT NULL
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

    def _get_unique_path(self, value) -> str:
        prefix = str(uuid4())
        if isinstance(value, PIL_Image):
            return prefix + ".png"
        return prefix + ".pickle"

    def _write_value(self, value, path: str):
        full_path = self._asset_path / path
        if isinstance(value, PIL_Image):
            value.save(full_path)
        elif path.endswith(".pickle"):
            with full_path.open("wb") as file:
                dump(value, file)
            message = f"Saved type {type(value)} as pickle file to {full_path}"
            warnings.warn(message)
        else:
            raise NotImplementedError()

    def _write_to_db(
        self,
        agent: str,
        model: str,
        task: str,
        kwargs: Dict,
        prompt: str,
        explanation: str,
        code: str,
        value: str,
    ):
        parameters = [
            (agent, model, task, prompt, explanation, code, value),
        ]
        self._cursor.executemany(
            "INSERT INTO RESULTS VALUES(datetime('now'), ?, ?, ?, ?, ?, ?, ?)", parameters
        )
        self._conn.commit()

    def write(
        self,
        agent: str,
        model: str,
        task: str,
        kwargs: Dict,
        prompt: str,
        explanation: str,
        code: str,
        value,
    ):
        """Writes the run to the store"""
        path = self._get_unique_path(value)

        self._write_value(value, path)
        self._write_to_db(agent, model, task, kwargs, prompt, explanation, code, value=path)

    def read(self, agent: str, model: str, task: str, kwargs: Dict) -> Dict:
        """Reads the latest run from the store if it exists"""
        res = self._cursor.execute(
            """SELECT prompt, explanation, code, value FROM RESULTS where agent=? and model=? and \
                task=? ORDER BY time DESC LIMIT 1""",
            [agent, model, task],
        )
        result = res.fetchone()

        if result:
            prompt, explanation, code, path = result
        else:
            return {}

        full_path = self._asset_path / path

        if path.endswith(".png"):
            value = open_pil_image(full_path)
        elif path.endswith(".pickle"):
            with full_path.open("rb") as file:
                value = load(file)  # nosec
        else:
            raise NotImplementedError()

        return {"prompt": prompt, "explanation": explanation, "code": code, "value": value}

    def exists(self, agent: str, model: str, task: str, kwargs: Dict) -> bool:
        """Returns True if a similar run exists"""
        sql = """SELECT EXISTS(SELECT 1 FROM RESULTS WHERE agent=? and model=? \
            and task=?);"""
        res = self._cursor.execute(sql, [agent, model, task])
        value = res.fetchone()[0]
        return bool(value)

    def delete(self, agent: str, model: str, task: str):
        """Deletes all the runs specified"""
        sql = "DELETE FROM RESULTS WHERE agent=? and model=? and task=?"
        self._cursor.execute(sql, [agent, model, task])
        self._conn.commit()
