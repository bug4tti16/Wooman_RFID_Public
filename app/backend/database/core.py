from os.path import join, isfile
from pathlib import Path
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Literal

from .tables import Base


class Database:
    def __init__(self):
        old_db = join(Path(__file__).parent.parent.parent.parent, "data", "data_old.db")
        engine_old = create_engine("sqlite:///" + old_db) if isfile(old_db) else None

        new_db = join(Path(__file__).parent.parent.parent.parent, "data", "data.db")
        engine_new = create_engine("sqlite:///" + new_db)
        self._connections = {
            "new": {"engine": engine_new, "session": sessionmaker(engine_new)},
            "old": (
                {"engine": engine_old, "session": sessionmaker(engine_old)}
                if engine_old
                else None
            ),
        }
        if not isfile(new_db):
            self._create_db()

    def _session(self, options: Literal["new", "old"] = "new") -> Session | None:

        return (
            self._connections[options]["session"]()
            if self._connections[options]
            else None
        )

    def _engine(self, options: Literal["new", "old"] = "new") -> Engine | None:

        return (
            self._connections[options]["engine"] if self._connections[options] else None
        )

    def _create_db(self):
        Base.metadata.create_all(self._engine("new"))


database = Database()
