from gettext import gettext as _
from gi.repository import GObject, Gtk, Gio, Gedit
import html_matcher

# some key combo do not work?, "<Primary><Shift>a", "<Alt>a", "<Alt>s"
ACTIONS = {
    'matchhtmltagson': {
        'label': _("Match Html Parent Tags"),
        #'key': ['<Primary><Shift>q'],
        'key': ['<Alt>z'],
        'method': 'match_tags_on',
    },
    'matchhtmltagsoff': {
        'label': _("Match Html Parent Tags Clear"),
        'key': ['<Alt>x'],
        'method': 'match_tags_off',
    },
    'matchhtmltagsselect': {
        'label': _("Match Html Parent Tags Select Between"),
        'key': ['<Alt>q'],
        'method': 'match_tags_select',
    }
}

class Matchhtmltags(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "Matchhtmltags"
    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.menu_ext = self.extend_menu("edit-section-1")

        for action, config in ACTIONS.items():
            item = Gio.MenuItem.new(config['label'], "win.%s" % action)
            self.menu_ext.append_menu_item(item)
            self.app.set_accels_for_action("win.%s" % action, config['key'])


    def do_deactivate(self):
        for action in ACTIONS.keys():
            self.app.set_accels_for_action("win.%s" % action, [])

        del self.menu_ext

class MatchhtmltagsWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "MatchhtmltagsWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        try:
            """
            # TODO: DOES NOT WORK?
            for action, config in ACTIONS.items():
                item = Gio.SimpleAction(name=action)
                item.connect('activate', lambda e, f: getattr(self, config['method'])())
                self.window.add_action(item)
            """
            action = Gio.SimpleAction(name="matchhtmltagson")
            action.connect('activate', lambda e, f: getattr(self, 'match_tags_on')())
            self.window.add_action(action)

            action = Gio.SimpleAction(name="matchhtmltagsoff")
            action.connect('activate', lambda e, f: getattr(self, 'match_tags_off')())
            self.window.add_action(action)

            action = Gio.SimpleAction(name="matchhtmltagsselect")
            action.connect('activate', lambda e, f: getattr(self, 'match_tags_select')())
            self.window.add_action(action)

        except Exception:
            print("Error initializing \"Matchhtmltags\" plugin")

    def do_update_state(self):
        for action, config in ACTIONS.items():
            self.window.lookup_action(action).set_enabled(self.window.get_active_document() is not None)

    def match_tags_on(self):
        window_src_buf = self.window.get_active_document()
        if not window_src_buf:
            return

        #print(window_src_buf.get_text(window_src_buf.get_start_iter(),window_src_buf.get_end_iter(),window_src_buf))

        mark = window_src_buf.get_insert()

        start_iter = window_src_buf.get_start_iter()
        mark_iter = window_src_buf.get_iter_at_mark(mark)
        end_iter = window_src_buf.get_end_iter()

        #html_content = window_src_buf.get_text(mark_iter,end_iter,window_src_buf)
        html_content = window_src_buf.get_text(start_iter,end_iter,window_src_buf)

        #start_tg_idx, end_tg_idx = html_matcher.find(html_content,mark_iter.get_offset())
        start_tg, end_tg = html_matcher.get_tags(html_content,mark_iter.get_offset())

        """
        start_iter.set_offset(idx)
        end_iter.set_offset(idx)
        html_content = window_src_buf.get_text(mark_iter,end_iter,window_src_buf)
        print("content in tags:",html_content)
        """

        #self.smart_highlight_on(window_src_buf,start_tg.end,end_tg.start)
        #self.smart_highlight_on(window_src_buf,start_tg.start,end_tg.end)
        #self.smart_highlight_on(window_src_buf,start_tg_idx,end_tg_idx)

        self.smart_highlight_on(window_src_buf,start_tg.start,start_tg.end)
        self.smart_highlight_on(window_src_buf,end_tg.start,end_tg.end)

    def match_tags_off(self):
        window_src_buf = self.window.get_active_document()
        if not window_src_buf:
            return

        self.smart_highlight_off(window_src_buf)

    def match_tags_select(self):
        window_src_buf = self.window.get_active_document()
        if not window_src_buf:
            return

        start_iter = window_src_buf.get_start_iter()

        mark = window_src_buf.get_insert()
        mark_iter = window_src_buf.get_iter_at_mark(mark)

        end_iter = window_src_buf.get_end_iter()

        html_content = window_src_buf.get_text(start_iter,end_iter,window_src_buf)
        start_tg, end_tg = html_matcher.get_tags(html_content,mark_iter.get_offset())

        mark_iter.set_offset(end_tg.start)
        window_src_buf.move_mark(mark,mark_iter)

    def smart_highlight_on(self,doc, highlight_start, highlight_end):
	    if doc.get_tag_table().lookup('smart_highlight') == None:
		    #tag = doc.create_tag("smart_highlight", foreground="#2e3436", background="#888a85")
		    tag = doc.create_tag("smart_highlight", background="#a40000")
	    doc.apply_tag_by_name('smart_highlight', doc.get_iter_at_offset(highlight_start), doc.get_iter_at_offset(highlight_end))

    def smart_highlight_off(self,doc):
        start, end = doc.get_bounds()

        doc.remove_tag_by_name('smart_highlight', start, end)

                

