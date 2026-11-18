"""The Encore trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Encore(BuildTrait):
    """Encore (DA_Encore19): "When Encore champions fire projectiles with their abilities, they fire an extra one
    with reduced effectiveness." The extra missiles are in each member's spell script, which reads
    CT_Encore19 RecastEffectiveness at the Encore tier (e.g. Neeko). Non-members are unaffected."""
    KEY = "DA_Encore19"
    display_name = "Encore"


Encore.levels = [0] + Encore.breakpoints()  # the newest build's breakpoints (units on the board)
