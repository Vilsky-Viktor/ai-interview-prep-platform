def company_block(description: str) -> str:
    if not description.strip():
        return ""

    return f"Company description:\n{description}\n\n"


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
