from collections import OrderedDict
from datetime import datetime


class StatusTable(object):

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(StatusTable, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.double_chars = ["❌", "✅"]
        self.columns = OrderedDict(
            [
                ("Directory", 20),
                ("File Name", 20),
                ("Input", 0),
                ("Output", 0),
                ("OCR Text", 10),
                ("IMS?", 0),
                ("AP?", 0),
                ("Status", 6),
                ("Timestamp", 0),
            ]
        )
        self.status = OrderedDict()
        for c in self.columns:
            self.status[c] = ""

        self.status["IMS?"] = "❌"
        self.status["AP?"] = "❌"

        self.print(title=True)

    def update_statuses(self, statuses, show=True):
        for k in statuses:
            if k in self.columns:
                self.status[k] = statuses[k]
        if show:
            self.print()

    def update_status(self, key, value, show=True):
        if key in self.columns:
            self.status[key] = value
            if show:
                self.print()

    # length of string with emojis ✅ = 2 characters
    def elen(self, key):
        k = self.status[key]
        return len(key) - sum(k.count(d) for d in self.double_chars) + self.columns[key]

    def print(self, title=False):
        self.status["Timestamp"] = str(datetime.now())[11:19]
        status_row = [
            (
                self.status[k][0 : self.elen(k)].center(self.elen(k))
                if not title
                else k.center(self.elen(k))
            )
            for k in self.status
        ]
        print(" | ".join(status_row))
        if title:
            print(
                "+".join(
                    [
                        "-" * (len(k) + (1 if i == 0 else 2))
                        for i, k in enumerate(status_row)
                    ]
                )
            )
