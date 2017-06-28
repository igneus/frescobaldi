import os, re

from . import in_adiutorium_root

FIAL_RE = re.compile(r'^(?P<prefix>fial://)?(?P<path>.+?)#(?P<id>.+?)(\?(?P<params>.*))?$')

class FIAL:
    """
    parsed reference to a score in the In adiutorium project structure
    """

    def __init__(self, text):
        self.source = text

        m = FIAL_RE.match(text)
        self.path = m.group('path')
        self.id = m.group('id')

        self.params = {}
        if m.group('params'):
            for p in m.group('params').split('&'):
                try:
                    par, val = p.split('=', 1)
                except ValueError:
                    self.params[p] = True
                else:
                    self.params[par] = val

    def expand_path(self, some_path):
        """
        accepts path of project root or any project file,
        returns path of the referenced file
        """
        root = in_adiutorium_root(some_path)
        return os.path.join(root, self.path)
