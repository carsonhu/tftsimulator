# from collections import deque
import re
from item import Item
from role import Role
import set15buffs
import status

# from champion import Stat

offensive_craftables = [
    "Rabadons",
    "Bloodthirster",
    "HextechGunblade",
    "Archangels",
    "HoJ",
    "InfinityEdge",
    "LastWhisper",
    "Shojin",
    "Titans",
    "GS",
    "GSNoGiant",
    "Nashors",
    "StrikersFlail",
    "Deathblade",
    "QSS",
    "JeweledGauntlet",
    "Red",
    "SteraksGage",
    "Blue",
    "Morellos",
    "TacticiansCrown",
    "Adaptive",
    "GuinsoosRageblade",
    "VoidStaff",
    "KrakensFury",
]

mana_items = ["Blue", "Shojin", "GuinsoosRageblade", "Nashors", "Adaptive"]

artifacts = [
    "InfinityForce",
    "Fishbones",
    "RFC",
    "Mittens",
    "GamblersBlade",
    "WitsEnd",
    "LichBane",
    "GoldCollector",
    "Flickerblade",
    "ShivArtifact",
]

radiants = [
    "RadiantBlue",
    "RadiantVoidStaff",
    "RadiantArchangels",
    "RadiantKrakensFury",
    "RadiantLastWhisper",
    "RadiantGS",
    "RadiantRabadons",
    "RadiantJeweledGauntlet",
    "RadiantNashors",
    "RadiantShojin",
    "RadiantInfinityEdge",
    "RadiantDeathblade",
    "RadiantTitans",
    "RadiantStrikersFlail",
    "RadiantHoJ",
    "RadiantRed",
    "RadiantMorellos",
    "RadiantQSS",
    "RadiantAdaptive",
    "RadiantSteraksGage",
    "RadiantGuinsoosRageblade",
]

no_item = ["NoItem"]


class NoItem(Item):
    def __init__(self):
        super().__init__("NoItem", phases=None)


class Rabadons(Item):
    def __init__(self):
        super().__init__(
            "Rabadon's Deathcap",
            ap=50,
            dmgMultiplier=0.15,
            has_radiant=True,
            phases=None,
        )


class Bloodthirster(Item):
    def __init__(self):
        super().__init__("Bloodthirster", ad=15, ap=15, omnivamp=0.20, phases=None)


class EdgeOfNight(Item):
    def __init__(self):
        super().__init__("Edge of Night", ad=10, ap=10, aspd=20, phases=None)


class HextechGunblade(Item):
    def __init__(self):
        super().__init__(
            "Gunblade", ad=20, ap=20, manaRegen=1, omnivamp=0.15, phases=None
        )


