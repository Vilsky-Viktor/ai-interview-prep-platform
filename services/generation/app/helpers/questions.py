def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def merge_buckets(buckets: list[list[str]], limit: int) -> list[str]:
    """Round-robin across subtopic buckets, dropping duplicates, up to `limit`."""
    seen = set()
    merged: list[str] = []
    pos = [0] * len(buckets)
    progressed = True

    while len(merged) < limit and progressed:
        progressed = False

        for bi, bucket in enumerate(buckets):
            while pos[bi] < len(bucket):
                question = bucket[pos[bi]].strip()
                pos[bi] += 1
                key = normalize(question)

                if question and key not in seen:
                    seen.add(key)
                    merged.append(question)
                    progressed = True

                    break

            if len(merged) >= limit:
                break

    return merged


def clean_distractors(distractors: list[str], correct: str) -> list[str]:
    """Strip, dedupe (case-insensitive), and drop anything equal to the correct option."""
    seen = {normalize(correct)}
    cleaned: list[str] = []

    for distractor in distractors:
        distractor = distractor.strip()
        key = normalize(distractor)

        if distractor and key not in seen:
            seen.add(key)
            cleaned.append(distractor)

    return cleaned
