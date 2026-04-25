# Workout App Backend (Flask + SQLAlchemy + Marshmallow)

A RESTful backend API for a workout tracking application. Personal trainers can:

- Create and list workouts.
- Create and list exercises.
- Attach exercises to workouts with reps/sets or duration.
- Retrieve workouts with their workout-exercise details.
- Retrieve exercises with their associated workout-exercises.

The backend enforces model, schema, and database-level validations to keep data clean and realistic.

---

## Tech Stack

- Python 3.8
- Flask 2.2.2
- Flask‑SQLAlchemy 3.0.3
- Flask‑Migrate 3.1.0
- Marshmallow 3.20.1
- SQLite (app.db)
- Pipenv

---

## Project Structure

backend-workout-app/
  Pipfile
  Pipfile.lock
  README.md
  server/
    app.py
    models.py
    seed.py
    migrations/
    app.db (after migrations)


# Workout App Backend – Common Commands

# ---------------------------
# 0. Clone and enter project
# ---------------------------
git clone https://github.com/rich-peeps/backend-workout-app.git
cd backend-workout-app

# ---------------------------
# 1. Create / activate env
# ---------------------------
pipenv --python 3.8
pipenv install
pipenv shell

# If needed (inside pipenv shell):
# python -m pip install Flask==2.2.2 Flask-Migrate==3.1.0 flask-sqlalchemy==3.0.3 marshmallow==3.20.1 pytest

# ---------------------------
# 2. Initialize database
# ---------------------------
cd server
export FLASK_APP=app.py
export FLASK_RUN_PORT=5555

# ---------------------------
# 3. Seed database
# ---------------------------
python seed.py

# Re-run python seed.py any time you want to clear+reset data.

# ---------------------------
# 4. Run the server
# ---------------------------
python -m flask run
# App now running at http://127.0.0.1:5555

# ---------------------------
# 5. Basic manual tests (in a NEW terminal)
# ---------------------------

# List workouts
curl http://localhost:5555/workouts

# Create a workout
curl -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-04-30",
    "duration_minutes": 60,
    "notes": "Leg day"
  }'

# List exercises
curl http://localhost:5555/exercises

# Create an exercise
curl -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Back Squat",
    "category": "strength",
    "equipment_needed": true
  }'

# Attach an exercise to a workout (e.g., workout 1, exercise 1)
curl -X POST http://localhost:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps": 8, "sets": 3}'