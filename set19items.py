"""Set 19 items. Each is written from the selected build (its curve rows and effects), one at a time like the
champions; a class is live only when listed in one of the registries below."""
from item import Item

offensive_craftables = []
artifacts = []
radiants = []
emblems = []
animas = []
no_item = ["NoItem"]


class NoItem(Item):
    """The baseline row every table's ratios are read against."""
    display_name = "NoItem"

    def __init__(self):
        super().__init__(self.display_name, phases=None)
