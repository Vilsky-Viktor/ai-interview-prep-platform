import math

from app.config.settings import settings
from app.constants.generation import ANSWER_BATCH_SIZE


def track_progress(progress: dict, chunk: dict) -> bool:
    """Update {"done", "total"} from one graph stream chunk. Returns True if it changed."""
    changed = False

    for node, update in chunk.items():
        if node == "human_review" and update["approved"]:
            topics = update["topics"]
            question_steps = sum(len(topic["subtopics"]) or 1 for topic in topics)
            answer_steps = len(topics) * math.ceil(
                settings.questions_per_topic / ANSWER_BATCH_SIZE
            )
            progress.update(
                done=0, total=question_steps + answer_steps, question_steps=question_steps
            )
            changed = True
        elif node == "merge_questions":
            answer_steps = sum(
                math.ceil(len(questions) / ANSWER_BATCH_SIZE)
                for questions in update["topic_questions"]
            )
            progress["total"] = progress["question_steps"] + answer_steps
            changed = True
        elif node in ("generate_questions", "generate_answers"):
            progress["done"] += 1
            changed = True

    return changed
