from datetime import date
from jamo import h2j, j2hcj
from sqlalchemy import select, func, or_, and_, case, cast,Integer
from sqlalchemy.orm import Session, lazyload
import re

from .tables import User, Log


class Search:
    _base = (
        select(User)
        .where(User.active == 1)
        .options(lazyload(User.use.and_(func.date(Log.timestamp) == date.today())))
    )
    _full = select(User).options(
        lazyload(User.use.and_(func.date(Log.timestamp) == date.today()))
    )
    _history = select(User).options(lazyload(User.use))
    _loadbase = (
        select(User)
        .join(Log)
        .filter(func.date(Log.timestamp) == date.today())
        .group_by(User.id)
        .having(and_(func.max(Log.timestamp).isnot(None), Log.canceled.isnot(1)))
        .order_by(func.max(Log.timestamp).desc())
    )
    _count_menu=(
        select(User)
        .join(Log)
        .filter(func.date(Log.timestamp) == date.today())
        .group_by(User.id)
        .having(and_(func.max(Log.timestamp).isnot(None), Log.canceled.isnot(1),Log.menu.isnot(0)))
        .order_by(func.max(Log.timestamp).desc())
    )

    @classmethod
    def _load(cls, session: Session):
        return [t.tuple()[0] for t in session.execute(statement=cls._loadbase)]

    @classmethod
    def _count(cls, session: Session):
        tot=len(session.execute(statement=cls._loadbase).all())
        men=len(session.execute(statement=cls._count_menu).all())
        res=(men,tot)
        print(res)
        return res

    @classmethod
    def _test(cls, session: Session):
        kw = input("Enter KW...\n")
        print("Exact Matches:")
        result1 = cls.history_exact(session, kw)
        if result1:
            print(result1.card_number, ": ", result1.name)
            for l in result1.use:
                print(l.timestamp)

        print("Close Values:")
        result2 = cls.history_kw(session, kw)
        print(len(result2), " found")
        for t in result2:
            print(t.card_number, ": ", t.name)
            for l in t.use:
                print(l.timestamp)

    @classmethod
    def _exact(cls, session: Session, data: str):
        res = session.execute(
            cls._base.where(
                or_(
                    User.card_rfid.like(data),
                    User.card_number.like(data),
                    User.name.like(data),
                )
            )
        ).all()
        if len(res) == 1:
            return res[0].tuple()[0]

    @classmethod
    def _kw(cls, session: Session, kw: str):
        if kw:
            return [
                t.tuple()[0]
                for t in session.execute(
                    cls._base.where(or_(User.card_number.like(kw), User.name.like(kw)))
                )
            ] + [
                t.tuple()[0]
                for t in session.execute(
                    cls._base.where(
                        or_(
                            User.card_number.like(kw + "%"),
                            User.name_jamo.like(j2hcj(h2j(kw)) + "%"),
                        )
                    ).where(
                        and_(
                            User.card_number.not_like(kw),
                            User.name.not_like(kw),
                        )
                    )
                )
            ]

    @classmethod
    def full_exact(cls, session: Session, data: str):
        res = session.execute(
            cls._full.where(
                or_(
                    User.card_rfid.like(data),
                    User.card_number.like(data),
                    User.name.like(data),
                )
            )
        ).all()
        if len(res) == 1:
            return res[0].tuple()[0]

    @classmethod
    def full_kw(cls, session: Session, kw: str):
        if kw:
            return [
                t.tuple()[0]
                for t in session.execute(
                    cls._full.where(or_(User.card_number.like(kw), User.name.like(kw)))
                )
            ] + [
                t.tuple()[0]
                for t in session.execute(
                    cls._full.where(
                        or_(
                            User.card_number.like(kw + "%"),
                            User.name_jamo.like(j2hcj(h2j(kw)) + "%"),
                        )
                    ).where(
                        and_(
                            User.card_number.not_like(kw),
                            User.name.not_like(kw),
                        )
                    )
                )
            ]

    @classmethod
    def history_exact(cls, session: Session, data: str):
        res = session.execute(
            cls._history.where(
                or_(
                    User.card_rfid.like(data),
                    User.card_number.like(data),
                    User.name.like(data),
                )
            )
        ).all()
        if len(res) == 1:
            return res[0].tuple()[0]

    @classmethod
    def history_kw(cls, session: Session, kw: str):
        if kw:
            return [
                t.tuple()[0]
                for t in session.execute(
                    cls._history.where(
                        or_(User.card_number.like(kw), User.name.like(kw))
                    )
                )
            ] + [
                t.tuple()[0]
                for t in session.execute(
                    cls._full.where(
                        or_(
                            User.card_number.like(kw + "%"),
                            User.name_jamo.like(j2hcj(h2j(kw)) + "%"),
                        )
                    ).where(
                        and_(
                            User.card_number.not_like(kw),
                            User.name.not_like(kw),
                        )
                    )
                )
            ]

    @classmethod
    def _id(cls, session: Session, _id: int):
        res = session.execute(cls._base.where(User.id == _id)).first()
        if res:
            return res.tuple()[0]


