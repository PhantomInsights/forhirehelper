"""
This tab displays all the posts the user has bookmarked.

It also shares some features from the first tab. The biggest
differences are the Search button is not present and
there's a Delete button instead of an Add button.
"""

import html
import webbrowser
from datetime import datetime

import wx
import wx.html2
from wx.adv import NotificationMessage

import main
from libs import sql_helpers
from libs.subreddits import SUBREDDITS_LIST


class Tab3(wx.Panel):

    def __init__(self, *args):
        wx.Panel.__init__(self, *args)

        self.selected_post = ""
        self.posts_list = list()
        self.keywords = list()
        self.blacklist = list()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title_label = wx.StaticText(
            self, label="Manage and filter your bookmarks.")

        self.main_sizer.Add(
            self.title_label, wx.SizerFlags().Center().Border(wx.ALL, 5))

        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.top_sizer, wx.SizerFlags(
        ).Centre().Center().Border(wx.ALL, 5))

        self.top_sizer_flags = wx.SizerFlags(
            1).Center().Expand().Border(wx.ALL, 5)

        self.subreddit_label = wx.StaticText(self, label="Select a Subreddit:")
        self.top_sizer.Add(self.subreddit_label, wx.SizerFlags().Centre())

        self.subreddit_type = wx.ComboBox(
            self, style=wx.CB_READONLY, choices=[item["name"] for item in SUBREDDITS_LIST])
        self.Bind(wx.EVT_COMBOBOX, self.select_subreddit, self.subreddit_type)
        self.top_sizer.Add(self.subreddit_type, self.top_sizer_flags)

        self.post_type_label = wx.StaticText(self, label="Select a Post type:")
        self.top_sizer.Add(self.post_type_label, wx.SizerFlags().Centre())

        self.post_type = wx.ComboBox(self, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.filter_results, self.post_type)
        self.top_sizer.Add(self.post_type, self.top_sizer_flags)

        self.keywords_checkbox = wx.CheckBox(self, label="Apply Keywords")
        self.Bind(wx.EVT_CHECKBOX, self.filter_results, self.keywords_checkbox)
        self.top_sizer.Add(self.keywords_checkbox, self.top_sizer_flags)

        self.blacklist_checkbox = wx.CheckBox(
            self, label="Apply Blacklist")
        self.Bind(wx.EVT_CHECKBOX, self.filter_results,
                  self.blacklist_checkbox)
        self.top_sizer.Add(
            self.blacklist_checkbox, self.top_sizer_flags)

        self.posts_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.posts_table.InsertColumn(0, "Post ID", width=100)
        self.posts_table.InsertColumn(1, "Published Date", width=150)
        self.posts_table.InsertColumn(2, "Author", width=180)
        self.posts_table.InsertColumn(3, "Title", width=-1)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_item)
        self.main_sizer.Add(self.posts_table, wx.SizerFlags(
            1).Expand().Border(wx.ALL, 5))

        self.mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.mid_sizer, wx.SizerFlags(
        ).Centre().Center().Border(wx.ALL, 5))

        self.dm_button = wx.Button(self, label="Send Message")
        self.Bind(wx.EVT_BUTTON, self.send_dm, self.dm_button)
        self.mid_sizer.Add(self.dm_button, self.top_sizer_flags)

        self.link_button = wx.Button(self, label="View on Reddit")
        self.Bind(wx.EVT_BUTTON, self.open_reddit, self.link_button)
        self.mid_sizer.Add(self.link_button, self.top_sizer_flags)

        self.del_button = wx.Button(self, label="Delete from Bookmarks")
        self.Bind(wx.EVT_BUTTON, self.delete_from_bookmarks, self.del_button)
        self.mid_sizer.Add(self.del_button, self.top_sizer_flags)

        self.html_content = wx.html2.WebView.New(self, size=(-1, 400))
        self.main_sizer.Add(self.html_content, wx.SizerFlags(
            1).Expand().Border(wx.ALL, 5))

        self.SetSizer(self.main_sizer)
        self.Bind(wx.EVT_SHOW, self.show_handler)

        # We initialize the tab with the first subreeddit.
        self.subreddit_type.SetValue(SUBREDDITS_LIST[0]["name"])
        self.select_subreddit(None)

    def show_handler(self, event):
        """Called when the Panel is being shown."""

        if event.IsShown():
            self.keywords = [item[0].lower() for item in sql_helpers.load_words(
                main.sql_conn, "keywords")]

            self.blacklist = [item[0].lower() for item in sql_helpers.load_words(
                main.sql_conn, "blacklist")]

            self.load_posts()

    def select_subreddit(self, event):
        """Populates the post type ComboBox with the data from the selected subreddit."""

        for subreddit in SUBREDDITS_LIST:
            if subreddit["name"] == self.subreddit_type.Value:
                rules = subreddit["rules"]
                break

        self.post_type.Clear()
        self.post_type.AppendItems(rules)
        self.post_type.SetValue(rules[0])
        self.load_posts()

    def filter_results(self, event):
        """
        Applies the filters to the results.
        The way it works is a bit hacky.

        Blacklist items takes precedence over keywords.

        When an item checks against the blacklist it is removed
        from the main list.

        When an item checks against the keywords, it is added
        to a new list. And this new list is used to feed the table.        
        """

        self.posts_table.DeleteAllItems()
        temp_posts = self.posts_list[:]
        filtered_posts = list()

        if self.blacklist_checkbox.IsChecked():
            for item in reversed(temp_posts):
                if self.quick_filter(self.blacklist, item):
                    temp_posts.remove(item)

        if self.keywords_checkbox.IsChecked():
            for item in temp_posts:
                if self.quick_filter(self.keywords, item):
                    filtered_posts.append(item)

        if len(filtered_posts) == 0 and self.keywords_checkbox.IsChecked():
            # No results, we do nothing.
            pass
        elif len(filtered_posts) >= 1:
            for item in filtered_posts:
                if self.post_type.GetValue().lower() in item["flair"].lower():
                    self.posts_table.Append(
                        [item["post_id"], item["pub_date"], item["author"], item["title"]])
        else:
            for item in temp_posts:
                if self.post_type.GetValue().lower() in item["flair"].lower():
                    self.posts_table.Append(
                        [item["post_id"], item["pub_date"], item["author"], item["title"]])

        self.posts_table.SetColumnWidth(3, -1)

    def quick_filter(self, words, item):
        """Applies a quick filter iterating over a list of values."""

        for word in words:
            if word in item["title"].lower() or word in item["text"].lower():
                return True
        return False

    def load_posts(self):
        """Loads posts from the posts table specifying a subreddit."""

        for subreddit in SUBREDDITS_LIST:
            if subreddit["name"] == self.subreddit_type.Value:
                selected_subreddit = subreddit["id"]
                break

        self.posts_list = list()

        for item in sql_helpers.load_posts(main.sql_conn, selected_subreddit):
            self.posts_list.append(
                {"post_id": item[0], "subreddit": item[1], "flair": item[2], "author": item[3], "title": item[4],
                 "link": item[5], "text": item[6], "pub_date": item[7]})

        self.filter_results(None)

    def selected_item(self, event):
        """When an item is selected show the text in the WebView."""

        self.selected_post = event.GetText()

        for item in self.posts_list:
            if self.selected_post == item["post_id"]:
                self.html_content.SetPage(html.unescape(item["text"]), "")
                break

    def send_dm(self, event):
        """opens the default web browser with prefilled subject and title."""

        base_url = "https://www.reddit.com/message/compose/?to={}&subject=RE: {}"

        for item in self.posts_list:
            if self.selected_post == item["post_id"]:
                webbrowser.open(base_url.format(item["author"], item["title"]))
                break

    def open_reddit(self, event):
        """opens the default web browser with the post url."""

        base_url = "https://redd.it/{}"

        for item in self.posts_list:
            if self.selected_post == item["post_id"]:
                webbrowser.open(base_url.format(item["post_id"]))
                break

    def delete_from_bookmarks(self, event):
        """opens the default web browser with the post url."""

        for item in self.posts_list:
            if self.selected_post == item["post_id"]:
                sql_helpers.delete_post_from_table(
                    main.sql_conn, item["post_id"])
                temp_toast = NotificationMessage(
                    title="Success", message="Post successfully deleted.")
                temp_toast.Show()
                self.load_posts()
                self.html_content.SetPage("<html><body></body></html>", "")
                break
