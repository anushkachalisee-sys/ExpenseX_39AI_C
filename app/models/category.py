from app.database import Database


class CategoryModel:
    @staticmethod
    def get_all(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM categories
                WHERE user_id = %s OR user_id IS NULL
                ORDER BY type, name
                """,
                (user_id,),
            )
        finally:
            db.close()

    @staticmethod
    def get_all_with_counts(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT c.*, COUNT(t.id) AS txn_count
                FROM categories c
                LEFT JOIN transactions t
                  ON t.category_id = c.id AND t.user_id = %s
                WHERE c.user_id = %s OR c.user_id IS NULL
                GROUP BY c.id
                ORDER BY c.type, c.name
                """,
                (user_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def get_by_type(user_id, cat_type):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM categories
                WHERE (user_id = %s OR user_id IS NULL) AND type = %s
                ORDER BY name
                """,
                (user_id, cat_type),
            )
        finally:
            db.close()

    @staticmethod
    def find_by_id(cat_id, user_id):
        db = Database()
        try:
            return db.fetch_one(
                """
                SELECT * FROM categories
                WHERE id = %s AND (user_id = %s OR user_id IS NULL)
                """,
                (cat_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def duplicate_exists(user_id, name, cat_type, exclude_id=None):
        db = Database()
        try:
            if exclude_id:
                row = db.fetch_one(
                    """
                    SELECT id FROM categories
                    WHERE (user_id = %s OR user_id IS NULL)
                    AND name = %s AND type = %s AND id != %s
                    """,
                    (user_id, name, cat_type, exclude_id),
                )
            else:
                row = db.fetch_one(
                    """
                    SELECT id FROM categories
                    WHERE user_id = %s AND name = %s AND type = %s
                    """,
                    (user_id, name, cat_type),
                )
            return row is not None
        finally:
            db.close()

    @staticmethod
    def create(user_id, name, cat_type):
        db = Database()
        try:
            return db.execute(
                """
                INSERT INTO categories (user_id, name, type)
                VALUES (%s, %s, %s)
                """,
                (user_id, name, cat_type),
            )
        finally:
            db.close()

    @staticmethod
    def copy_global_to_user(user_id):
        db = Database()
        try:
            globals_ = db.fetch_all(
                "SELECT name, type FROM categories WHERE user_id IS NULL"
            )
            for cat in globals_:
                exists = db.fetch_one(
                    """
                    SELECT id FROM categories
                    WHERE user_id = %s AND name = %s AND type = %s
                    """,
                    (user_id, cat["name"], cat["type"]),
                )
                if not exists:
                    db.execute(
                        """
                        INSERT INTO categories (user_id, name, type)
                        VALUES (%s, %s, %s)
                        """,
                        (user_id, cat["name"], cat["type"]),
                    )
        finally:
            db.close()

    @staticmethod
    def update(cat_id, user_id, name, cat_type):
        db = Database()
        try:
            db.execute(
                """
                UPDATE categories SET name = %s, type = %s
                WHERE id = %s AND user_id = %s
                """,
                (name, cat_type, cat_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def delete(cat_id, user_id):
        db = Database()
        try:
            db.execute(
                """
                UPDATE transactions SET category_id = NULL
                WHERE category_id = %s AND user_id = %s
                """,
                (cat_id, user_id),
            )
            db.execute(
                "DELETE FROM categories WHERE id = %s AND user_id = %s",
                (cat_id, user_id),
            )
        finally:
            db.close()
