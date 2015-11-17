"""
Custom functionality to make workflows of the 'In adiutorium' project
more pleasant and convenient.
"""

PROJECT_DIR = 'In-adiutorium'

# It's not that much general to detect project root by directory
# name, but for my purposes it's just OK.

def is_in_adiutorium_file(path):
    return PROJECT_DIR in path

def in_adiutorium_root(path):
    parts = path.split('/')
    try:
        i = parts.index(PROJECT_DIR)
        return '/'.join(parts[:i+1])
    except ValueError:
        return None
