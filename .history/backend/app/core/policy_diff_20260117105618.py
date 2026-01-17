import difflib

def diff_policies(old_text: str, new_text: str):
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="old_policy",
        tofile="new_policy",
        lineterm=""
    )

    return list(diff)
