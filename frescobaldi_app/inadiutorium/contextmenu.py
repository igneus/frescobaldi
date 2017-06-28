from PyQt5.QtWidgets import QApplication, QAction, QMessageBox
from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtCore import QUrl

import app

from . import is_in_adiutorium_file
from .variations import is_variations_file, main_file, variations_file
from . import score

def actions(cursor, menu, mainwindow):
    """
    Return a list of In adiutorium-related actions (maybe empty)
    for files at the cursor to open.
    """

    return ActionsFactory(cursor, menu, mainwindow).actions()

class ActionsFactory:
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

        actions.append(self._copy())
        actions.append(self._duplicate())

        if self._current_score.has_fial():
            actions.append(self._goto_source())

        if self._current_score.has_id():
            actions.append(self._goto_variations())

        return actions

    def _copy(self):
        a = QAction(self._menu)
        a.setText('Copy score')

        @a.triggered.connect
        def trigger():
            # copy score
            copy_cursor = QTextCursor(self._document)
            score_end = self._current_score.end()
            # it isn't easily possible to get score start index
            # from the DOM ...
            start_token = '\\score'
            score_start_cur = self._document.find(start_token, score_end, QTextDocument.FindBackward)
            score_start = score_start_cur.position() - len(start_token)
            copy_cursor.setPosition(score_start, QTextCursor.MoveAnchor)
            copy_cursor.setPosition(score_end, QTextCursor.KeepAnchor)

            # copy to clipboard
            fragment = copy_cursor.selection()
            QApplication.clipboard().setText(fragment.toPlainText())

        return a

    def _duplicate(self):
        a = QAction(self._menu)
        a.setText('Duplicate score')

        @a.triggered.connect
        def trigger():
            # add newline after the score
            cursor = QTextCursor(self._document)
            cursor.setPosition(self._current_score.end(), QTextCursor.MoveAnchor)
            cursor.insertText('\n\n')

            # copy score
            copy_cursor = QTextCursor(self._document)
            score_end = self._current_score.end()
            # it isn't easily possible to get score start index
            # from the DOM ...
            start_token = '\\score'
            score_start_cur = self._document.find(start_token, score_end, QTextDocument.FindBackward)
            score_start = score_start_cur.position() - len(start_token)
            while self._document.characterAt(score_start - 1) == ' ':
                score_start -= 1
            copy_cursor.setPosition(score_start, QTextCursor.MoveAnchor)
            copy_cursor.setPosition(score_end, QTextCursor.KeepAnchor)

            # insert copy
            fragment = copy_cursor.selection()
            cursor.insertFragment(fragment)

            # make it selected
            fragment_len = len(fragment.toPlainText())
            score_beginning = cursor.position() - fragment_len
            cursor.setPosition(score_beginning, QTextCursor.KeepAnchor)
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
        QMessageBox.critical(mainwindow, app.caption(_("Error")), msg)
        return
    else:
        mainwindow.setCurrentDocument(doc)
        id_str = 'id = "{0}"'.format(score_id)
        cursor = doc.find(id_str)
        if cursor.isNull():
            msg = "Score with id '{0}' not found.".format(score_id)
            QMessageBox.information(mainwindow, app.caption(_("Error")), msg)
        else:
            mainwindow.setTextCursor(cursor)
