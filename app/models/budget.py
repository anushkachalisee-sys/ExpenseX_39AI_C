from app.database import Database
#Budget Model completed

class BudgetModel:
    ACHIEVEMENTS = [
        {
            "title": "Income Milestone",
            "description": "Earned NPR 10,000+ in total income",
            "icon": "trending-up",
            "check": lambda totals, streak: totals["income"] >= 10000,
        },
        {
            "title": "Expense Tracker",
            "description": "Tracked NPR 500+ in expenses",
            "icon": "bar-chart-2",
            "check": lambda totals, streak: totals["expense"] >= 500,
        },
        {
            "title": "7-Day Streak",
            "description": "Logged in 7 days in a row",
            "icon": "zap",
            "check": lambda totals, streak: streak >= 7,
        },
        {
            "title": "30-Day Streak",
            "description": "Logged in 30 days in a row",
            "icon": "award",
            "check": lambda totals, streak: streak >= 30,
        },
        {
            "title": "Saver",
            "description": "Total income exceeds total expenses",
            "icon": "trending-up",
            "check": lambda totals, streak: totals["income"] > totals["expense"],
        },
        {
            "title": "Goal Achiever",
            "description": "Completed a savings goal",
            "icon": "flag",
            "check": None,
        },
    ]

    @staticmethod
    def get_budget(user_id):
        db = Database()
        try:
            return db.fetch_one(
                "SELECT * FROM budgets WHERE user_id = %s", (user_id,)
            )
        finally:
            db.close()

    @staticmethod
    def upsert_budget(user_id, monthly_limit, daily_limit):
        db = Database()
        try:
            existing = db.fetch_one(
                "SELECT id FROM budgets WHERE user_id = %s", (user_id,)
            )
            if existing:
                db.execute(
                    """
                    UPDATE budgets SET monthly_limit = %s, daily_limit = %s
                    WHERE user_id = %s
                    """,
                    (monthly_limit, daily_limit, user_id),
                )
            else:
                db.execute(
                    """
                    INSERT INTO budgets (user_id, monthly_limit, daily_limit)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, monthly_limit, daily_limit),
                )
        finally:
            db.close()

    @staticmethod
    def get_goals(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM goals
                WHERE user_id = %s
                ORDER BY completed ASC, deadline ASC, id DESC
                """,
                (user_id,),
            )
        finally:
            db.close()

    @staticmethod
    def find_goal(goal_id, user_id):
        db = Database()
        try:
            return db.fetch_one(
                "SELECT * FROM goals WHERE id = %s AND user_id = %s",
                (goal_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def add_goal(user_id, title, target_amount, deadline=None):
        db = Database()
        try:
            return db.execute(
                """
                INSERT INTO goals (user_id, title, target_amount, deadline)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, title, target_amount, deadline or None),
            )
        finally:
            db.close()

    @staticmethod
    def update_goal(goal_id, user_id, title, target_amount, current_amount, deadline=None):
        db = Database()
        try:
            completed = 1 if float(current_amount) >= float(target_amount) else 0
            db.execute(
                """
                UPDATE goals
                SET title = %s, target_amount = %s, current_amount = %s,
                    deadline = %s, completed = %s
                WHERE id = %s AND user_id = %s
                """,
                (
                    title,
                    target_amount,
                    current_amount,
                    deadline or None,
                    completed,
                    goal_id,
                    user_id,
                ),
            )
            return completed
        finally:
            db.close()

    @staticmethod
    def delete_goal(goal_id, user_id):
        db = Database()
        try:
            db.execute(
                "DELETE FROM goals WHERE id = %s AND user_id = %s",
                (goal_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def mark_goal_completed(goal_id, user_id):
        db = Database()
        try:
            db.execute(
                "UPDATE goals SET completed = 1 WHERE id = %s AND user_id = %s",
                (goal_id, user_id),
            )
        finally:
            db.close()

    @staticmethod
    def get_achievements(user_id):
        db = Database()
        try:
            return db.fetch_all(
                """
                SELECT * FROM achievements
                WHERE user_id = %s
                ORDER BY unlocked_at DESC
                """,
                (user_id,),
            )
        finally:
            db.close()

    @staticmethod
    def has_achievement(user_id, title):
        db = Database()
        try:
            row = db.fetch_one(
                "SELECT id FROM achievements WHERE user_id = %s AND title = %s",
                (user_id, title),
            )
            return row is not None
        finally:
            db.close()

    @staticmethod
    def unlock_achievement(user_id, title, description, icon="award"):
        db = Database()
        try:
            if BudgetModel.has_achievement(user_id, title):
                return False
            db.execute(
                """
                INSERT INTO achievements (user_id, title, description, icon)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, title, description, icon),
            )
            return True
        finally:
            db.close()

    @staticmethod
    def check_and_unlock_achievements(user_id, totals, streak):
        unlocked = []
        for ach in BudgetModel.ACHIEVEMENTS:
            if ach["check"] is None:
                continue
            if ach["check"](totals, streak):
                if BudgetModel.unlock_achievement(
                    user_id, ach["title"], ach["description"], ach["icon"]
                ):
                    unlocked.append(ach["title"])
        return unlocked

    @staticmethod
    def unlock_goal_achievement(user_id):
        ach = BudgetModel.ACHIEVEMENTS[5]
        if BudgetModel.unlock_achievement(
            user_id, ach["title"], ach["description"], ach["icon"]
        ):
            return ach["title"]
        return None
