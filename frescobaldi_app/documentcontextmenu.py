# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
A context menu with actions for a Document.
Used by the tabbar and the doclist tool.
"""


import weakref
import os

from PyQt5.QtWidgets import QMenu, QMessageBox
from PyQt5.QtCore import QUrl

import app
import icons
from inadiutorium import is_in_adiutorium_file
from inadiutorium.variations import is_variations_file, main_file, variations_file


class DocumentContextMenu(QMenu):
    def __init__(self, mainwindow):
        super(DocumentContextMenu, self).__init__(mainwindow)
        self._doc = lambda: None

        self.createActions()
        app.translateUI(self)
        self.aboutToShow.connect(self.updateActions)

    def createActions(self):
        self.doc_save = self.addAction(icons.get('document-save'), '')
        self.doc_save_as = self.addAction(icons.get('document-save-as'), '')
        self.addSeparator()
        self.doc_close = self.addAction(icons.get('document-close'), '')
        self.doc_close_others = self.addAction(icons.get('document-close'), '')
        self.addSeparator()
        self.doc_toggle_sticky = self.addAction(icons.get('pushpin'), '')
        self.doc_toggle_sticky.setCheckable(True)

        self.doc_save.triggered.connect(self.docSave)
        self.doc_save_as.triggered.connect(self.docSaveAs)
        self.doc_close.triggered.connect(self.docClose)
        self.doc_close_others.triggered.connect(self.docCloseOther)
        self.doc_toggle_sticky.triggered.connect(self.docToggleSticky)

        self.addSeparator()
        self.doc_open_inadiutorium_variations = self.addAction(icons.get('document-open'), '')
        self.doc_open_inadiutorium_variations.triggered.connect(self.docOpenInAdiutoriumVariations)

    def updateActions(self):
        """Called just before show."""
        doc = self._doc()
        if doc:
            import engrave
            engraver = engrave.Engraver.instance(self.mainwindow())
            self.doc_toggle_sticky.setChecked(doc is engraver.stickyDocument())

    def translateUI(self):
        self.doc_save.setText(_("&Save"))
        self.doc_save_as.setText(_("Save &As..."))
        self.doc_close.setText(_("&Close"))
        self.doc_close_others.setText(_("Close Other Documents"))
        self.doc_toggle_sticky.setText(_("Always &Engrave This Document"))

        self.doc_open_inadiutorium_variations.setText('Open Variations/Main file')

    def mainwindow(self):
        return self.parentWidget()

    def exec_(self, document, pos):
        self._doc = weakref.ref(document)
        super(DocumentContextMenu, self).exec_(pos)

    def docSave(self):
        doc = self._doc()
        if doc:
            self.mainwindow().saveDocument(doc)

    def docSaveAs(self):
        doc = self._doc()
        if doc:
            self.mainwindow().saveDocumentAs(doc)

    def docClose(self):
        doc = self._doc()
        if doc:
            self.mainwindow().closeDocument(doc)

    def docCloseOther(self):
        """ Closes all documents that are not our current document. """
        cur = self._doc()
        if not cur:
            return # not clear which to keep open...
        win = self.mainwindow()
        win.setCurrentDocument(cur, findOpenView=True)
        win.closeOtherDocuments()

    def docToggleSticky(self):
        doc = self._doc()
        if doc:
            import engrave
            engraver = engrave.Engraver.instance(self.mainwindow())
            if doc is engraver.stickyDocument():
                engraver.setStickyDocument(None)
            else:
                engraver.setStickyDocument(doc)

    def docOpenInAdiutoriumVariations(self):
        """
        If current file is a 'main' file in the In adiutorium project,
        opens it's 'variations' file.
        In the other case opens the corresponding 'main' file.
        """

        cur = self._doc()
        if not cur:
            return

        path = cur.url().path()

        path_to_open = None
        if is_variations_file(path):
            path_to_open = main_file(path)
        elif is_in_adiutorium_file(path):
            path_to_open = variations_file(path)
        else:
            msg = 'Current file does not seem to be part of the In adiutorium project structure.'
            QMessageBox.critical(self, app.caption(_("Error")), msg)
            return

        url = QUrl.fromLocalFile(path_to_open)
        try:
            doc = app.openUrl(url)
        except IOError as e:
            msg = 'Failed to read corresponding file %s.' % path_to_open
            QMessageBox.critical(self, app.caption(_("Error")), msg)
            return
        else:
            self.mainwindow().setCurrentDocument(doc)
