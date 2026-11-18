"""Set 19 items: every item class and the registries the page reads. The classes live in items/ (base, debuffs,
craftables, radiants, artifacts, emblems) and become live with @register (registry.py); this module gathers them so callers
can name any item as set19items.<Class>. Status and evidence per item: docs/ITEMS.md (decision D6).
"""
from items.base import *  # noqa: F401,F403
from items.debuffs import *  # noqa: F401,F403
from items.craftables import *  # noqa: F401,F403
from items.radiants import *  # noqa: F401,F403
from items.artifacts import *  # noqa: F401,F403
from items.emblems import *  # noqa: F401,F403
from registry import REGISTRIES

# the DPS item table: offensive craftables only (owner, 2026-11-17: tank items such as Warmog's are not part of it)
offensive_craftables = sorted(REGISTRIES["craftable"])
radiants = REGISTRIES["radiant"]  # in the order they are defined, below their base items
artifacts = sorted(REGISTRIES["artifact"])
emblems = REGISTRIES["emblem"]
no_item = ["NoItem"]
