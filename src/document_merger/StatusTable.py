from collections import OrderedDict
from datetime import datetime


class StatusTable(object):

    def __new__(cls, print_output):
        if not hasattr(cls, "instance"):
            cls.instance = super(StatusTable, cls).__new__(cls)
            cls.instance.print_output = print_output
        return cls.instance

    def __init__(self, print_output):
        self.double_chars = ["❌", "✅"]
        self.columns = OrderedDict(
            [
                ("Directory", {"width": 20, "align": "center"}),
                ("File Name", {"width": 20, "align": "center"}),
                ("Input", {"width": 0, "align": "center"}),
                ("Output", {"width": 0, "align": "center"}),
                ("OCR Text", {"width": 5, "align": "left"}),
                # Image skipped?
                ("IMS?", {"width": 10, "align": "left"}),
                # Already processed?
                ("AP?", {"width": 0, "align": "left"}),
                ("Status", {"width": 11, "align": "center"}),
                ("Timestamp", {"width": 0, "align": "center"}),
            ]
        )
        self.status = OrderedDict()
        for c in self.columns:
            self.status[c] = ""

        self.status["IMS?"] = "❌"
        self.status["AP?"] = "❌"

        self.print_output = print_output

        self.print(title=True)

    def update_statuses(self, statuses, show=True, reset_to={}):
        """
        statuses (dict[str]): the names and values of the column that will be updated
        show (bool): flag to show changed values immediately or on next update
        reset_to (dict[str]): reset the status to this value on next change
        """
        for k in statuses:
            if k in self.columns:
                self.status[k] = statuses[k]

        if show:
            self.print(highlight=statuses)

        if reset_to:
            for k in self.columns:
                self.status[k] = reset_to[k] if k in reset_to.keys() else self.status[k]

    def update_status(self, key, value, show=True, reset_to=""):
        """
        key (str): the name of the column that will be updated
        value (any): the value that is being updated
        show (bool): flag to show changed values immediately or on next update
        reset_to (any): reset the status to this value on next change
        """
        if key in self.columns:
            self.status[key] = value
            if show:
                self.print(highlight=[key])

            if reset_to:
                self.status[key] = reset_to

    def glen(self, key):
        """
        dirty approximation of glyph length of string with emojis. ✅ = 2 characters in monospace.
        key (str): the value of the cell in the table
        """
        return (
            len(key)
            - sum(self.status[key].count(d) for d in self.double_chars)
            + int(self.columns[key]["width"])
        )

    def align(self, key, text=None):
        if text == None:
            text = key
        if self.columns[key]["align"] == "center":
            return text.center(self.glen(key))
        elif self.columns[key]["align"] == "left":
            return text.ljust(self.glen(key))
        else:  # defaults to center align
            return text.center(self.glen(key))

    def print(self, title=False, highlight=[None]):
        if self.print_output:
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
