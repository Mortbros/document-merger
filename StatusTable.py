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
                ("Directory", {"width": 20, "align": "center"}),
                ("File Name", {"width": 20, "align": "center"}),
                ("Input", {"width": 0, "align": "center"}),
                ("Output", {"width": 0, "align": "center"}),
                ("OCR Text", {"width": 10, "align": "left"}),
                # Image skipped?
                ("IMS?", {"width": 10, "align": "left"}),
                # Already processed?
                ("AP?", {"width": 0, "align": "left"}),
                ("Status", {"width": 6, "align": "center"}),
                ("Timestamp", {"width": 0, "align": "center"}),
            ]
        )
        self.status = OrderedDict()
        for c in self.columns:
            self.status[c] = ""

        self.status["IMS?"] = "❌"
        self.status["AP?"] = "❌"

        self.print(title=True)

    def update_statuses(self, statuses, show=True, reset=""):
        for k in statuses:
            if k in self.columns:
                self.status[k] = statuses[k]
        
        if show:
            self.print(highlight=statuses)

        if reset:
            for k in statuses:
                if k in self.columns:
                    self.status[k] = reset

    def update_status(self, key, value, show=True, reset=""):
        if key in self.columns:
            self.status[key] = value
            if show:
                self.print(highlight=[key])
            
            if reset:
                self.status[key] = reset

    # dirty approximation of glyph length of string with emojis. ✅ = 2 characters in monospace.
    def glen(self, key):
        return len(key) - sum(self.status[key].count(d) for d in self.double_chars) + self.columns[key]["width"]

    def align(self, key, text=None):
        if text == None:
            text = key
        if self.columns[key]["align"] == "center":
            return text.center(self.glen(key))
        elif self.columns[key]["align"] == "left":
            return text.ljust(self.glen(key))
        else: # defaults to center align
            return text.center(self.glen(key))

    def print(self, title=False, highlight=[None]):
        self.status["Timestamp"] = str(datetime.now())[11:19]
        status_row = [
            (
                f"{"\033[30;47m" if k in highlight else ""}{self.align(k, self.status[k][0 : self.glen(k)])}\033[0m"
                if not title
                else self.align(k)
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
