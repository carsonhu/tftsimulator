from item import Item
from role import Role

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
    "EdgeOfNight",
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
    "Dawncore",
    "TitanicHydra",
    "CrownOfDemacia",
    "DarkinStaff",
    "CappaJuice"
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

emblems = [
    "VanquisherEmblem",
    "QuickstrikerEmblem",
    "YordleEmblem",
    "LongshotEmblem",
    "ZaunEmblem",
    "BilgewaterEmblem",
    "GunslingerEmblem",
    "DemaciaEmblem",
    "SlayerEmblem",
    "IoniaEmblem",
    "NoxusEmblem",
    "ArcanistEmblem",
    "VoidEmblem",
]

no_item = ["NoItem"]


class Emblem(Item):
    display_name = "Emblem"

    def __init__(self, display_name, trait, **kwargs):
        super().__init__(display_name, **kwargs)
        self.trait = trait


class VanquisherEmblem(Emblem):
    display_name = "Vanquisher Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Vanquisher", ad=15, ap=15, crit=20, phases=None
        )


class QuickstrikerEmblem(Emblem):
    display_name = "Quickstriker Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Quickstriker", aspd=25, phases=None
        )


class YordleEmblem(Emblem):
    display_name = "Yordle Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Yordle", ad=20, ap=20, phases=None
        )


class LongshotEmblem(Emblem):
    display_name = "Longshot Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Longshot", hp=150, aspd=20, phases=None
        )


class ZaunEmblem(Emblem):
    display_name = "Zaun Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Zaun", hp=350, crit=20, phases=None
        )


class BilgewaterEmblem(Emblem):
    display_name = "Bilgewater Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Bilgewater", ad=10, ap=10, mana=2, phases=None
        )


class GunslingerEmblem(Emblem):
    display_name = "Gunslinger Emblem (no Armor reduce)"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Gunslinger", hp=150, ad=20, phases=None
        )


class DemaciaEmblem(Emblem):
    display_name = "Demacia Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Demacia", manaRegen=3, phases=None
        )


class SlayerEmblem(Emblem):
    display_name = "Slayer Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Slayer", ad=20, phases=None
        )


class IoniaEmblem(Emblem):
    display_name = "Ionia Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Ionia", ad=25, ap=25, phases=None
        )


class NoxusEmblem(Emblem):
    display_name = "Noxus Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Noxus", ad=25, ap=25, phases=None
        )


class ArcanistEmblem(Emblem):
    display_name = "Arcanist Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Arcanist", ap=25, phases=None
        )


class VoidEmblem(Emblem):
    display_name = "Void Emblem"

    def __init__(self):
        super().__init__(
            self.display_name, trait="Void", ad=10, ap=10, aspd=20, phases=None
        )


class NoItem(Item):
    display_name = "NoItem"

    def __init__(self):
        super().__init__(self.display_name, phases=None)


class Rabadons(Item):
    display_name = "Rabadon's Deathcap"

    def __init__(self):
        super().__init__(
            self.display_name,
            ap=50,
            dmgMultiplier=0.15,
            has_radiant=True,
            phases=None,
        )


class Bloodthirster(Item):
    display_name = "Bloodthirster"

    def __init__(self):
        super().__init__(self.display_name, ad=20, ap=20, omnivamp=0.20, phases=None)


class EdgeOfNight(Item):
    display_name = "Edge of Night"

    def __init__(self):
        super().__init__(self.display_name, ad=10, ap=10, aspd=15, phases=None)


class HextechGunblade(Item):
    display_name = "Gunblade"

    def __init__(self):
        super().__init__(
            self.display_name, ad=20, ap=20, manaRegen=1, omnivamp=0.15, phases=None
        )


class GuinsoosRageblade(Item):
    display_name = "Guinsoo's Rageblade"

    def __init__(self):
        super().__init__(
            self.display_name,
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


class CrownOfDemacia(Item):
    display_name = "Crown of Demacia"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=30,
            hp=300,
            phases=["onUpdate"],
        )
        self.next_bonus = 2
        self.scaling = 10

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            champion.bonus_ad.addStat(self.scaling)
            champion.ap.addStat(self.scaling)
            self.next_bonus += 2


