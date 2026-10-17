# Tags the examples of questions written before generation gave each its language, and re-tags
# "text" ones that are in a notation after all.
CODE_LANGUAGES_PROMPT = """Each numbered item below is the example shown with an interview \
question. For each, give the notation it is written in, so the site can color it. One that \
shows several files gets the notation most of it is written in. A table's rows, a formula in \
plain symbols or plain prose is "text".

{examples}"""
