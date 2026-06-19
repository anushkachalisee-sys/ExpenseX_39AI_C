from datetime import date, timedelta
#Transaction Model completed
from app.database import Database
#check for transition
#ongoing
#done
#no error validation complete
#working in this file
#checked
class TransactionModel:
    PER_PAGE = 20

    @staticmethod
    def _current_month():
        return date.today().strftime("%Y-%m")

    @staticmethod
    def count_by_type(user_id, txn_type, month=None, category_id=None):
        db = Database()
        try:
            month = month or TransactionModel._current_month()
            query = """
                SELECT COUNT(*) AS cnt FROM transactions t
                WHERE t.user_id = %s AND t.type = %s
                AND DATE_FORMAT(t.date, '%%Y-%%m') = %s
            """
            params = [user_id, txn_type, month]
            if category_id:
                query += " AND t.category_id = %s"
                params.append(category_id)
            row = db.fetch_one(query, tuple(params))
            return int(row["cnt"]) if row else 0
        finally:
            db.close()

    @staticmethod
    def list_by_type(user_id, txn_type, month=None, category_id=None, page=1, per_page=None):
        db = Database()
        try:
            per_page = per_page or TransactionModel.PER_PAGE
            month = month or TransactionModel._current_month()
            offset = (max(page, 1) - 1) * per_page
            query = """
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = %s
                AND DATE_FORMAT(t.date, '%%Y-%%m') = %s
            """
            params = [user_id, txn_type, month]
            if category_id:
                query += " AND t.category_id = %s"
                params.append(category_id)
            query += " ORDER BY t.date DESC, t.id DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            return db.fetch_all(query, tuple(params))
        finally:
            db.close()

    @staticmethod
    def find_by_id(txn_id, user_id):
        db = Database()
        try:
            return db.fetch_one(
                """
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = %s AND t.user_id = %s
                """,
                (txn_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def create(
        user_id,
        category_id,
        txn_type,
        amount,
        description,
        txn_date,
        notes=None,
        is_recurring=0,
        recurrence=None,
    ):
        db = Database()
        try:
            return db.execute(
                """
                INSERT INTO transactions
                (user_id, category_id, type, amount, description, date,
                 notes, is_recurring, recurrence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    category_id or None,
                    txn_type,
                    amount,
                    description,
                    txn_date,
                    notes,
                    is_recurring,
                    recurrence,
                ),
            )
        finally:
            db.close()

    @staticmethod
    def update(
        txn_id,
        user_id,
        category_id,
        txn_type,
        amount,
        description,
        txn_date,
        notes=None,
        is_recurring=0,
        recurrence=None,
    ):
        db = Database()
        try:
            db.execute(
                """
                UPDATE transactions
                SET category_id = %s, type = %s, amount = %s,
                    description = %s, date = %s, notes = %s,
                    is_recurring = %s, recurrence = %s
                WHERE id = %s AND user_id = %s
                """,
                (
                    category_id or None,
                    txn_type,
                    amount,
                    description,
                    txn_date,
                    notes,
                    is_recurring,
                    recurrence,
                    txn_id,
                    user_id,
                ),
            )
        finally:
            db.close()

    @staticmethod
    def delete(txn_id, user_id):
        db = Database()
        try:
            db.execute(
                "DELETE FROM transactions WHERE id = %s AND user_id = %s",
                (txn_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def _search_clause():
        return """
            (
                t.description LIKE %s
                OR t.notes LIKE %s
                OR COALESCE(c.name, '') LIKE %s
                OR t.type LIKE %s
                OR CAST(t.amount AS CHAR) LIKE %s
                OR DATE_FORMAT(t.date, '%%Y-%%m-%%d') LIKE %s
            )
        """

    @staticmethod
    def count_search(user_id, query):
        db = Database()
        try:
            pattern = f"%{query}%"
            params = (user_id, pattern, pattern, pattern, pattern, pattern, pattern)
            row = db.fetch_one(
                f"""
                SELECT COUNT(*) AS cnt
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND {TransactionModel._search_clause()}
                """,
                params,
            )
            return int(row["cnt"]) if row else 0
        finally:
            db.close()

    @staticmethod
    def search(user_id, query, page=1, per_page=None):
        db = Database()
        try:
            per_page = per_page or TransactionModel.PER_PAGE
            offset = (max(page, 1) - 1) * per_page
            pattern = f"%{query}%"
            params = [
                user_id,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                pattern,
                per_page,
                offset,
            ]
            return db.fetch_all(
                f"""
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND {TransactionModel._search_clause()}
                ORDER BY t.date DESC, t.id DESC
                LIMIT %s OFFSET %s
                """,
                tuple(params),
            )
        finally:
            db.close()

    @staticmethod
    def get_monthly_summary(user_id, month=None):
        db = Database()
        try:
            month = month or TransactionModel._current_month()
            income = db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE user_id = %s AND type = 'income'
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
                """,
                (user_id, month),
            )
            expense = db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE user_id = %s AND type = 'expense'
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
                """,
                (user_id, month),
            )
            return {
                "income": float(income["total"]) if income else 0.0,
                "expense": float(expense["total"]) if expense else 0.0,
            }
        finally:
            db.close()

    @staticmethod
    def get_prev_month_summary(user_id):
        today = date.today()
        first = date(today.year, today.month, 1)
        prev_end = first - timedelta(days=1)
        prev_month = prev_end.strftime("%Y-%m")
        return TransactionModel.get_monthly_summary(user_id, prev_month)

    @staticmethod
    def get_monthly_series(user_id, txn_type, months=6):
        db = Database()
        try:
            rows = db.fetch_all(
                """
                SELECT DATE_FORMAT(date, '%%Y-%%m') AS month,
                       COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE user_id = %s AND type = %s
                AND date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
                GROUP BY DATE_FORMAT(date, '%%Y-%%m')
                ORDER BY month
                """,
                (user_id, txn_type, months),
            )
            data_map = {r["month"]: float(r["total"]) for r in rows}
            result = []
            today = date.today()
            for i in range(months - 1, -1, -1):
                d = date(today.year, today.month, 1) - timedelta(days=i * 28)
                key = d.strftime("%Y-%m")
                y, m = today.year, today.month - i
                while m <= 0:
                    m += 12
                    y -= 1
                key = f"{y:04d}-{m:02d}"
                result.append(data_map.get(key, 0.0))
            labels = []
            for i in range(months - 1, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                labels.append(f"{y:04d}-{m:02d}")
            values = [data_map.get(lbl, 0.0) for lbl in labels]
            return values
        finally:
            db.close()

    @staticmethod
    def get_today_expense(user_id):
        db = Database()
        try:
            today = date.today().isoformat()
            row = db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE user_id = %s AND type = 'expense' AND date = %s
                """,
                (user_id, today),
            )
            return float(row["total"]) if row else 0.0
        finally:
            db.close()

    @staticmethod
    def get_recent(user_id, limit=5):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s
                ORDER BY t.date DESC, t.id DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
        finally:
            db.close()

    @staticmethod
    def get_all_for_export(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s
                ORDER BY t.date DESC, t.id DESC
                """,
                (user_id,),
            )
        finally:
            db.close()

    @staticmethod
    def get_expense_by_category(user_id, month=None):
        db = Database()
        try:
            month = month or TransactionModel._current_month()
            return db.fetch_all(
                """
                SELECT COALESCE(c.name, 'Uncategorized') AS category_name,
                       COALESCE(SUM(t.amount), 0) AS total
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'expense'
                AND DATE_FORMAT(t.date, '%%Y-%%m') = %s
                GROUP BY c.name
                ORDER BY total DESC
                """,
                (user_id, month),
            )
        finally:
            db.close()

    @staticmethod
    def get_daily_expenses(user_id, month=None):
        db = Database()
        try:
            month = month or TransactionModel._current_month()
            return db.fetch_all(
                """
                SELECT DATE_FORMAT(date, '%%Y-%%m-%%d') AS day,
                       COALESCE(SUM(amount), 0) AS total
                FROM transactions
                WHERE user_id = %s AND type = 'expense'
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
                GROUP BY date
                ORDER BY date
                """,
                (user_id, month),
            )
        finally:
            db.close()

    @staticmethod
    def get_six_month_comparison(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT DATE_FORMAT(date, '%%Y-%%m') AS month,
                       SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
                       SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
                FROM transactions
                WHERE user_id = %s
                AND date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(date, '%%Y-%%m')
                ORDER BY month
                """,
                (user_id,),
            )
        finally:
            db.close()

    @staticmethod
    def get_expense_by_category_range(user_id, start_date, end_date):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT COALESCE(c.name, 'Uncategorized') AS category_name,
                       COALESCE(SUM(t.amount), 0) AS total
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.type = 'expense'
                AND t.date BETWEEN %s AND %s
                GROUP BY c.name
                ORDER BY total DESC
                """,
                (user_id, start_date, end_date),
            )
        finally:
            db.close()

    @staticmethod
    def get_income_expense_series(user_id, start_date, end_date):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT DATE_FORMAT(date, '%%Y-%%m-%%d') AS day,
                       COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
                       COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
                FROM transactions
                WHERE user_id = %s AND date BETWEEN %s AND %s
                GROUP BY date
                ORDER BY date
                """,
                (user_id, start_date, end_date),
            )
        finally:
            db.close()

    @staticmethod
    def get_category_comparison(user_id, start_date, end_date):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT COALESCE(c.name, 'Uncategorized') AS category_name,
                       COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) AS expense,
                       COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END), 0) AS income
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = %s AND t.date BETWEEN %s AND %s
                GROUP BY c.name
                HAVING expense > 0 OR income > 0
                ORDER BY expense DESC
                LIMIT 12
                """,
                (user_id, start_date, end_date),
            )
        finally:
            db.close()

    @staticmethod
    def get_summary_for_range(user_id, start_date, end_date):
        db = Database()
        try:
            row = db.fetch_one(
                """
                SELECT
                  COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
                  COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
                FROM transactions
                WHERE user_id = %s AND date BETWEEN %s AND %s
                """,
                (user_id, start_date, end_date),
            )
            return {
                "income": float(row["income"]) if row else 0.0,
                "expense": float(row["expense"]) if row else 0.0,
            }
        finally:
            db.close()
#verification by kushumlta
