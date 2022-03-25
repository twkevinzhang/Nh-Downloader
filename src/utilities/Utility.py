import os
import re


def to_dir(original_name: str) -> str:
    new_name = re.sub(r'[:!\\*"<>?/|	]*', "", original_name).strip()
    if len(new_name) > 95: new_name = new_name[:95]
    new_name = new_name.strip()
    return new_name


def remove_prefix(text, prefix) -> str:
    return re.sub(r'^%s' % prefix, '', text)


def remove_suffix(text: str, suffix) -> str:
    return re.sub(r'%s$' % suffix, '', text)

def isImage(path: str) -> bool:
    return os.path.isfile(path) and re.search(r'^\d+(\.jpg|png|gif)*$', path)