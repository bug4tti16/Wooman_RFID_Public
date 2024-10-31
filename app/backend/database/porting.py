import pathlib, os

from alive_progress import alive_it
from datetime import datetime
from jamo import h2j,j2hcj
from sqlalchemy import select,text, func
from sqlalchemy.orm import Session

from .tables import User, Log
from .core import database


class TransferData:
    def __init__(self):
        self._is_data=True if database._engine("old") else False

    def find_user(
        self,
        session: Session,
        num: int | None = None,
        name: str | None = None,
        rfid: str | None = None,
    ) -> User | None:
        if num and name:
            res = session.execute(
                select(User).where(User.name == name).where(User.card_number == num)
            ).first()
            if res:
                return res[0]
            else:
                return None
        if num:
            res = session.execute(
                select(User).where(User.active == 1).where(User.card_number == num)
            ).first()
            if res:
                return res[0]
            else:
                return None
        elif rfid:
            res = session.execute(
                select(User).where(User.active == 1).where(User.card_rfid == rfid)
            ).first()
            if res:
                return res[0]
            else:
                return None
        raise Exception("No argument given")

    def port_user(self):
        if not self._is_data:
            return None
        exec_str = text("SELECT DISTINCT num,name from parsed_data")
        session_old = database._session("old")
        session_new = database._session("new")
        for t in alive_it(
            session_old.execute(exec_str), title="Porting User Data: Base  "
        ):
            if not t[1]:
                pass
            elif self.find_user(session=session_new, num=t[0], name=t[1]):
                pass
            else:
                session_new.add(
                    User(
                        name=t[1],
                        card_number=t[0],
                        active=0,
                        name_jamo=j2hcj(h2j(t[1])),
                    )
                )
        session_new.commit()
        exec_str = text("SELECT * FROM users")
        for t in alive_it(
            session_old.execute(exec_str), title="Porting user data: RFID  "
        ):
            if not t[1]:
                pass
            else:
                search = self.find_user(session=session_new, num=t[0], name=t[1])
                if not search:
                    pass
                elif search.active:
                    pass
                else:
                    if t[2] != "#":
                        search.card_rfid = t[2].strip("#")
                    search.active = 1
                    session_new.add(search)
        print("msg:  Committing")
        session_new.commit()
        print("msg:  Done\n")
        session_new.close()
        session_old.close()

    def port_history(self):
        if not self._is_data:
            return None
        session_old = database._session("old")
        session_new = database._session("new")
        exec_str = text("SELECT * FROM parsed_data ORDER BY date ASC")
        max_time = session_new.execute(
            statement=select(func.max(Log.timestamp))
        ).first()
        if max_time[0]:
            max_time: str = max_time[0].strftime("%F")
            exec_str = text(
                f"""SELECT * FROM parsed_data WHERE DATE(date)>"{max_time}" ORDER BY date ASC"""
            )
        cnt = 0
        for t in alive_it(session_old.execute(exec_str), title="Porting history:  "):
            if t[2]:
                # Find user object
                user_obj = self.find_user(session=session_new, num=t[1], name=t[2])
                if not user_obj:
                    # redundunt failsafe
                    user_obj = User(card_number=t[1], name=t[2], active=0)
                    session_new.add(user_obj)
                    session_new.commit()
                    session_new.refresh(user_obj)
                # Create log object
                log_obj = Log(
                    timestamp=datetime.fromisoformat(t[3]),
                    menu=t[4],
                    card=0 if t[5] == 1 else 1,
                    user_id=user_obj.id,
                )
                session_new.add(log_obj)
                cnt += 1
            if cnt == 1000:
                print("msg:  Committing")
                session_new.commit()
                print("msg:  Done\n")
                cnt = 0
        print("msg:  Committing")
        session_new.commit()
        print("msg:  Done")
        session_new.close()
        session_old.close()