class DataValidation:
    @classmethod
    def collate_users(cls, session: Session, num: str, name: str):
        stmt = (
            select(User)
            .options(lazyload(User.use))
            .where(and_(User.name.like(name), User.card_number.like(num)))
            .order_by(User.id)
        )
        res = session.execute(stmt).all()
        print(res)
        if len(res) < 2:
            return None
        target = res[0][0]
        print("target ", target.name, " selected")
        for i in range(len(res)):
            if i != 0:
                if res[i][0].active == 1 and target.active != 1:
                    target.active = 1
                    target.card_rfid = res[i][0].card_rfid
                    session.add(target)
                    print("Changing User", target.name, " to active")
                for x in res[i][0].use:
                    x.user_id = target.id
                    session.add(x)
                session.delete(res[i][0])
                session.commit()

    @classmethod
    def duplicate_num(cls, session: Session, num: str):
        stmt = select(User).where(and_(User.card_number.like(num), User.active == 1))
        return session.execute(stmt).first()

    @classmethod
    def duplicate_all(cls, session: Session, num: str, name: str):
        stmt = select(User).where(
            and_(User.name.like(name), User.card_number.like(num))
        )
        res = session.execute(stmt).all()
        return res if len(res) > 0 else None

    @classmethod
    def _test(cls, session: Session):
        _max = session.execute(select(func.max(User.id))).first()
        if not _max:
            return None
        for i in range(_max[0]):
            print("Checked", i, " out of ", _max[0], "users")
            res = session.execute(select(User).where(User.id == i)).first()
            if res:
                r = cls.duplicate_num(session, str(res[0].card_number))
                if r:
                    print(r[0].name)


class CreateNew:
    @classmethod
    def _user(cls, session: Session, name: str, num: str, rfid: str | None = None):
        DataValidation.collate_users(session=session, num=num, name=name)
        existing_test = DataValidation.duplicate_all(
            session=session, num=num, name=name
        )
        if existing_test:
            to_update: User = existing_test[0][0]
            return Update._user(session=session, user_obj=to_update, rfid=rfid)
        user_obj = User(
            name=name,
            name_jamo=j2hcj(h2j(name)),
            card_number=int(num),
            rfid=rfid,
        )
        session.add(user_obj)
        session.commit()
        session.refresh(user_obj)
        return user_obj

    @classmethod
    def _log(
        cls,
        session: Session,
        user_obj: User | None,
        no_card: bool | None = None,
        _cancel: bool | None = None,
    ):
        if not user_obj:
            return None

        log_obj = Log(user_id=user_obj.id)
        if no_card:
            log_obj.card = 0
        if _cancel:
            log_obj.canceled = 1
        session.add(log_obj)
        session.commit()
        session.refresh(log_obj)
        return log_obj


class Update:
    @classmethod
    def _user(
        cls,
        session: Session,
        user_obj: User,
        name: str | None = None,
        num: str | None = None,
        rfid: str | None = None,
    ):
        user_obj.active = 1
        if name:
            user_obj.name = name
            user_obj.name_jamo = j2hcj(h2j(name))
        if rfid:
            validate = Search.full_exact(session=session, data=rfid)
            overwrite: User | None = validate[0] if validate else None
            if overwrite:
                overwrite.card_rfid = None
                session.add(overwrite)
                session.commit()
            user_obj.card_rfid = rfid
        if num:
            validate = Search._exact(session=session, data=num)
            overwrite = validate[0] if validate else None
            if overwrite:
                overwrite.active = 0
                session.add(overwrite)
                session.commit()
            user_obj.card_number = int(num)
        session.add(user_obj)
        session.commit()
        session.refresh(user_obj)
        return user_obj

    @classmethod
    def _log_menu(cls, session: Session, user_obj: User | None):
        log = None
        if user_obj:
            if len(user_obj.use) > 0:
                log = user_obj.use[-1]
        if not log:
            return None
        if log.canceled == 1 or log.timestamp.date() == date.today():
            return None
        log.menu = 1 if log.menu == 0 else 0
        session.add(log)
        session.commit()
        session.refresh(log)
        return log


class TagMethod:
    @classmethod
    def _tag_user(cls, session: Session, data: str):
        nocard = True
        if re.search("[A-Z]", data):
            nocard = False
        user_obj = Search._exact(session=session, data=data)
        if not user_obj:
            return None
        if user_obj.use:
            if not user_obj.use[-1].canceled:
                return user_obj, "Exists"
        log_obj = CreateNew._log(session=session, user_obj=user_obj, no_card=nocard)
        if not log_obj:
            return None
        session.refresh(user_obj)
        return user_obj, "New"

    @classmethod
    def _cancel(cls, session: Session, data: str):
        log_obj = None
        user_obj = Search._exact(session=session, data=data)
        if not user_obj:
            return None
        if user_obj.use:
            if not user_obj.use[-1].canceled:
                log_obj = user_obj.use[-1]
        if log_obj:
            log_obj.canceled = 1

            session.add(log_obj)
            session.commit()
            session.refresh(user_obj)
            return user_obj

    @classmethod
    def _menu(cls, session: Session, data: str):
        user_obj = Search._exact(session=session, data=data)
        log_obj = None
        if not user_obj:
            return None
        if user_obj.use:
            if not user_obj.use[-1].canceled:
                log_obj = user_obj.use[-1]
        if log_obj:
            log_obj.menu = 1 if log_obj.menu == 0 else 0
            session.add(log_obj)
            session.commit()
            session.refresh(user_obj)
            return user_obj
