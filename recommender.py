

import json
import os

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "food_menu.json")
HISTORY_FILE = os.path.join(BASE_DIR, "order_history.json")
ALLERGY_FILE = os.path.join(BASE_DIR, "allergy_profile.json")

# ---------------------------------------------------------------------------
# Scoring weights (Section 4.3 of the System Specification)
# ---------------------------------------------------------------------------
SCORE_DIET_MATCH = 25
SCORE_HEALTH_GOAL_MATCH = 20
SCORE_HIGH_NUTRITION = 15
SCORE_PER_PAST_ORDER = 5      # awarded once per past occurrence of this food
SCORE_PAST_ORDER_CAP = 20     # frequency bonus cannot exceed this
SCORE_ALLERGY_CONFLICT = -100

HEALTH_GOAL_RULES = {
    "High Protein": lambda f: f["protein"] >= 20,
    "Low Calorie": lambda f: f["calories"] <= 300,
    "Balanced Diet": lambda f: f["health_rating"] >= 7,
}


def load_menu(path: str = DATA_FILE):
    """Load the predefined food dataset from JSON."""
    with open(path, "r") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Order history persistence (the "previous orders" percept)
# ---------------------------------------------------------------------------
def load_history(path: str = HISTORY_FILE) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def save_history(history: dict, path: str = HISTORY_FILE):
    with open(path, "w") as fh:
        json.dump(history, fh, indent=2)


def get_student_history(student_id: str, path: str = HISTORY_FILE):
    history = load_history(path)
    return history.get(student_id, [])


def log_order(student_id: str, food_name: str, path: str = HISTORY_FILE):
    """Actuator: persist a newly chosen/confirmed order for future sessions."""
    history = load_history(path)
    history.setdefault(student_id, []).append(food_name)
    save_history(history, path)


# ---------------------------------------------------------------------------
# Allergy profile persistence (stable attribute, still editable)
# ---------------------------------------------------------------------------
def load_allergy_profiles(path: str = ALLERGY_FILE) -> dict:
    """Load {student_id: [allergy, ...]} from disk."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def save_allergy_profiles(profiles: dict, path: str = ALLERGY_FILE):
    with open(path, "w") as fh:
        json.dump(profiles, fh, indent=2)


def get_student_allergies(student_id: str, path: str = ALLERGY_FILE):
    """Return the stored allergy list for one student (empty if none on file)."""
    profiles = load_allergy_profiles(path)
    return profiles.get(student_id, [])


def set_student_allergies(student_id: str, allergies: list, path: str = ALLERGY_FILE):
    """
    Actuator: overwrite the stored allergy profile for a student with the
    current checkbox state. Called every time preferences are submitted,
    so unchecking a stale allergy or checking a newly discovered one is
    always persisted -- the profile always reflects the latest confirmed
    state rather than growing indefinitely like order history does.
    """
    profiles = load_allergy_profiles(path)
    profiles[student_id] = list(allergies)
    save_allergy_profiles(profiles, path)


class UserProfile:
    """Represents percepts collected from the user (Section 4.1)."""

    def __init__(self, diet_preference, health_goal, allergies,
                 order_history=None):
        self.diet_preference = diet_preference
        self.health_goal = health_goal
        self.allergies = set(allergies) if allergies else {"None"}
        self.order_history = order_history or []


class RecommendationEngine:
    """
    The rational agent's decision procedure.

    Percepts  -> UserProfile (incl. order_history, allergies) + food menu
    Reasoning -> score_food()
    Action    -> recommend() returns ranked list
    """

    def __init__(self, menu=None):
        self.menu = menu if menu is not None else load_menu()

    def score_food(self, food: dict, user: UserProfile):
        score = 0
        reasons = []

        conflict = any(a != "None" and a in food["allergens"]
                        for a in user.allergies)
        if conflict:
            return SCORE_ALLERGY_CONFLICT, ["\u2716 Contains an allergen you avoid"]

        wants_veg = user.diet_preference == "Vegetarian"
        if wants_veg == food["veg"]:
            score += SCORE_DIET_MATCH
            reasons.append(f"\u2714 Matches {user.diet_preference} preference")

        rule = HEALTH_GOAL_RULES.get(user.health_goal)
        if rule and rule(food):
            score += SCORE_HEALTH_GOAL_MATCH
            reasons.append(f"\u2714 Matches {user.health_goal} goal")

        if food["health_rating"] >= 8:
            score += SCORE_HIGH_NUTRITION
            reasons.append("\u2714 High nutritional rating")

        past_orders = user.order_history.count(food["name"])
        if past_orders > 0:
            bonus = min(past_orders * SCORE_PER_PAST_ORDER, SCORE_PAST_ORDER_CAP)
            score += bonus
            times = "time" if past_orders == 1 else "times"
            reasons.append(f"\u2714 Ordered {past_orders} {times} before (+{bonus})")

        return score, reasons

    def recommend(self, user: UserProfile, top_n: int = 3):
        scored = []
        for food in self.menu:
            score, reasons = self.score_food(food, user)
            if score > 0:
                scored.append({"food": food, "score": score, "reasons": reasons})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_n]


if __name__ == "__main__":
    engine = RecommendationEngine()
    student = "student_001"
    history = get_student_history(student)
    allergies = get_student_allergies(student)
    print("Loaded order history:", history)
    print("Loaded allergy profile:", allergies)

    user = UserProfile(
        diet_preference="Non-Vegetarian",
        health_goal="High Protein",
        allergies=allergies,
        order_history=history,
    )
    results = engine.recommend(user)
    for r in results:
        f = r["food"]
        print(f"{f['name']} | Score: {r['score']} | "
              f"Cal: {f['calories']} | Protein: {f['protein']}g")
        for reason in r["reasons"]:
            print("   ", reason)
