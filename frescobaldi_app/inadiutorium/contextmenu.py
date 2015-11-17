from __future__ import unicode_literals

from PyQt4.QtGui import QAction, QMessageBox, QTextCursor
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

    actions = []

    document = mainwindow.currentDocument()
    if not document:
        return actions

    path = document.url().path()
    if not is_in_adiutorium_file(path):
        return actions

    current_score = score.score_under_cursor(cursor)
    if current_score is None:
        return actions

    if current_score.has_fial():
        a = QAction(menu)
        a.setText('Go to source')
        @a.triggered.connect
        def goto_source():
            fial = current_score.fial()
            open_fial(fial, path, mainwindow)

        actions.append(a)

    if current_score.has_id():
        a = QAction(menu)
        a.setText('Go to variations/main')
        @a.triggered.connect
        def goto_variations():
            if is_variations_file(path):
                path_to_open = main_file(path)
            elif is_in_adiutorium_file(path):
                path_to_open = variations_file(path)

            open_score(path_to_open, current_score.headers['id'], mainwindow)

        actions.append(a)

    return actions



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
