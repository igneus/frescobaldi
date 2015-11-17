import ly.music.items
import documentinfo

from fial import FIAL

class Score(object):
    """
    encapsulates a score, provides functionality important
    for In adiutorium project tasks
    """

    def __init__(self, lyscore):
        self._lyscore = lyscore

        self.headers = {}

        header = self._lyscore.find_child(ly.music.items.Header)
        if header:
            for h in header.find_children(ly.music.items.Assignment):
                hkey = unicode(h.name())
                hval = h.value().plaintext()
                self.headers[hkey] = hval

    def has_id(self):
        return self.headers.get('id') is not None

    def has_fial(self):
        return self.headers.get('fial') is not None

    def fial(self):
        f = self.headers.get('fial')
        return f and FIAL(f)

    def lyscore(self):
        return self._lyscore

    def start(self):
        """ position of the score start in it's file """
        return self._lyscore.tokens[0].start

    def end(self):
        """ position of the score end in it's file """
        return self._lyscore.tokens[-1].end

def score_under_cursor(cursor):
    """ Return score under cursor. """
    node = documentinfo.music(cursor.document()).node(cursor.position())
    if not (node and node.end_position() >= cursor.selectionEnd()):
        return None


    if isinstance(node, ly.music.items.Score):
        return Score(node)

    for a in node.ancestors():
        if isinstance(a, ly.music.items.Score):
            return Score(a)

    return None
