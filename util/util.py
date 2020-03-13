import re

def remove_prefix(text, prefix):
    return re.sub(r'^%s'%prefix, '', text)

def remove_suffix(text:str, suffix):
    return re.sub(r'%s$'%suffix, '', text)
