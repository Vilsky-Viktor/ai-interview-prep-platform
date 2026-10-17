import uuid

from app.constants.interviews import DEFAULT_TOPIC_QUESTIONS
from app.helpers.candidates import candidate_seconds
from app.helpers.interviews import interview_minutes

PYTHON = str(uuid.uuid4())
SQL = str(uuid.uuid4())


def a_set(python_questions: int, sql_questions: int) -> dict:
    return {
        "topics": [
            {"id": PYTHON, "title": "Python", "question_count": python_questions},
            {"id": SQL, "title": "SQL", "question_count": sql_questions},
        ]
    }


def test_the_whole_interview_counts_the_questions_each_topic_gives():
    # 4 questions from Python and 6 from SQL, at 60 seconds each.
    assert interview_minutes(a_set(20, 20), {PYTHON: 4, SQL: 6}, 60) == 10


def test_a_topic_with_fewer_questions_than_its_limit_gives_all_it_has():
    # Python has 3 of its 10 default questions; SQL gives its 5.
    assert interview_minutes(a_set(3, 20), {SQL: 5}, 60) == 8
    # Without limits, each topic gives the default or all it has.
    assert interview_minutes(a_set(30, 30), {}, 60) == 2 * DEFAULT_TOPIC_QUESTIONS


def test_extra_time_lengthens_the_whole_interview_rounded_up():
    seconds = candidate_seconds(45, 50)

    # 7 questions at 68 seconds each (45 with half again) are 476 seconds: 7.9 minutes.
    assert seconds == 68
    assert interview_minutes(a_set(3, 4), {PYTHON: 3, SQL: 4}, seconds) == 8


def test_the_whole_interview_is_unknown_until_its_questions_are():
    assert interview_minutes(None, {}, 60) is None
