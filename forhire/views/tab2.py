"""
In this tab you can manage your keywords and blacklist items.

The code in this tab is highly reusable since both keywords and blacklists are
based on the same principle.
"""

import wx

import main
from libs import sql_helpers


class Tab2(wx.Panel):

    def __init__(self, *args):
        wx.Panel.__init__(self, *args)

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.left_sizer, wx.SizerFlags(
            1).Centre().Center().Expand().Border(wx.ALL, 5))
        self.main_sizer.Add(self.right_sizer, wx.SizerFlags(
            1).Centre().Center().Expand().Border(wx.ALL, 5))

        ########
        # Keywords section starts here.
        ########

        self.keywords_label = wx.StaticText(self, label="Keywords")
        self.left_sizer.Add(self.keywords_label,
                            wx.SizerFlags().Center().Border(wx.ALL, 5))

        self.keywords_desc = wx.StaticText(
            self, label="Add keywords that you are looking for, e.g: python, nodejs, seo, writing")
        self.left_sizer.Add(self.keywords_desc,
                            wx.SizerFlags().Expand().Left().Border(wx.ALL, 5))

        self.left_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer.Add(self.left_sub_sizer, wx.SizerFlags(
        ).Expand().Centre().Border(wx.ALL, 5))

        self.keywords_entry = wx.TextCtrl(self)
        self.left_sub_sizer.Add(self.keywords_entry, wx.SizerFlags(
            1).Expand().Centre().Border(wx.ALL, 5))

        self.keywords_add_button = wx.Button(self, label="Add")
        self.Bind(wx.EVT_BUTTON, lambda event, table_name="keywords": self.add_word(
            event, table_name), self.keywords_add_button)
        self.left_sub_sizer.Add(self.keywords_add_button,
                                wx.SizerFlags().Centre().Border(wx.ALL, 5))

        self.keywords_del_button = wx.Button(self, label="Delete")
        self.Bind(wx.EVT_BUTTON, lambda event, table_name="keywords": self.delete_word(
            event, table_name), self.keywords_del_button)
        self.left_sub_sizer.Add(self.keywords_del_button,
                                wx.SizerFlags().Centre().Border(wx.ALL, 5))

        self.keywords_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.left_sizer.Add(self.keywords_list, wx.SizerFlags(
            1).Expand().Center().Border(wx.ALL, 5))

        ########
        # Blacklist section starts here.
        ########

        self.blacklist_label = wx.StaticText(self, label="Blacklist")
        self.right_sizer.Add(self.blacklist_label,
                             wx.SizerFlags().Center().Border(wx.ALL, 5))

        self.blacklist_desc = wx.StaticText(
            self, label="Add words that you want to filter out, e.g: simple, rockstar, ninja, crypto")
        self.right_sizer.Add(self.blacklist_desc,
                             wx.SizerFlags().Expand().Left().Border(wx.ALL, 5))

        self.right_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.right_sizer.Add(self.right_sub_sizer,
                             wx.SizerFlags().Expand().Centre().Border(wx.ALL, 5))

        self.blacklist_entry = wx.TextCtrl(self)
        self.right_sub_sizer.Add(
            self.blacklist_entry, wx.SizerFlags(1).Expand().Centre().Border(wx.ALL, 5))

        self.blacklist_add_button = wx.Button(self, label="Add")
        self.Bind(wx.EVT_BUTTON, lambda event, table_name="blacklist": self.add_word(
            event, table_name), self.blacklist_add_button)
        self.right_sub_sizer.Add(
            self.blacklist_add_button, wx.SizerFlags().Centre().Border(wx.ALL, 5))

        self.blacklist_del_button = wx.Button(self, label="Delete")
        self.Bind(wx.EVT_BUTTON, lambda event, table_name="blacklist": self.delete_word(
            event, table_name), self.blacklist_del_button)
        self.right_sub_sizer.Add(
            self.blacklist_del_button, wx.SizerFlags().Centre().Border(wx.ALL, 5))

        self.blacklist_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.right_sizer.Add(self.blacklist_list, wx.SizerFlags(
            1).Expand().Center().Border(wx.ALL, 5))

        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_SHOW, self.show_handler)

    def show_handler(self, event):
        """Called when the Panel is being shown."""

        if event.IsShown():
            self.load_words("keywords")
            self.load_words("blacklist")

    def add_word(self, event, table_name):
        """Adds the new word to the database."""

        if table_name == "keywords":
            new_word = self.keywords_entry.Value
        elif table_name == "blacklist":
            new_word = self.blacklist_entry.Value

        if new_word != "":
            sql_helpers.insert_word_to_table(
                main.sql_conn, table_name, new_word)
            self.load_words(table_name)

            if table_name == "keywords":
                self.keywords_entry.SetValue("")
            elif table_name == "blacklist":
                self.blacklist_entry.SetValue("")

    def delete_word(self, event, table_name):
        """Deletes the selected word from the database."""

        if table_name == "keywords":
            selected_word = self.keywords_list.StringSelection
        elif table_name == "blacklist":
            selected_word = self.blacklist_list.StringSelection

        if selected_word != "":
            sql_helpers.delete_word_from_table(
                main.sql_conn, table_name, selected_word)
            self.load_words(table_name)

    def load_words(self, table_name):
        """Loads the values from keywords or blacklist."""

        temp_words = sql_helpers.load_words(main.sql_conn, table_name)

        if table_name == "keywords":
            self.keywords_list.Clear()

            for word in temp_words:
                self.keywords_list.Append(word[0])

        elif table_name == "blacklist":
            self.blacklist_list.Clear()

            for word in temp_words:
                self.blacklist_list.Append(word[0])
