# -*- coding: utf-8 -*-
from gi.repository import Gtk

class CiteDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__()
        self.set_name("cite_dialog")

        # Combo box that will hold the citation keys
        self.combo = Gtk.ComboBoxText()
        self.liststore = Gtk.ListStore(str)
        self.combo.set_model(self.liststore)

        cell = Gtk.CellRendererText()
        self.combo.pack_start(cell, True)
        self.combo.add_widget(cell)
        self.combo.set_active(0)

        # Add combo to dialog's content area
        content = self.get_content_area()
        content.pack_start(self.combo, True, 0, 0)

        self._selected_key = None

    def populate_keys(self, keys):
        """keys – iterable of citation keys."""
        self.liststore.clear()
        for k in keys:
            self.liststore.append([k])

    def get_selected_key(self):
        return self.combo.get_active_text()
