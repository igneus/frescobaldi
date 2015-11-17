from __future__ import unicode_literals

from PyQt4.QtGui import QAction, QMessageBox, QTextCursor, QTextDocument
from PyQt4.QtCore import QUrl

import app

from . import is_in_adiutorium_file
from variations import is_variations_file, main_file, variations_file
import score

def actions(cursor, menu, mainwindow):
    """
    Return a list of In adiutorium-related actions (maybe empty)
    for files at the cursor to open.
    """

    return ActionsFactory(cursor, menu, mainwindow).actions()

class ActionsFactory(object):
    def __init__(self, cursor, menu, mainwindow):
        self._cursor = cursor
        self._menu = menu
        self._mainwindow = mainwindow

        self._document = mainwindow.currentDocument()
        self._path = self._document and self._document.url().path()
        self._current_score = score.score_under_cursor(self._cursor)

    def actions(self):
        if not self._document:
            return []

        if not is_in_adiutorium_file(self._path):
            return []

        if self._current_score is None:
            return []

        actions = []

        actions.append(self._duplicate())

        if self._current_score.has_fial():
            actions.append(self._goto_source())

        if self._current_score.has_id():
            actions.append(self._goto_variations())

        return actions

    def _duplicate(self):
        a = QAction(self._menu)
        a.setText('Duplicate score')

        @a.triggered.connect
        def trigger():
            cursor = QTextCursor(self._document)
            cursor.setPosition(self._current_score.end(), QTextCursor.MoveAnchor)
            cursor.insertText('\n\n')

            copy_cursor = QTextCursor(self._document)
            score_end = self._current_score.end()
            # it isn't easily possible to get score start index
            # from the DOM ...
            start_token = '\\score'
            score_start_cur = self._document.find(start_token, score_end, QTextDocument.FindBackward)
            score_start = score_start_cur.position() - len(start_token)
            copy_cursor.setPosition(score_start, QTextCursor.MoveAnchor)
            copy_cursor.setPosition(score_end, QTextCursor.KeepAnchor)

            cursor.insertFragment(copy_cursor.selection())
            self._mainwindow.setTextCursor(cursor)

        return a

    def _goto_source(self):
        a = QAction(self._menu)
        a.setText('Go to source')
        @a.triggered.connect
        def trigger():
            fial = self._current_score.fial()
            open_fial(fial, self._path, self._mainwindow)

        return a

    def _goto_variations(self):
        a = QAction(self._menu)
        file_type = ['variations', 'main'][is_variations_file(self._path)]
        a.setText('Go to {0}'.format(file_type))
        @a.triggered.connect
        def trigger():
            if is_variations_file(self._path):
                path_to_open = main_file(self._path)
            else:
                path_to_open = variations_file(self._path)

            open_score(path_to_open, self._current_score.headers['id'], self._mainwindow)

        return a

""" Helper functions """

def open_fial(fial, project_path, mainwindow):
    open_score(fial.expand_path(project_path), fial.id, mainwindow)

def open_score(path, score_id, mainwindow):
    url = QUrl.fromLocalFile(path)
    try:
        doc = app.openUrl(url)
    except IOError as e:
        msg = 'Failed to read referenced file {0}.'.format(path)
        QMessageBox.critical(self, app.caption(_("Error")), msg)
        return
    else:
        mainwindow.setCurrentDocument(doc)
        id_str = 'id = "{0}"'.format(score_id)
        cursor = doc.find(id_str)
        mainwindow.setTextCursor(cursor)
