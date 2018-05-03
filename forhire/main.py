import wx

from libs import sql_helpers
from views import tab1, tab2, tab3

sql_conn = sql_helpers.init_db()


class Root(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(
            self, parent, title="r/ForHire Helper v0.3", size=(1000, 800))

        self.notebook = wx.Notebook(self)

        self.page1 = tab1.Tab1(self.notebook)
        self.page2 = tab2.Tab2(self.notebook)
        self.page3 = tab3.Tab3(self.notebook)

        self.notebook.AddPage(self.page1, "Posts Explorer")
        self.notebook.AddPage(self.page2, text="Keywords and Blacklist")
        self.notebook.AddPage(self.page3, text="Bookmarks")

        self.Show(True)


if __name__ == "__main__":
    app = wx.App(False)
    frame = Root(None)
    frame.Center()
    app.MainLoop()