class GuinsoosRagebladeOld(Item):
    def __init__(self):
        super().__init__(
            "Guinsoo's Rageblade (Old)",
            aspd=10,
            ap=10,
            has_radiant=True,
            phases=["postAttack"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.aspd.stat <= 5:
            champion.aspd.add += 5
        return 0


class GuinsoosRageblade(Item):
    def __init__(self):
        super().__init__(
            "Guinsoo's Rageblade",
            aspd=10,
            ap=10,
            has_radiant=True,
            phases=["onUpdate"],
        )
        self.next_bonus = 1
        self.aspd_bonus = 7

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            if champion.aspd.stat <= 5:
                champion.aspd.add += self.aspd_bonus
            self.next_bonus += 1
        return 0


class Archangels(Item):
    def __init__(self):
        super().__init__(
            "Archangels",
            manaRegen=1,
            ap=20,
            has_radiant=True,
            phases=["onUpdate"],
        )
        self.nextAP = 5

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAP:
            champion.ap.add += 30
            self.nextAP += 5
        return 0


class VoidStaff(Item):
    def __init__(self):
        super().__init__(
            "Void Staff",
            manaRegen=2,
            ap=35,
            aspd=15,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.mr.mult = 0.7
        return 0


class Warmogs(Item):
    def __init__(self):
        super().__init__("Warmogs", hp=1000, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class HoJ(Item):
    def __init__(self):
        super().__init__(
            "Hand of Justice",
            manaRegen=1,
            crit=20,
            ad=30,
            ap=30,
            omnivamp=0.12,
            has_radiant=True,
            phases=None,
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class TacticiansCrown(Item):
    def __init__(self):
        super().__init__(
            "Tacticians' Crown (Coronation)", aspd=20, ad=25, ap=30, phases=None
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class StrikersFlail(Item):
    def __init__(self):
        super().__init__(
            "StrikersFlail",
            crit=20,
            hp=150,
            aspd=20,
            dmgMultiplier=0.1,
            has_radiant=True,
            phases=["onCrit"],
        )
        self.current_buff = 0
        self.buff_duration = 5
        self.dmg_amp_value = 0.05

    def performAbility(self, phase, time, champion, input_=0):
        champion.applyStatus(
            status.DmgAmpModifier(
                "StrikersFlail {} {}".format(id(self), self.current_buff)
            ),
            self,
            time,
            self.buff_duration,
            self.dmg_amp_value,
        )
        self.current_buff = (self.current_buff + 1) % 4
        return 0


class Guardbreaker(Item):
    def __init__(self):
        super().__init__(
            "Guardbreaker",
            crit=20,
            ap=10,
            hp=150,
            aspd=20,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.25
        return 0


class GuardbreakerNoGuard(Item):
    def __init__(self):
        super().__init__(
            "Guardbreaker (no shield)",
            crit=20,
            hp=150,
            ap=10,
            aspd=20,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.1
        return 0


class InfinityEdge(Item):
    def __init__(self):
        super().__init__(
            "Infinity Edge",
            ad=35,
            crit=35,
            has_radiant=True,
            phases=["postPreCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0


class LastWhisper(Item):
    def __init__(self):
        super().__init__(
            "Last Whisper",
            aspd=20,
            crit=20,
            ad=15,
            has_radiant=True,
            phases=["preAttack"],
        )

    def performAbility(self, phase, time, champion, opponents):
        # NOTE: LW usually applies AFTER attack but we want to calculate w/ reduced armor
        for opponent in champion.opponents:
            opponent.armor.mult = 0.7
        return 0


class Shojin(Item):
    def __init__(self):
        super().__init__(
            "Spear of Shojin",
            ad=20,
            manaRegen=1,
            ap=10,
            has_radiant=True,
            phases=["preCombat"],
        )
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(5)
        return 0


class Titans(Item):
    def __init__(self):
        super().__init__(
            "Titan's Resolve",
            aspd=10,
            armor=20,
            has_radiant=True,
            phases="preAttack",
        )
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 25:
            champion.bonus_ad.addStat(2)
            champion.ap.addStat(2)
        self.stacks += 1
        if self.stacks == 25:
            champion.armor.addStat(20)
            champion.mr.addStat(20)
        return 0


class Nashors(Item):
    def __init__(self):
        super().__init__(
            "Nashor's Tooth",
            aspd=10,
            hp=150,
            ap=20,
            manaRegen=2,
            has_radiant=True,
            phases=["postAbility", "onUpdate"],
        )
        self.active = False
        self.wearoffTime = 9999
        self.base_duration = 5
        self.aspdBoost = 30
        # we just dont treat it as a sttus

    def performAbility(self, phase, time, champion, input_=0):
        duration = champion.castTime + self.base_duration  # add cast time
        if phase == "postAbility":
            if not self.active:
                # if not active, give the AS bonus
                champion.aspd.addStat(self.aspdBoost)
            self.active = True
            self.wearoffTime = time + duration
        elif phase == "onUpdate":
            if time > self.wearoffTime and self.active:
                # wearing off
                self.active = False
                champion.aspd.addStat(self.aspdBoost * -1)
        return 0


class Adaptive(Item):
    def __init__(self):
        super().__init__(
            "Adaptive Helm",
            manaRegen=2,
            ad=15,
            ap=15,
            has_radiant=True,
            phases=["preCombat"],
        )
        self.mult = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaGainMultiplier.addStat(0.15)
        return 0


class KrakensFury(Item):
    def __init__(self):
        super().__init__(
            "Kraken's Fury",
            aspd=10,
            ad=15,
            has_radiant=True,
            phases="preAttack",
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(3)
        return 0


class Deathblade(Item):
    def __init__(self):
        super().__init__("Deathblade", ad=55, has_radiant=True, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.1
        return 0


class SteraksGage(Item):
    def __init__(self):
        super().__init__("Sterak's Gage", ad=40, hp=300, has_radiant=True, phases=None)


class QSS(Item):
    def __init__(self):
        super().__init__("Quicksilver", aspd=30, crit=20, phases="onUpdate")
        self.nextAS = 2
        self.asGain = 3
        self.procs_left = 9

    def performAbility(self, phase, time, champion, input_=0):
        if time >= self.nextAS and self.procs_left > 0:
            champion.aspd.addStat(self.asGain)
            self.nextAS += 2
            self.procs_left -= 1
        return 0


class JeweledGauntlet(Item):
    def __init__(self):
        super().__init__(
            "Jeweled Gauntlet",
            crit=35,
            ap=35,
            has_radiant=True,
            phases=["postPreCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0


class Red(Item):
    def __init__(self):
        super().__init__("Red (no burn yet)", aspd=35, dmgMultiplier=0.06, phases=None)


class Morellos(Item):
    def __init__(self):
        super().__init__(
            "Morellos (no burn yet)", ap=20, manaRegen=2, hp=150, phases=None
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class Shiv(Item):
    def __init__(self):
        super().__init__(
            "Statikk Shiv",
            ap=15,
            aspd=15,
            mana=15,
            has_radiant=True,
            phases=["preAttack"],
        )
        self.shivDmg = 30
        self.shivTargets = 4
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg
            # only consider dmg to primary target
            # champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
            for opponent in champion.opponents[0 : self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg, "magical", time)
                opponent.applyStatus(status.MRReduction("MR"), champion, time, 5, 0.7)
        return 0


class GS(Item):
    # needs reworking
    def __init__(self):
        super().__init__(
            "Giant Slayer",
            aspd=20,
            ad=20,
            ap=20,
            has_radiant=True,
            phases="preCombat",
        )

    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        champion.dmgMultiplier.add += 0.1
        if len(champion.opponents) > 0:
            vsGiants = champion.opponents[0].role == Role.TANK
            if vsGiants:
                champion.dmgMultiplier.add += 0.15
        return 0


class GSNoGiant(Item):
    # needs reworking
    def __init__(self):
        super().__init__(
            "Giant Slayer (no Giant)",
            aspd=10,
            ad=25,
            ap=25,
            has_radiant=True,
            phases="preCombat",
        )

    def performAbility(self, phase, time, champion, input_):
        champion.dmgMultiplier.add += 0.1
        return 0


class Bramble(Item):
    def __init__(self):
        super().__init__("Bramble Vest", armor=55, phases=None)


class Blue(Item):
    def __init__(self):
        super().__init__(
            "Blue Buff",
            manaRegen=5,
            ap=15,
            ad=15,
            has_radiant=True,
            phases=None,
        )


### ARTIFACTS


class InfinityForce(Item):
    def __init__(self):
        super().__init__(
            "Infinity Force",
            ad=25,
            ap=25,
            aspd=25,
            hp=250,
            mana=25,
            item_type="Artifact",
            phases=None,
        )


class Fishbones(Item):
    def __init__(self):
        super().__init__("Fishbones", aspd=50, ad=20, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0


class RFC(Item):
    def __init__(self):
        super().__init__("Rapid Firecannon", aspd=66, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0


class Mittens(Item):
    def __init__(self):
        super().__init__("Mittens", aspd=60, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0


class GamblersBlade(Item):
    def __init__(self):
        super().__init__("Gambler's Blade (30g)", aspd=65, ap=10, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0


class GoldCollector(Item):
    def __init__(self):
        super().__init__("Gold Collector", ad=25, crit=30, phases=None)

    def performAbility(self, phase, time, champion, input_):
        return 0


class LichBane(Item):
    def __init__(self):
        super().__init__(
            "Lich Bane", ap=30, aspd=30, phases=["preAbility", "preAttack"]
        )
        self.dmg = {2: 240, 3: 320, 4: 400, 5: 480, 6: 540}
        self.enhancedAuto = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            self.enhancedAuto = True
        elif phase == "preAttack":
            if self.enhancedAuto:
                dmg = self.dmg[champion.stage]
                champion.doDamage(
                    champion.opponents[0], [], 0, dmg, dmg, "magical", time
                )
                self.enhancedAuto = False
        return 0


class WitsEnd(Item):
    def __init__(self):
        super().__init__("Wit's End", aspd=30, mr=30, hp=300, phases="preAttack")
        self.dmg = {2: 42, 3: 60, 4: 75, 5: 90, 6: 100}

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = self.dmg[champion.stage]
        champion.doDamage(
            champion.opponents[0], [], 0, baseDmg, baseDmg, "magical", time
        )
        return 0


class ShivArtifact(Item):
    def __init__(self):
        super().__init__(
            "Statikk Shiv (Artifact)",
            ap=40,
            aspd=40,
            has_radiant=True,
            phases=["preAttack"],
        )
        self.shivDmg = 40
        self.shivTargets = 4
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg + champion.ap.stat * 40
            # only consider dmg to primary target
            for opponent in champion.opponents[0 : self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg, "magical", time)
        return 0


class Flickerblade(Item):
    def __init__(self):
        super().__init__("Flickerblade", aspd=15, ap=10, phases=["postAttack"])
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        self.counter += 1
        if champion.aspd.stat <= 5:
            champion.aspd.addStat(7)
        if self.counter == 5:
            champion.bonus_ad.addStat(4)
            champion.ap.addStat(5)
            self.counter = 0
        return 0


### RADIANTS


class RadiantSteraksGage(Item):
    def __init__(self):
        super().__init__(
            "Radiant Sterak's Gage",
            ad=80,
            hp=600,
            has_radiant=True,
            phases=None,
        )


class RadiantStrikersFlail(Item):
    def __init__(self):
        super().__init__(
            "Radiant Strikers' Flail",
            crit=35,
            aspd=35,
            hp=150,
            dmgMultiplier=0.2,
            has_radiant=True,
            phases=["preCombat", "onCrit"],
        )
        self.current_buff = 0
        self.buff_duration = 8
        self.dmg_amp_value = 0.08

    def performAbility(self, phase, time, champion, input_=0):
        champion.applyStatus(
            status.DmgAmpModifier(
                "RadiantStrikersFlail {} {}".format(id(self), self.current_buff)
            ),
            self,
            time,
            self.buff_duration,
            self.dmg_amp_value,
        )
        self.current_buff = (self.current_buff + 1) % 4
        return 0


class RadiantGuardbreaker(Item):
    def __init__(self):
        super().__init__(
            "Radiant Guardbreaker",
            crit=20,
            ap=30,
            aspd=30,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.5
        return 0


class RadiantShiv(Item):
    def __init__(self):
        super().__init__("Radiant Shiv", ap=50, aspd=20, mana=15, phases=["preAttack"])
        self.shivDmg = 95
        self.shivTargets = 8
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg
            # only consider dmg to primary target
            # champion.doDamage(champion.opponents[0], [], 0, baseDmg, baseDmg,'magical', time)
            for opponent in champion.opponents[0 : self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg, "magical", time)
                opponent.applyStatus(status.MRReduction("MR"), champion, time, 5, 0.7)
        return 0


class RadiantBlue(Item):
    def __init__(self):
        super().__init__(
            "Radiant Blue",
            manaRegen=10,
            ap=60,
            ad=60,
            has_radiant=True,
            phases=None,
        )


class RadiantArchangels(Item):
    def __init__(self):
        super().__init__("Radiant Archangels", manaRegen=2, ap=60, phases=["onUpdate"])
        self.nextAP = 4

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAP:
            champion.ap.add += 40
            self.nextAP += 4
        return 0


class RadiantGuinsoosRageblade(Item):
    def __init__(self):
        super().__init__(
            "Radiant Guinsoo's Rageblade", aspd=30, ap=30, phases=["onUpdate"]
        )
        self.next_bonus = 1
        self.aspd_bonus = 14

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            if champion.aspd.stat <= 5:
                champion.aspd.add += self.aspd_bonus
            self.next_bonus += 1
        return 0


class RadiantKrakensFury(Item):
    def __init__(self):
        super().__init__(
            "Radiant Kraken's Fury",
            aspd=25,
            ad=30,
            has_radiant=True,
            phases="preAttack",
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(6)
        return 0


class RadiantHoJ(Item):
    def __init__(self):
        super().__init__(
            "Radiant HoJ",
            manaRegen=2,
            crit=40,
            ad=70,
            ap=70,
            omnivamp=0.20,
            phases=None,
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class RadiantLastWhisper(Item):
    def __init__(self):
        super().__init__("Radiant LW", aspd=25, crit=55, ad=45, phases=["preAttack"])

    def performAbility(self, phase, time, champion, opponents):
        # NOTE: LW usually applies AFTER attack but we want to calculate w/ reduced armor
        for opponent in champion.opponents:
            opponent.armor.mult = 0.7
        return 0


class RadiantGS(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Radiant GS", aspd=10, ad=50, ap=50, phases="preCombat")

    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        champion.dmgMultiplier.add += 0.2
        if len(champion.opponents) > 0:
            vsGiants = champion.opponents[0].hp.stat >= 1750
            if vsGiants:
                champion.dmgMultiplier.add += 0.3
        return 0


class RadiantRabadons(Item):
    def __init__(self):
        super().__init__("Radiant Rab", ap=80, dmgMultiplier=0.5, phases=None)


class RadiantJeweledGauntlet(Item):
    def __init__(self):
        super().__init__("Radiant JG", crit=75, ap=70, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0


class RadiantNashors(Item):
    def __init__(self):
        super().__init__(
            "Radiant Nashor's",
            manaRegen=3,
            aspd=20,
            ap=30,
            hp=200,
            phases=["postAbility", "onUpdate"],
        )
        self.active = False
        self.wearoffTime = 9999
        self.duration = 8
        self.aspdBoost = 75
        # we just dont treat it as a sttus

    def performAbility(self, phase, time, champion, input_=0):
        self.duration = champion.castTime + self.duration  # add cast time
        if phase == "postAbility":
            if not self.active:
                # if not active, give the AS bonus
                champion.aspd.addStat(self.aspdBoost)
            self.active = True
            self.wearoffTime = time + self.duration
        elif phase == "onUpdate":
            if time > self.wearoffTime and self.active:
                # wearing off
                self.active = False
                champion.aspd.addStat(self.aspdBoost * -1)
        return 0


class RadiantShojin(Item):
    def __init__(self):
        super().__init__(
            "Radiant Spear of Shojin",
            ad=40,
            manaRegen=2,
            ap=30,
            phases=["preCombat"],
        )
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(10)
        return 0


class RadiantVoidStaff(Item):
    def __init__(self):
        super().__init__(
            "Radiant Void Staff",
            manaRegen=2,
            ap=60,
            aspd=60,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.mr.mult = 0.7
        return 0


class RadiantInfinityEdge(Item):
    def __init__(self):
        super().__init__(
            "Radiant InfinityEdge", ad=70, crit=75, phases=["postPreCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True
        return 0


class RadiantDeathblade(Item):
    def __init__(self):
        super().__init__("Radiant DB", ad=105, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.2
        return 0


class RadiantQSS(Item):
    def __init__(self):
        super().__init__("Radiant Quicksilver", aspd=50, crit=20, phases="onUpdate")
        self.nextAS = 2
        self.asGain = 9
        self.procs_left = 7

    def performAbility(self, phase, time, champion, input_=0):
        if time >= self.nextAS and self.procs_left > 0:
            champion.aspd.addStat(self.asGain)
            self.nextAS += 2
            self.procs_left -= 1
        return 0


class RadiantRed(Item):
    def __init__(self):
        super().__init__("Radiant Red (no burn yet)", aspd=60, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.1
        # champion.critDmg.add += 0.1
        return 0


class RadiantMorellos(Item):
    def __init__(self):
        super().__init__(
            "RadiantMorellos (no burn yet)",
            manaRegen=4,
            aspd=25,
            ap=50,
            hp=150,
            phases=None,
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class RadiantAdaptive(Item):
    def __init__(self):
        super().__init__(
            "Radiant Adaptive Helm",
            manaRegen=5,
            ad=30,
            ap=55,
            phases=["preCombat"],
        )
        self.mult = 0.4

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaGainMultiplier.addStat(self.mult)
        return 0


class RadiantTitans(Item):
    def __init__(self):
        super().__init__("Radiant Titans", aspd=30, armor=35, phases="preAttack")
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 25:
            champion.bonus_ad.addStat(3)
            champion.ap.addStat(3)
        self.stacks += 1
        if self.stacks == 25:
            champion.armor.addStat(50)
            champion.mr.addStat(50)
        return 0
