"""Radiant items (ledger I9): each runs its base craftable's script with its own effects and rows."""
from buildstore import load_build
from registry import register
from items.craftables import AdaptiveHelm, ArchangelsStaff, Bloodthirster, BlueBuff, Deathblade, EdgeOfNight, GiantSlayer, GiantSlayerNoTank, GuinsoosRageblade, HandOfJustice, HextechGunblade, InfinityEdge, JeweledGauntlet, KrakensFury, LastWhisper, Morellonomicon, NashorsTooth, Quicksilver, NO_BURN, RabadonsDeathcap, RedBuff, SpearOfShojin, SteraksGage, StrikersFlail, TitansResolve, VoidStaff


# ---------------------------------------------------------------- Radiants (I9)
def _radiant(base, key, stats, suffix=""):
    """The Radiant version of `base`: the same class and script, with the Radiant's key, stats effect, rows and
    script effects (read through its GA parameters, BuildItem.ga_param)."""
    name = load_build().item(key).name + suffix
    cls = type(base.__name__ + "Radiant", (base,), {"KEY": key, "STATS": (stats,), "display_name": name,
                                                  "__doc__": f"{name}: {base.__name__} with {key}'s numbers."})
    globals()[cls.__name__] = cls
    register("radiant")(cls)
    return cls


_radiant(AdaptiveHelm, "DA_AdaptiveHelm_Radiant", "GE_AdaptiveHelm_Stats_Radiant")
_radiant(ArchangelsStaff, "DA_ArchangelsStaffRadiant", "GE_ArchangelsStaffRadiant_Stats")
_radiant(Bloodthirster, "DA_BloodthirsterRadiant", "GE_BloodthirsterRadiant_Stats")
_radiant(BlueBuff, "DA_BlueBuffRadiant", "GE_BlueBuff_Radiant_Stats")
_radiant(Deathblade, "DA_DeathbladeRadiant", "GE_DeathbladeRadiant")
_radiant(EdgeOfNight, "DA_EdgeOfNightRadiant", "GE_EdgeOfNightRadiant_Stats")
_radiant(GiantSlayer, "DA_GiantSlayer_Radiant", "GE_GiantSlayer_Radiant_Stats", " (vs Tank)")
_radiant(GiantSlayerNoTank, "DA_GiantSlayer_Radiant", "GE_GiantSlayer_Radiant_Stats", " (vs non-Tank)")
_radiant(GuinsoosRageblade, "DA_GuinsoosRagebladeRadiant", "GE_GuinsoosRagebladeRadiant_Base")
_radiant(HandOfJustice, "DA_HandOfJusticeRadiant", "GE_HandOfJusticeRadiant_Stats")
_radiant(HextechGunblade, "DA_HextechGunbladeRadiant", "GE_HextechGunbladeRadiant_Stats")
_radiant(InfinityEdge, "DA_InfinityEdgeRadiant", "GE_InfinityEdgeRadiant")
_radiant(JeweledGauntlet, "DA_JeweledGauntletRadiant", "GE_JeweledGauntletRadiant")
_radiant(KrakensFury, "DA_KrakensFury_Radiant", "GE_KrakensFury_Stats_Radiant")
_radiant(LastWhisper, "DA_LastWhisperRadiant", "GE_LastWhisperRadiant_Stats")
_radiant(Morellonomicon, "DA_MorellonomiconRadiant", "GE_MorellonomiconRadiant", NO_BURN)
_radiant(NashorsTooth, "DA_NashorsToothRadiant", "GE_NashorsToothRadiant_Stats")
_radiant(Quicksilver, "DA_QuicksilverRadiant", "GE_QuicksilverRadiant_Stats")
_radiant(RabadonsDeathcap, "DA_RabadonsDeathcap_Radiant", "GE_RabadonsDeathcap_Radiant_Stats")
_radiant(RedBuff, "DA_RedBuffRadiant", "GE_RedBuffRadiant", NO_BURN)
_radiant(SpearOfShojin, "DA_SpearOfShojinRadiant", "GE_SpearOfShojinRadiant")
_radiant(SteraksGage, "DA_SteraksGageRadiant", "GE_SteraksGageRadiant_Stats")
_radiant(StrikersFlail, "DA_StrikersFlailRadiant", "GE_StrikersFlailRadiant_Stats")
_radiant(TitansResolve, "DA_TitansResolve_Radiant", "GE_TitansResolve_Radiant_Stats")
_radiant(VoidStaff, "DA_VoidStaffRadiant", "GE_VoidStaffRadiant_Stats")