class Archangels(Item):
    display_name = "Archangels"

    def __init__(self):
        super().__init__(
            self.display_name,
            manaRegen=1,
            ap=30,
            has_radiant=True,
            phases=["onUpdate"],
        )
        self.nextAP = 5
        self.ap_per_interval = 20
        self.seraphimActivated = False

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.nextAP:
            champion.ap.addStat(self.ap_per_interval)
            self.nextAP += 5

        if champion.seraphim and not self.seraphimActivated and champion.ap.stat >= 1.9:
            self.seraphimActivated = True
            champion.manaRegen.addStat(2)


class VoidStaff(Item):
    display_name = "Void Staff"

    def __init__(self):
        super().__init__(
            self.display_name,
            manaRegen=1,
            ap=35,
            aspd=15,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.mr.mult = 0.7


class Warmogs(Item):
    display_name = "Warmogs"

    def __init__(self):
        super().__init__(self.display_name, hp=1000, phases=None)


class HoJ(Item):
    display_name = "Hand of Justice"

    def __init__(self):
        super().__init__(
            self.display_name,
            manaRegen=1,
            crit=20,
            ad=30,
            ap=30,
            omnivamp=0.12,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.retribution:
            champion.canSpellCrit = True


class TacticiansCrown(Item):
    display_name = "Tacticians' Crown (Coronation)"

    def __init__(self):
        super().__init__(self.display_name, aspd=20, ad=25, ap=30, phases=None)


class StrikersFlail(Item):
    display_name = "StrikersFlail"

    def __init__(self):
        super().__init__(
            self.display_name,
            crit=20,
            hp=150,
            aspd=10,
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


class Guardbreaker(Item):
    display_name = "Guardbreaker"

    def __init__(self):
        super().__init__(
            self.display_name,
            crit=20,
            ap=10,
            hp=150,
            aspd=20,
            has_radiant=True,
            phases=["preCombat"],
        )
        self.dmg_amp = 0.25

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += self.dmg_amp


class GuardbreakerNoGuard(Item):
    display_name = "Guardbreaker (no shield)"

    def __init__(self):
        super().__init__(
            self.display_name,
            crit=20,
            hp=150,
            ap=10,
            aspd=20,
            has_radiant=True,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.add += 0.1


class InfinityEdge(Item):
    display_name = "Infinity Edge"

    def __init__(self):
        super().__init__(
            self.display_name,
            ad=35,
            crit=35,
            has_radiant=True,
            phases=["postPreCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True


class LastWhisper(Item):
    display_name = "Last Whisper"

    def __init__(self):
        super().__init__(
            self.display_name,
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


class Shojin(Item):
    display_name = "Spear of Shojin"

    def __init__(self):
        super().__init__(
            self.display_name,
            ad=15,
            manaRegen=1,
            ap=15,
            has_radiant=True,
            phases=["preCombat"],
        )
        self.mana_per_attack = 5

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaPerAttack.addStat(self.mana_per_attack)


class Titans(Item):
    display_name = "Titan's Resolve"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=10,
            armor=20,
            has_radiant=True,
            phases="preAttack",
        )
        self.stacks = 0
        self.stack_bonus = 2
        self.max_stack_bonus = 0.1

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 25:
            champion.bonus_ad.addStat(self.stack_bonus)
            champion.ap.addStat(self.stack_bonus)
        self.stacks += 1
        if self.stacks == 25:
            champion.dmgMultiplier.addStat(self.max_stack_bonus)


class Nashors(Item):
    display_name = "Nashor's Tooth"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=10,
            hp=150,
            ap=15,
            manaRegen=0,
            crit=20,
            has_radiant=True,
            phases=["preCombat", "onCrit", "postAttack"],
        )
        self.manaBonus = 2
        self.manaCritBonus = 2
        self.isActive = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.manaPerAttack.addStat(self.manaBonus)
        elif phase == "onCrit" and not input_ and not self.isActive:
            # input is: is spell or not spell
            # definitely want to watch for this, as it might be rly bad
            self.isActive = True
            champion.manaPerAttack.addStat(self.manaCritBonus)
        elif phase == "postAttack" and self.isActive:
            champion.manaPerAttack.addStat(-1 * self.manaCritBonus)
            self.isActive = False


class Adaptive(Item):
    display_name = "Adaptive Helm"

    def __init__(self):
        super().__init__(
            self.display_name,
            manaRegen=3,
            ad=10,
            ap=10,
            has_radiant=True,
            phases=["preCombat"],
        )
        self.mult = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaGainMultiplier.addStat(0.15)


class KrakensFury(Item):
    display_name = "Kraken's Fury"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=10,
            ad=10,
            mr=20,
            has_radiant=True,
            phases="preAttack",
        )
        self.stacks = 0
        self.maxStacks = 15
        self.adPerStack = 3.5
        self.max_stack_as = 15

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < self.maxStacks:
            self.stacks += 1
            champion.bonus_ad.addStat(self.adPerStack)
        elif self.stacks == self.maxStacks:
            champion.aspd.addStat(self.max_stack_as)
            self.stacks += 1


class Deathblade(Item):
    display_name = "Deathblade"

    def __init__(self):
        super().__init__(self.display_name, ad=55, dmgMultiplier=0.1, has_radiant=True, phases=None)


class SteraksGage(Item):
    display_name = "Sterak's Gage"

    def __init__(self):
        super().__init__(
            self.display_name, ad=40, hp=300, has_radiant=True, phases=None
        )


class QSS(Item):
    display_name = "Quicksilver"

    def __init__(self):
        super().__init__(self.display_name, aspd=15, crit=20, mr=20, phases="onUpdate")
        self.nextAS = 1
        self.asGain = 3

    def performAbility(self, phase, time, champion, input_=0):
        if time >= self.nextAS:
            champion.aspd.addStat(self.asGain)
            self.nextAS += 1


class JeweledGauntlet(Item):
    display_name = "Jeweled Gauntlet"

    def __init__(self):
        super().__init__(
            self.display_name,
            crit=35,
            ap=35,
            has_radiant=True,
            phases=["postPreCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.canSpellCrit:
            champion.critDmg.add += 0.1
        champion.canSpellCrit = True


class Red(Item):
    display_name = "Red (no burn)"

    def __init__(self):
        super().__init__(self.display_name, aspd=45, dmgMultiplier=0.06, phases=None)


class Morellos(Item):
    display_name = "Morellos (no burn)"

    def __init__(self):
        super().__init__(self.display_name, ap=20, manaRegen=1, hp=150, phases=None)


class Shiv(Item):
    display_name = "Statikk Shiv"

    def __init__(self):
        super().__init__(
            self.display_name,
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


class GS(Item):
    # needs reworking
    display_name = "Giant Slayer"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=15,
            ad=15,
            ap=15,
            has_radiant=True,
            phases="preCombat",
        )
        self.base_amp = 0.15
        self.giant_amp = 0.15

    def is_giant(self, target):
        return target.role == Role.TANK

    def performAbility(self, phase, time, champion, input_):
        # input_ is target
        champion.dmgMultiplier.add += self.base_amp
        if len(champion.opponents) > 0:
            vsGiants = self.is_giant(champion.opponents[0])
            if vsGiants:
                champion.dmgMultiplier.add += self.giant_amp


class GSNoGiant(Item):
    # needs reworking
    display_name = "Giant Slayer (no Giant)"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=15,
            ad=20,
            ap=20,
            has_radiant=True,
            phases="preCombat",
        )

    def performAbility(self, phase, time, champion, input_):
        champion.dmgMultiplier.add += 0.15


class Bramble(Item):
    display_name = "Bramble Vest"

    def __init__(self):
        super().__init__(self.display_name, armor=55, phases=None)


class Blue(Item):
    display_name = "Blue Buff"

    def __init__(self):
        super().__init__(
            self.display_name,
            manaRegen=5,
            ap=15,
            ad=15,
            has_radiant=True,
            phases="preCombat",
        )
        self.multScaling = 0.1

    def performAbility(self, phase, time, champion, input_):
        champion.ap.addMultiplier += self.multScaling
        champion.bonus_ad.addMultiplier += self.multScaling


### ARTIFACTS


class InfinityForce(Item):
    display_name = "Infinity Force"

    def __init__(self):
        super().__init__(
            self.display_name,
            ad=30,
            ap=30,
            aspd=30,
            hp=300,
            armor=30,
            mr=30,
            item_type="Artifact",
            phases=None,
        )


class Fishbones(Item):
    display_name = "Fishbones"

    def __init__(self):
        super().__init__(self.display_name, aspd=50, ad=50, phases=None)


class CappaJuice(Item):
    display_name = "Cappa Juice"

    def __init__(self):
        super().__init__(
            self.display_name,
            aspd=20,
            ad=25,
            ap=25,
            phases=["preCombat"],
        )
        self.hats = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.hats = champion.takedowns
            if self.hats > 0:
                champion.bonus_ad.addStat(self.hats)
                champion.ap.addStat(self.hats)

class RFC(Item):
    display_name = "Rapid Firecannon"

    def __init__(self):
        super().__init__(self.display_name, aspd=65, dmgMultiplier=.05,  phases=None)


class Mittens(Item):
    display_name = "Mittens"

    def __init__(self):
        super().__init__(self.display_name, aspd=65, dmgMultiplier=.15, phases="preCombat")

    def performAbility(self, phase, time, champion, input_):
        champion.dmgMultiplier.add += 0.15


class GamblersBlade(Item):
    display_name = "Gambler's Blade (30g)"

    def __init__(self):
        super().__init__(self.display_name, aspd=65, ap=10, phases=None)


class GoldCollector(Item):
    display_name = "Gold Collector"

    def __init__(self):
        super().__init__(self.display_name, ad=40, crit=20, phases=None)


class LichBane(Item):
    display_name = "Lich Bane"

    def __init__(self):
        super().__init__(
            self.display_name, ap=30, aspd=30, phases=["preAbility", "preAttack"]
        )
        self.dmg = {2: 240, 3: 320, 4: 450, 5: 525, 6: 600}
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


class TitanicHydra(Item):
    display_name = "Titanic Hydra (2 targets)"

    def __init__(self):
        super().__init__(
            self.display_name, ad=20, aspd=20, hp=300, phases=["preAttack"]
        )
        self.hp_scaling = 0.03
        self.ad_scaling = 0.08

    def performAbility(self, phase, time, champion, input_=0):
        dmg = (
            champion.hp.stat * self.hp_scaling
            + self.ad_scaling * champion.atk.stat * champion.bonus_ad.stat
        )
        for opp in range(2):
            champion.doDamage(
                champion.opponents[opp], [], 0, dmg, dmg, "physical", time
            )


class WitsEnd(Item):
    display_name = "Wit's End"

    def __init__(self):
        super().__init__(self.display_name, aspd=30, mr=30, hp=300, phases="onAttack")
        self.dmg = {2: 42, 3: 60, 4: 75, 5: 90, 6: 100}

    def performAbility(self, phase, time, champion, input_=0):
        baseDmg = self.dmg[champion.stage]
        champion.doDamage(
            champion.opponents[0], [], 0, baseDmg, baseDmg, "magical", time
        )


class ShivArtifact(Item):
    display_name = "Statikk Shiv (Artifact)"

    def __init__(self):
        super().__init__(
            self.display_name,
            ap=50,
            aspd=15,
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
            baseDmg = self.shivDmg + champion.ap.stat * 40
            # only consider dmg to primary target
            for opponent in champion.opponents[0 : self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg, "magical", time)


class Flickerblade(Item):
    display_name = "Flickerblade"

    def __init__(self):
        super().__init__(self.display_name, aspd=12, ap=10, phases=["postAttack"])
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        self.counter += 1
        if champion.aspd.stat <= 5:
            champion.aspd.addStat(5)
        if self.counter == 5:
            champion.bonus_ad.addStat(2)
            champion.ap.addStat(2)
            self.counter = 0


class Dawncore(Item):
    display_name = "Dawncore"

    def __init__(self):
        super().__init__(
            self.display_name, ad=10, ap=10, phases=["preCombat", "postAbility"]
        )
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.fullMana.addStat(-10)
        elif phase == "postAbility":
            if champion.fullMana.stat > 10:
                # we don't want to use mult since we do want it to round.
                champion.fullMana.addStat(-1 * (champion.fullMana.stat // 10))



class DarkinStaff(Item):
    display_name = "Darkin Staff"

    def __init__(self):
        super().__init__(
            self.display_name, manaRegen=1, ap=40, phases=["postAbility"]
        )
        self.manaSpent = 0

    def performAbility(self, phase, time, champion, input_=0):
        if champion.fullMana.stat > 0:
            self.manaSpent += champion.fullMana.stat
            while self.manaSpent >= 20:
                self.manaSpent -= 20
                dmg = 50
                champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)


### RADIANTS


class RadiantSteraksGage(SteraksGage):
    display_name = "Radiant Sterak's Gage"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ad = 80
        self.hp = 600


class RadiantStrikersFlail(StrikersFlail):
    display_name = "Radiant Strikers' Flail"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.crit = 40
        self.aspd = 20
        self.dmgMultiplier = 0.2
        self.buff_duration = 5
        self.dmg_amp_value = 0.1


class RadiantGuardbreaker(Guardbreaker):
    display_name = "Radiant Guardbreaker"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ap = 30
        self.aspd = 30
        self.dmg_amp = 0.5


class RadiantShiv(Shiv):
    display_name = "Radiant Shiv"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ap = 50
        self.aspd = 20
        self.shivDmg = 95
        self.shivTargets = 8


class RadiantBlue(Blue):
    display_name = "Radiant Blue Buff"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 10
        self.ap = 30
        self.ad = 30
        self.multScaling = 0.2


class RadiantArchangels(Archangels):
    display_name = "Radiant Archangels"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 2
        self.ap = 60
        self.ap_per_interval = 40
        self.nextAP = 5


class RadiantGuinsoosRageblade(GuinsoosRageblade):
    display_name = "Radiant Guinsoo's Rageblade"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 20
        self.ap = 20
        self.aspd_bonus = 14


class RadiantKrakensFury(KrakensFury):
    display_name = "Radiant Kraken's Fury"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 20
        self.ad = 20
        self.mr = 40
        self.adPerStack = 7
        self.max_stack_as = 30


class RadiantHoJ(HoJ):
    display_name = "Radiant Hand of Justice"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 2
        self.crit = 40
        self.ad = 60
        self.ap = 60
        self.omnivamp = 0.24


class RadiantLastWhisper(LastWhisper):
    display_name = "Radiant Last Whisper"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 40
        self.crit = 40
        self.ad = 45


class RadiantGS(GS):
    display_name = "Radiant Giant Slayer"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 30
        self.ad = 30
        self.ap = 30
        self.base_amp = 0.3
        self.giant_amp = 0.3

    def is_giant(self, target):
        return target.role == Role.TANK


class RadiantRabadons(Rabadons):
    display_name = "Radiant Rabadon's Deathcap"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ap = 100
        self.dmgMultiplier = 0.3


class RadiantJeweledGauntlet(JeweledGauntlet):
    display_name = "Radiant Jeweled Gauntlet"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.crit = 75
        self.ap = 75


class RadiantNashors(Nashors):
    display_name = "Radiant Nashor's Tooth"

    def __init__(self):
        super().__init__()
        # override stats after Nashors __init__
        self.hp = 300
        self.ap = 30
        self.aspd = 20
        self.crit = 40
        self.manaBonus = 4
        self.manaCritBonus = 4


class RadiantShojin(Shojin):
    display_name = "Radiant Spear of Shojin"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ad = 30
        self.manaRegen = 2
        self.ap = 30
        self.mana_per_attack = 10


class RadiantVoidStaff(VoidStaff):
    display_name = "Radiant Void Staff"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 2
        self.ap = 30
        self.aspd = 75


class RadiantInfinityEdge(InfinityEdge):
    display_name = "Radiant InfinityEdge"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ad = 65
        self.crit = 75


class RadiantDeathblade(Deathblade):
    display_name = "Radiant Deathblade"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.ad = 110
        self.dmgMultiplier = 0.2


class RadiantQSS(QSS):
    display_name = "Radiant Quicksilver"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 30
        self.crit = 40
        self.mr = 40
        self.asGain = 6


class RadiantRed(Red):
    display_name = "Radiant Red (no burn)"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 90
        self.dmgMultiplier = 0.06
        self.phases = None


class RadiantMorellos(Morellos):
    display_name = "RadiantMorellos (no burn)"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 2
        self.ap = 40
        self.hp = 300


class RadiantAdaptive(Adaptive):
    display_name = "Radiant Adaptive Helm"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.manaRegen = 6
        self.ad = 25
        self.ap = 25
        self.mult = 0.3


class RadiantTitans(Titans):
    display_name = "Radiant Titans"

    def __init__(self):
        super().__init__()
        self.name = self.display_name
        self.aspd = 20
        self.armor = 40
        self.stack_bonus = 4
        self.max_stack_bonus = 0.2
