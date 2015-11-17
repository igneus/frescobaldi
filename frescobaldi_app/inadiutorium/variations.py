"""
In the 'In adiutorium' project there are two types of files
in the directory structure:
"development" and "production" files. A production file usually
has a matching development file.

This module understands the conventions involved.
"""

from . import is_in_adiutorium_file


"""
Predicates
"""

def is_variations_file(path):
    """ Is the given path a development file? """
    return is_in_adiutorium_file(path) and '/variationes/' in path

"""
Finders.
It is not guaranteed that the returned paths actually exist.
"""

def main_file(path):
    """ For given development file finds production file. """
    return path.replace('variationes/', '')

def variations_file(path):
    """ For given production file finds development file. """
    return path.replace('In-adiutorium/', 'In-adiutorium/variationes/')
