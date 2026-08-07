# AI-Based Smart Cafeteria Food Recommendation System

> A rule-based intelligent agent that recommends suitable cafeteria meals using dietary preference, health goals, allergy restrictions, and previous orders.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![Status](https://img.shields.io/badge/Status-Academic%20Prototype-orange.svg)](#)

---

## Important Links

> Replace the placeholder URLs below before publishing the repository.

| Resource | Link |
|---|---|
| **▶ Simulation / Working Demo Video** | **[Watch the simulation video](https://drive.google.com/file/d/1FJISf4IzMfSmBl85p9SsyqlUlSBW1Kxe/view?usp=sharing)** |
| **📊 Presentation** | **[View the presentation](https://drive.google.com/file/d/1Ekl9DBiqa43qzCOglzwq8AeyqRQwtby4/view?usp=sharing)** |
| **📄 Assignment Report** | **[Read the project report](AI_Assignment_Smart_Cafeteria_Report_Final.pdf)** |

---

## Project Overview

The AI-Based Smart Cafeteria Food Recommendation System is a transparent, rule-based intelligent agent designed for a college cafeteria. It evaluates available menu items against a student's dietary preference, health goal, allergy profile, and previous order history, then displays the top three recommendations with their scores and explanations.

The project uses a simple weighted decision model rather than machine learning. This makes the recommendation process deterministic, explainable, lightweight, and suitable for a small predefined menu where allergy conflicts must be handled explicitly.

## Main Features

- Vegetarian and non-vegetarian dietary preference selection.
- Balanced Diet, High Protein, and Low Calorie health goals.
- Allergy filtering for Dairy, Nuts, Seafood, and Gluten.
- Persistent student order history stored locally in JSON.
- Order-history frequency bonus: +5 per previous order, capped at +20.
- Persistent allergy profiles that are pre-filled but remain editable.
- Allergy conflict acts as a safety veto and excludes unsuitable foods.
- Top-three recommendations with calories, protein, score, and reasons.
- Confirm & Order action that updates future recommendations.
- Scrollable interface with fixed Back, Recommend, and Exit controls.
- Offline operation using Python standard-library components.

## How the Agent Works

1. The student enters a Student ID.
2. The system loads the student's previous orders and saved allergy profile.
3. The student selects or updates dietary preference, health goal, and allergies.
4. The agent evaluates every item in `food_menu.json`.
5. Foods containing selected allergens are rejected.
6. Remaining foods receive weighted scores.
7. The system sorts the foods and displays the top three.
8. A confirmed order is appended to the student's history for future sessions.

## Scoring Model

| Condition | Score |
|---|---:|
| Dietary preference match | +25 |
| Health goal match | +20 |
| High nutritional rating | +15 |
| Each previous order of the item | +5 |
| Maximum order-history bonus | +20 |
| Allergy conflict | −100 / excluded |

The allergy check is applied as a hard safety constraint before normal ranking. The final score is intended to explain the recommendation, not to represent a medical or nutritional diagnosis.

## Project Structure

```text
smart-cafeteria-food-recommender/
├── app.py                  # Tkinter graphical user interface
├── recommender.py          # Rule-based agent and persistence functions
├── food_menu.json          # Predefined cafeteria menu
├── order_history.json      # Created/updated automatically after orders
├── allergy_profile.json    # Created/updated automatically after preferences
└── README.md               # Project documentation
```

`order_history.json` and `allergy_profile.json` may be created automatically when the application is first used. Keep all files in the same directory.

## Requirements

- Python 3.10 or later.
- Tkinter, normally included with standard Python installations.
- No external Python packages are required.

On Debian/Ubuntu Linux, install Tkinter if it is missing:

```bash
sudo apt install python3-tk
```

## Running the Application

```bash
python3 app.py
```

On Windows, the command may be:

```bash
python app.py
```

The current implementation uses `RecommendationEngine`, `UserProfile`, JSON-based history, and editable allergy profiles in the GUI. [file:69]

## Example Demonstration

A student profile may contain:

- Student ID: `student_001`
- Dietary preference: Vegetarian
- Health goal: Balanced Diet
- Saved allergy: Gluten
- Previous orders: Fruit Bowl four times and Tofu Stir Fry once

In this situation, Fruit Bowl receives an order-history bonus of +20, while Tofu Stir Fry receives +5. The application displays the score and the reasons for each recommendation, allowing the result to be inspected rather than presenting an unexplained answer.

## AI Agent Classification

### PEAS

- **Performance measure:** healthy nutritional fit, allergy safety, order-history relevance, and reduced decision time.
- **Environment:** student, cafeteria menu, stored profiles, and order records.
- **Actuators:** display ranked recommendations and persist confirmed orders/profile changes.
- **Sensors:** Student ID, diet preference, health goal, allergy selections, menu data, and previous orders.

### Environment

The system is deterministic and discrete. A recommendation run is static while it is being computed, but the overall system is sequential across sessions because a confirmed order changes future recommendations. It is a single-agent system with known rules and data.

## Limitations

- The menu is predefined and stored locally.
- The current system does not retrieve live stock, prices, or cafeteria availability.
- The rule weights are manually selected and are not learned from a large dataset.
- Allergy information depends on accurate user input and should not replace professional medical guidance.
- The current prototype has no cloud synchronization or multi-device account system.

## Future Enhancements

- IoT-based food freshness verification.
- Mobile application and cafeteria pre-ordering.
- Adaptive preference learning from accepted and rejected recommendations.
- Live stock, price, and availability integration.
- Administrator interface for updating the menu.

## Academic Context

This project demonstrates how an intelligent agent can perceive an environment, apply a rational decision procedure, and act according to a measurable objective. A sophisticated machine-learning model is not required for the present problem because the menu and input categories are small, structured, and explainable.

## Author

**Name:** Jose James  
**Roll Number:** 37  
**Class:** S7 CSE  
**Institution:** Viswajyothi College of Engineering and Technology, Vazhakulam
