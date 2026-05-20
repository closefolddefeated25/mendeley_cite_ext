# -*- coding: utf-8 -*-
"""
mendeley_cite/__init__.py

Exposes the UNO service `com.example.mendeleycite.CiteExtension`.
The only public method is `insertCitation(self, ctx)` which the
toolbar button will call.
"""

import os
import sqlite3
import unohelper
from gi.repository import Gtk

# ------------------------------------------------------------------------
# 1) Locate the Mendeley SQLite DB (default install location)
# ------------------------------------------------------------------------
DEFAULT_DB = os.path.expanduser(
    "~/.local/share/Mendeley Desktop/library.sqlite"
)

def _db_path():
    return DEFAULT_DB

def _connect():
    db = _db_path()
    if not os.path.isfile(db):
        raise FileNotFoundError(f"Mendeley DB not found at {db}")
    return sqlite3.connect(db)

def _load_library():
    """Return a dict {citekey: {title, authors, year}}."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT citationKey, title, authors, year FROM library")
    result = {}
    for key, title, authors, year in cur.fetchall():
        result[key] = {"title": title, "authors": authors, "year": year}
    conn.close()
    return result

# Cache the library so we open the DB only once per process
_LIBRARY = None
def get_library():
    global _LIBRARY
    if _LIBRARY is None:
        _LIBRARY = _load_library()
    return _LIBRARY

# ------------------------------------------------------------------------
# 2) UI helper – the dialog that lists citation keys
# ------------------------------------------------------------------------
from . import cite_dialog   # UI wrapper defined in cite_dialog/cite_dialog.py

# ------------------------------------------------------------------------
# 3) The UNO component itself
# ------------------------------------------------------------------------
class CiteExtension(unohelper.Base):
    """
    UNO component registered as `com.example.mendeleycite.CiteExtension`.
    The method `insertCitation(self, ctx)` is invoked from a toolbar button.
    """
    def __init__(self, ctx):
        self.Context = ctx   # not used further, but kept for API compatibility

    def insertCitation(self, ctx):
        """Insert a formatted citation at the current cursor position."""
        lib = get_library()
        if not lib:
            # In a real extension you could pop up a warning dialog here.
            return True

        # ---- 1) Show the key‑selection dialog ---------------------------
        dlg = cite_dialog.CiteDialog()
        dlg.populate_keys(list(lib.keys()))
        if dlg.run() != Gtk.ResponseType.OK:   # user pressed Cancel or closed the dialog
            return True

        selected_key = dlg.get_selected_key()
        if not selected_key:
            return True

        citation = lib[selected_key]

        # ---- 2) Very simple formatting ----------------------------------
        auths = citation["authors"].split("; ")
        year = citation["year"] or "n.d."
        if len(auths) == 1:
            formatted = f"({auths[0]}, {year})"
        else:
            # Collapse first author + "et al." if >2 authors, otherwise join with '&'
            if len(auths) > 2:
                auths = [auths[0] + " et al."]
            formatted = f"({' & '.join(auths)}, {year})"

        # ---- 3) Insert the formatted string at the cursor ---------------
        # Retrieve the current document from the UNO context
        doc = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.document.Document", ctx)
        cursor = doc.Text.createTextCursor()
        doc.Text.insertString(cursor, formatted, False)

        return True

# ------------------------------------------------------------------------
# 4) Auto‑registration (nothing extra needed – Python UNO detects classes
#    whose name matches the fully‑qualified name declared in manifest.xml)
# ------------------------------------------------------------------------
