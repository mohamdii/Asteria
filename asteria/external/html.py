"""Shared HTML extraction without acquisition or demo dependencies."""
import re
from html import unescape
from html.parser import HTMLParser

class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None
    def handle_starttag(self, tag, attrs):
        if tag=='tr': self.row=[]
        if tag in ('td','th') and self.row is not None: self.cell=[]
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row)
            self.row=None


def plain(raw):
    return ' '.join(unescape(re.sub('<[^>]+>',' ',raw.decode('utf-8'))).split())
