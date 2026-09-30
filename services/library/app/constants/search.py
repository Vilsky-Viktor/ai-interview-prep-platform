SEARCH_LANGUAGE = "english"
TOPIC_SEARCH_EXPRESSION = f"to_tsvector('{SEARCH_LANGUAGE}', title || ' ' || subtopics::text)"
