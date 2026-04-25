from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError 

from models import (
    db,
    Workout,
    Exercise,
    WorkoutExercise,
    WorkoutSchema,
    ExerciseSchema,
    WorkoutExerciseSchema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
we_schema = WorkoutExerciseSchema()
wes_schema = WorkoutExerciseSchema(many=True)


@app.route('/')
def index():
    return 'Workout API'


@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.get_json() or {}
    try:
        valid = workout_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    workout = Workout(**valid)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    db.session.delete(workout)  # cascades to WorkoutExercises
    db.session.commit()
    return "", 204


@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json() or {}
    try:
        valid = exercise_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = Exercise(**valid)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({"error": "Exercise not found"}), 404
    db.session.delete(exercise)  # cascades to WorkoutExercises
    db.session.commit()
    return "", 204


@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)
    if not workout or not exercise:
        return jsonify({"error": "Workout or Exercise not found"}), 404

    payload = request.get_json() or {}
    payload["workout_id"] = workout_id
    payload["exercise_id"] = exercise_id

    try:
        valid = we_schema.load(payload)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    we = WorkoutExercise(**valid)
    db.session.add(we)
    db.session.commit()
    return jsonify(we_schema.dump(we)), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)