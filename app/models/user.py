from datetime import date, timedelta
#User model completed
#checking
#working in this file
#checked
from app.auth import hash_password
from app.database import Database


class UserModel:
    @staticmethod
    def find_by_email(email):
        db = Database()
        try:
            return db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        finally:
            db.close()

    @staticmethod
    def find_by_id(user_id):
        db = Database()
        try:
            return db.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        finally:
            db.close()

    @staticmethod
    def create(name, email, password, role="user", currency="NPR"):
        db = Database()
        try:
            hashed = hash_password(password)
            user_id = db.execute(
                """
                INSERT INTO users (name, email, password, role, streak, currency, is_active)
                VALUES (%s, %s, %s, %s, 0, %s, 1)
                """,
                (name, email, hashed, role, currency),
            )
            return user_id
        finally:
            db.close()

    @staticmethod
    def update_profile(user_id, name, email, password=None, currency=None):
        db = Database()
        try:
            if password and currency is not None:
                hashed = hash_password(password)
                db.execute(
                    """
                    UPDATE users SET name = %s, email = %s, password = %s, currency = %s
                    WHERE id = %s
                    """,
                    (name, email, hashed, currency, user_id),
                )
            elif password:
                hashed = hash_password(password)
                db.execute(
                    """
                    UPDATE users SET name = %s, email = %s, password = %s
                    WHERE id = %s
                    """,
                    (name, email, hashed, user_id),
                )
            elif currency is not None:
                db.execute(
                    """
                    UPDATE users SET name = %s, email = %s, currency = %s
                    WHERE id = %s
                    """,
                    (name, email, currency, user_id),
                )
            else:
                db.execute(
                    "UPDATE users SET name = %s, email = %s WHERE id = %s",
                    (name, email, user_id),
                )
        finally:
            db.close()

    @staticmethod
    def update_currency(user_id, currency):
        db = Database()
        try:
            db.execute(
                "UPDATE users SET currency = %s WHERE id = %s",
                (currency, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def email_exists_for_other(email, user_id):
        db = Database()
        try:
            row = db.fetch_one(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (email, user_id),
            )
            return row is not None
        finally:
            db.close()

    @staticmethod
    def update_login_streak(user_id):
        db = Database()
        try:
            user = db.fetch_one(
                "SELECT streak, last_login FROM users WHERE id = %s", (user_id,)
            )
            if not user:
                return 0

            today = date.today()
            last_login = user.get("last_login")
            streak = user.get("streak") or 0

            if last_login:
                if isinstance(last_login, str):
                    last_login = date.fromisoformat(str(last_login))
                elif hasattr(last_login, "date"):
                    last_login = (
                        last_login.date()
                        if callable(getattr(last_login, "date", None))
                        else last_login
                    )

                if last_login == today:
                    new_streak = streak
                elif last_login == today - timedelta(days=1):
                    new_streak = streak + 1
                else:
                    new_streak = 1
            else:
                new_streak = 1

            db.execute(
                "UPDATE users SET streak = %s, last_login = %s WHERE id = %s",
                (new_streak, today, user_id),
            )
            return new_streak
        finally:
            db.close()

    @staticmethod
    def get_totals(user_id):
        db = Database()
        try:
            income = db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM transactions WHERE user_id = %s AND type = 'income'
                """,
                (user_id,),
            )
            expense = db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM transactions WHERE user_id = %s AND type = 'expense'
                """,
                (user_id,),
            )
            return {
                "income": float(income["total"]) if income else 0.0,
                "expense": float(expense["total"]) if expense else 0.0,
            }
        finally:
            db.close()

    @staticmethod
    def is_active_user(user):
        if user is None:
            return False
        return user.get("is_active", 1) in (1, True)
#user is check working properly validation complete
#verification by kushumlata 
#checked
