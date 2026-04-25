from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, CheckConstraint
from sqlalchemy.orm import validates
from marshmallow import Schema, fields, validates_schema, ValidationError, validates as ma_validates
import datetime

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# ---------- MODELS ----------

class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id"),
        nullable=False
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False
    )

    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # Table-level constraint: must have either (reps & sets) OR duration_seconds
    __table_args__ = (
        CheckConstraint(
            "(reps IS NOT NULL AND sets IS NOT NULL) OR duration_seconds IS NOT NULL",
            name="ck_workoutexercise_has_reps_sets_or_duration"
        ),
    )

    def __repr__(self):
        return f"<WorkoutExercise {self.id} W{self.workout_id} E{self.exercise_id}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # One-to-many: Workout ➜ WorkoutExercise
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    # Many-to-many: Workout ↔ Exercise (viewonly, via WorkoutExercise)
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        viewonly=True,
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Workout duration must be greater than 0 minutes.")
        return value

    @validates("date")
    def validate_date(self, key, value):
        if not isinstance(value, datetime.date):
            raise ValueError("Workout date must be a date.")
        if value > datetime.date.today() + datetime.timedelta(days=365):
            raise ValueError("Workout date is too far in the future.")
        return value

    def __repr__(self):
        return f"<Workout {self.id} {self.date} {self.duration_minutes} min>"


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # One-to-many: Exercise ➜ WorkoutExercise
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    # Many-to-many: Exercise ↔ Workout (viewonly, via WorkoutExercise)
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        viewonly=True,
    )

    @validates("name")
    def validate_name_model(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name is required.")
        if len(value.strip()) < 3:
            raise ValueError("Exercise name must be at least 3 characters long.")
        return value

    @validates("category")
    def validate_category_model(self, key, value):
        if not value:
            raise ValueError("Category is required.")
        allowed = {"strength", "cardio", "mobility", "other"}
        if value.lower() not in allowed:
            raise ValueError("Category must be one of: strength, cardio, mobility, other.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id} {self.name} ({self.category})>"


# ---------- SCHEMAS ----------

class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    # Simple nested exercise for responses
    exercise = fields.Nested("ExerciseSchema", only=("id", "name", "category"), dump_only=True)

    @validates_schema
    def validate_reps_sets_or_duration(self, data, **kwargs):
        """
        Schema-level validation: must have (reps & sets) OR duration_seconds.
        """
        reps = data.get("reps")
        sets_ = data.get("sets")
        duration = data.get("duration_seconds")

        if not ((reps is not None and sets_ is not None) or (duration is not None)):
            raise ValidationError(
                "Must provide reps and sets, or duration_seconds.",
                field_name="workout_exercise"
            )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)

    @ma_validates("name")
    def validate_name_schema(self, value):
        if len(value.strip()) < 3:
            raise ValidationError("Exercise name must be at least 3 characters long.")

    @ma_validates("category")
    def validate_category_schema(self, value):
        allowed = {"strength", "cardio", "mobility", "other"}
        if value.lower() not in allowed:
            raise ValidationError("Invalid category.")
