from app.database import Database
#Admin models completed
#checked fro admin method no errors validation complete
#checking
class AdminModel:
    PER_PAGE = 20

    @staticmethod
    def get_all_users(page=1, per_page=None):
        db = Database()
        try:
            per_page = per_page or AdminModel.PER_PAGE
            offset = (max(page, 1) - 1) * per_page
            return db.fetch_all(
                """
                SELECT u.*,
                       (SELECT COUNT(*) FROM transactions t WHERE t.user_id = u.id) AS txn_count
                FROM users u
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (per_page, offset),
            )
        finally:
            db.close()

    @staticmethod
    def count_users():
        db = Database()
        try:
            row = db.fetch_one("SELECT COUNT(*) AS cnt FROM users")
            return int(row["cnt"]) if row else 0
        finally:
            db.close()

    @staticmethod
    def get_user_by_id(user_id):
        db = Database()
        try:
            return db.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        finally:
            db.close()

    @staticmethod
    def toggle_user_status(user_id):
        db = Database()
        try:
            user = db.fetch_one(
                "SELECT is_active, name FROM users WHERE id = %s", (user_id,)
            )
            if not user:
                return None, None
            new_val = 0 if user.get("is_active", 1) else 1
            db.execute(
                "UPDATE users SET is_active = %s WHERE id = %s",
                (new_val, user_id),
            )
            status = "active" if new_val else "inactive"
            return new_val, f"{user['name']} → {status}"
        finally:
            db.close()

    @staticmethod
    def change_user_role(user_id, role):
        db = Database()
        try:
            user = db.fetch_one("SELECT name FROM users WHERE id = %s", (user_id,))
            if role not in ("user", "admin"):
                role = "user"
            db.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id),
            )
            if user:
                return f"{user['name']} → {role}"
            return None
        finally:
            db.close()

    @staticmethod
    def count_admins():
        db = Database()
        try:
            row = db.fetch_one(
                "SELECT COUNT(*) AS cnt FROM users WHERE role = 'admin'"
            )
            return int(row["cnt"]) if row else 0
        finally:
            db.close()

    @staticmethod
    def delete_user(user_id):
        db = Database()
        try:
            user = db.fetch_one(
                "SELECT id, name, email, role FROM users WHERE id = %s",
                (user_id,),
            )
            if not user:
                return False, "not_found"
            if user.get("role") == "admin" and AdminModel.count_admins() <= 1:
                return False, "last_admin"
            db.execute("DELETE FROM users WHERE id = %s", (user_id,))
            if db.cursor.rowcount < 1:
                return False, "not_found"
            return True, user.get("name") or user.get("email") or str(user_id)
        finally:
            db.close()

    @staticmethod
    def get_user_transactions(user_id, limit=50):
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
    def get_all_transactions(month=None, user_id=None, txn_type=None, page=1, per_page=30):
        db = Database()
        try:
            offset = (max(page, 1) - 1) * per_page
            query = """
                SELECT t.*, c.name AS category_name, u.name AS user_name, u.email
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                JOIN users u ON t.user_id = u.id
                WHERE 1=1
            """
            params = []
            if month:
                query += " AND DATE_FORMAT(t.date, '%%Y-%%m') = %s"
                params.append(month)
            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)
            if txn_type:
                query += " AND t.type = %s"
                params.append(txn_type)
            query += " ORDER BY t.date DESC, t.id DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            return db.fetch_all(query, tuple(params))
        finally:
            db.close()

    @staticmethod
    def count_all_transactions(month=None, user_id=None, txn_type=None):
        db = Database()
        try:
            query = "SELECT COUNT(*) AS cnt FROM transactions t WHERE 1=1"
            params = []
            if month:
                query += " AND DATE_FORMAT(t.date, '%%Y-%%m') = %s"
                params.append(month)
            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)
            if txn_type:
                query += " AND t.type = %s"
                params.append(txn_type)
            row = db.fetch_one(query, tuple(params))
            return int(row["cnt"]) if row else 0
        finally:
            db.close()

    @staticmethod
    def get_all_transactions_export(month=None, user_id=None, txn_type=None):
        db = Database()
        try:
            query = """
                SELECT t.*, c.name AS category_name, u.name AS user_name, u.email
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                JOIN users u ON t.user_id = u.id
                WHERE 1=1
            """
            params = []
            if month:
                query += " AND DATE_FORMAT(t.date, '%%Y-%%m') = %s"
                params.append(month)
            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)
            if txn_type:
                query += " AND t.type = %s"
                params.append(txn_type)
            query += " ORDER BY t.date DESC, t.id DESC"
            return db.fetch_all(query, tuple(params))
        finally:
            db.close()

    @staticmethod
    def get_platform_stats():
        db = Database()
        try:
            users = db.fetch_one("SELECT COUNT(*) AS total FROM users")
            active = db.fetch_one(
                "SELECT COUNT(*) AS total FROM users WHERE is_active = 1"
            )
            txns = db.fetch_one("SELECT COUNT(*) AS total FROM transactions")
            volume = db.fetch_one(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions"
            )
            return {
                "total_users": int(users["total"]) if users else 0,
                "active_users": int(active["total"]) if active else 0,
                "total_transactions": int(txns["total"]) if txns else 0,
                "volume_tracked": float(volume["total"]) if volume else 0.0,
            }
        finally:
            db.close()

    @staticmethod
    def get_activity_feed(limit=15):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM activity_log
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
        finally:
            db.close()

    @staticmethod
    def get_signups_by_month(months=6):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month,
                       COUNT(*) AS count
                FROM users
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
                GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
                ORDER BY month
                """,
                (months,),
            )
        finally:
            db.close()

    @staticmethod
    def get_top_active_users(limit=5):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT u.id, u.name, u.email, COUNT(t.id) AS txn_count,
                       u.created_at
                FROM users u
                LEFT JOIN transactions t ON t.user_id = u.id
                GROUP BY u.id
                ORDER BY txn_count DESC
                LIMIT %s
                """,
                (limit,),
            )
        finally:
            db.close()

    @staticmethod
    def get_global_categories():
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM categories WHERE user_id IS NULL
                ORDER BY type, name
                """
            )
        finally:
            db.close()

    @staticmethod
    def create_global_category(name, type_):
        db = Database()
        try:
            return db.execute(
                """
                INSERT INTO categories (user_id, name, type)
                VALUES (NULL, %s, %s)
                """,
                (name, type_),
            )
        finally:
            db.close()

    @staticmethod
    def delete_global_category(cat_id):
        db = Database()
        try:
            db.execute(
                "UPDATE transactions SET category_id = NULL WHERE category_id = %s",
                (cat_id,),
            )
            db.execute(
                "DELETE FROM categories WHERE id = %s AND user_id IS NULL",
                (cat_id,),
            )
        finally:
            db.close()

    @staticmethod
    def global_category_exists(name, type_):
        db = Database()
        try:
            row = db.fetch_one(
                """
                SELECT id FROM categories
                WHERE user_id IS NULL AND name = %s AND type = %s
                """,
                (name, type_),
            )
            return row is not None
        finally:
            db.close()
