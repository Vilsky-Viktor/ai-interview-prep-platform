# Messages the services show users, by language, keyed by the English text they're raised with:
# one module per language in messages/. A message missing there is shown in English.
from importlib import import_module

from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES

TRANSLATIONS = {
    code: import_module(f"prepza_common.messages.{code}").MESSAGES
    for code in LANGUAGES
    if code != DEFAULT_LANGUAGE
}


def raised_messages(app_dir) -> set[str]:
    """Every fixed message a service raises as an HTTPException's detail, read from its code in
    `app_dir` (the service's `app` package): string literals and constants. Messages put
    together at run time (f-strings) can't be translated by their text, so they're left out.
    Services' tests check each one has a translation in every language."""
    import ast
    from pathlib import Path

    root = Path(app_dir)
    found = set()

    for path in root.rglob("*.py"):
        module = None
        name = ".".join((root.name, *path.relative_to(root).with_suffix("").parts))

        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call):
                continue

            called = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else getattr(node.func, "id", None)
            )

            if called != "HTTPException":
                continue

            detail = node.args[1] if len(node.args) > 1 else None
            detail = next((item.value for item in node.keywords if item.arg == "detail"), detail)

            if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
                found.add(detail.value)
            elif isinstance(detail, (ast.Name, ast.Attribute)):
                module = module or import_module(name)
                value = _resolve(module, detail)

                if isinstance(value, str):
                    found.add(value)

    return found


def _resolve(module, node):
    """The value a name or a dotted name in `module` refers to."""
    import ast

    if isinstance(node, ast.Name):
        return getattr(module, node.id, None)

    owner = (
        _resolve(module, node.value) if isinstance(node.value, (ast.Name, ast.Attribute)) else None
    )

    return getattr(owner, node.attr, None)
