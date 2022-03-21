import re


def to_dir(original_name: str) -> str:
    new_name = re.sub(r'[:!\\*"<>?/|	]*', "", original_name).strip()
    if len(new_name) > 95: new_name = new_name[:95]
    new_name = new_name.strip()
    return new_name