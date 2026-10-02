# Topics whose embeddings are within this cosine distance count as the same subject. Measured
# with text-embedding-3-small at 256 dimensions: the same subject in other words lands at
# 0.25-0.35, related but different subjects (bookkeeping vs financial statements) at 0.39-0.57.
MAX_TOPIC_DISTANCE = 0.35
# A question is proven, and can be reused, once answered this many times without a flag.
MIN_REUSE_ANSWERS = 5
MAX_REUSE_COUNT = 100
MAX_EMBEDDING_BATCH = 100
