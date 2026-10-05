ALLOWED_COMPONENTS = {
    "Sidebar",
    "TaskList",
    "Search",
    "Filters",
    "FocusPanel",
    "QuickAdd",
}

ALLOWED_FOCUS_ITEMS = {
    "quickAdd",
    "today",
    "priority",
    "markDone",
    "search",
}

ALLOWED_CONSTRAINTS = {"allowCustomHtml"}


def validate_layout(layout: dict) -> tuple[bool, list[str]]:
    errors = []

    if not isinstance(layout, dict):
        return False, ["Layout must be an object"]

    components = layout.get("components")
    focus_items = layout.get("focusItems", [])
    constraints = layout.get("constraints", {})

    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty array")
    else:
        unknown = [x for x in components if x not in ALLOWED_COMPONENTS]
        if unknown:
            errors.append(f"Unknown components: {unknown}")

    if not isinstance(focus_items, list):
        errors.append("focusItems must be an array")
    else:
        unknown = [x for x in focus_items if x not in ALLOWED_FOCUS_ITEMS]
        if unknown:
            errors.append(f"Unknown focus items: {unknown}")

    if not isinstance(constraints, dict):
        errors.append("constraints must be an object")
    elif constraints.get("allowCustomHtml", False) is not False:
        errors.append("Custom HTML is forbidden")

    if len(components) > 8:
        errors.append("Too many components")

    if len(focus_items) > 6:
        errors.append("Too many focus items")

    return len(errors) == 0, errors
