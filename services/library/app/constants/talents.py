# The templates for similar roles a company's test is matched with, to suggest their talents.
SIMILAR_TEMPLATES = 5
# The same role, not just a shared skill: two topics are alike within this distance (stricter
# than the question bank's MAX_TOPIC_DISTANCE), and at least this share of the test's topics and
# of the template's topics must each have an alike topic on the other side. So a frontend
# template sharing "testing" or "Git" with a backend test doesn't match it.
SIMILAR_TOPIC_DISTANCE = 0.25
MIN_SHARED_TOPICS = 0.6
