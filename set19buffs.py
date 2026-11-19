"""Set 19 traits, augments and other buffs: every class and the registries the page reads. The classes live in
traits/ (one module per trait) and become live with @register (registry.py); this module gathers them so callers can
name any buff as set19buffs.<Class>. The import order below is the order traits are offered and run in.
"""
from traits.base import *  # noqa: F401,F403
from traits.encore import *  # noqa: F401,F403
from traits.trickshot import *  # noqa: F401,F403
from traits.kda import *  # noqa: F401,F403
from traits.swiftstriker import *  # noqa: F401,F403
from traits.arcanist import *  # noqa: F401,F403
from traits.hyperpop import *  # noqa: F401,F403
from traits.ionic_spark import *  # noqa: F401,F403
from traits.hitmaker import *  # noqa: F401,F403
from traits.illbeats import *  # noqa: F401,F403
from traits.heartsteel import *  # noqa: F401,F403
from traits.true_damage import *  # noqa: F401,F403
from traits.prodigy import *  # noqa: F401,F403
from traits.pentakill import *  # noqa: F401,F403
from traits.composer import *  # noqa: F401,F403
from traits.renegade import *  # noqa: F401,F403
from traits.classical import *  # noqa: F401,F403
from traits.slayer import *  # noqa: F401,F403
from traits.choreographer import *  # noqa: F401,F403
from traits.jazz import *  # noqa: F401,F403
from traits.beach_pop import *  # noqa: F401,F403
from traits.gu_feng import *  # noqa: F401,F403
from augments.combat import *  # noqa: F401,F403
from registry import REGISTRIES

class_buffs = REGISTRIES["trait"]  # traits
augments = REGISTRIES["augment"]
no_buff = ["NoBuff"]
