import re


def remove_prefix(text, prefix) -> str:
    return re.sub(r'^%s' % prefix, '', text)


def remove_suffix(text: str, suffix) -> str:
    return re.sub(r'%s$' % suffix, '', text)
