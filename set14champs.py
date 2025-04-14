from champion import Champion, Stat, Attack
from collections import deque
import math
import numpy as np
import heapq
import random
import set14buffs as buffs
import status

champ_list = ['Kogmaw', 'Kindred', 'Nidalee', 'Seraphine', 'Shaco', 'Zyra',
              'Jhin', 'Leblanc', 'Senna', 'TwistedFate', 'Vayne', 'Veigar',
              'Draven', 'Elise', 'Jinx', 'Varus', 'Yuumi',
              'Annie', 'Aphelios', 'Brand', 'MissFortune', 'Vex', 'Xayah', 'Zeri', 'Ziggs']


class Kogmaw(Champion):
    canFourStar = True
    def __init__(self, level):
        hp = 500
        atk = 50
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Kogmaw', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Boombot', 'Rapidfire']
        self.buff_duration = 5
        self.manalockDuration = 5
        self.aspd_bonus = [50, 50, 50, 50]
        self.items = [buffs.KogUlt()]
        self.castTime = 0

        self.ultActive = False
        self.notes = "Boombot not yet coded, need to figure out interaction with runaans/shiv"

    def abilityScaling(self, level, AD, AP):
        adScale = [.4, .4, .4, .4]
        apScale = [9, 14, 20, 26]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.ASModifier("Kogmaw"),
                         self, time, self.buff_duration, self.aspd_bonus[self.level-1])
        self.applyStatus(status.UltActivator("Kog ult"),
                         self, time, self.buff_duration)


class Kindred(Champion):
    canFourStar = True
    def __init__(self, level):
        hp= 500
        atk = 48
        curMana = 0
        fullMana = 50
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Kindred', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Rapidfire', 'Marksman']
        self.castTime = 1.5

    def abilityScaling(self, level, AD, AP):
        adScale = [5.2, 5.2, 5.2, 5.2]
        apScale = [20, 30, 45, 60]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', 1)


class Shaco(Champion):
    canFourStar = True
    def __init__(self, level):
        hp= 600
        atk = 55
        curMana = 0
        fullMana = 50
        aspd = .8
        armor = 40
        mr = 40
        super().__init__('Shaco', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Slayer']
        self.castTime = 1
        self.notes = "Just using for ranged investigation"

    def abilityScaling(self, level, AD, AP):
        adScale = [2.75, 2.75, 2.75]
        apScale = [40, 60, 90, 120]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', 1)


class Nidalee(Champion):
    def __init__(self, level):
        hp = 650
        atk = 40
        curMana = 20
        fullMana = 60
        aspd = .75
        armor = 40
        mr = 40
        super().__init__('Nidalee', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AMP']
        self.amp_level = 0
        self.castTime = 1
        self.notes = "Melee; add scoped / rfc"
        self.ultActive = False

    def abilityScaling(self, level, AD, AP):
        apScale = [200, 300, 455]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [75, 115, 170]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling, 'magical')

        num_targets = 2 + self.amp_level
        self.multiTargetSpell(opponents, items,
                              time, num_targets, self.extraAbilityScaling, 'magical')


class Seraphine(Champion):
    canFourStar = True
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 0
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Seraphine', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Techie']
        self.castTime = 1
        self.num_targets = 3

    def abilityScaling(self, level, AD, AP):
        apScale = [250, 375, 585, 795]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            self.multiTargetSpell(opponents, items, time, 1,
                                  lambda x, y, z: .65**(count) * self.abilityScaling(x, y, z), 'magical')


class Zyra(Champion):
    canFourStar = True
    def __init__(self, level):
        hp= 500
        atk = 30
        curMana = 0
        fullMana = 60
        aspd = .7
        armor = 15
        mr = 15
        super().__init__('Zyra', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Techie']
        self.castTime = 1

    def abilityScaling(self, level, AD, AP):
        apScale = [260, 390, 600, 810]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [130, 195, 300, 405]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 1, self.extraAbilityScaling, 'magical')


class Jhin(Champion):
    def __init__(self, level):
        hp= 550
        atk = 44
        curMana = 14
        fullMana = 74
        aspd = .74
        armor = 20
        mr = 20
        super().__init__('Jhin', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Exotech', 'Marksman', 'Dynamo']
        self.castTime = 1

    def abilityScaling(self, level, AD, AP):
        adScale = [1.74, 1.74, 1.74]
        return adScale[level - 1] * AD

    def fourthAbilityScaling(self, level, AD, AP):
        adScale = [4.44, 4.44, 4.44]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for index in range(3):
            self.multiTargetSpell(opponents[index:], items,
                                  time, 1,
                                  self.abilityScaling,
                                  'physical')
            opponents[index].applyStatus(status.ArmorReduction("Armor Jhin"), self, time, 4.4 * self.ap.stat, .8)
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.fourthAbilityScaling,
                              'physical', 1)            


class Leblanc(Champion):
    def __init__(self, level):
        hp = 550
        atk = 40
        curMana = 0
        fullMana = 50
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Leblanc', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cypher', 'Strategist']
        self.castTime = 1
        self.sigils = 5
        self.notes = "Cast time doesnt increase with more sigils"

    def abilityScaling(self, level, AD, AP):
        apScale = [65, 95, 145]
        return apScale[level - 1] * AP * self.sigils

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, 1, self.abilityScaling, 'magical')
        self.sigils += 1


class TwistedFate(Champion):
    def __init__(self, level):
        hp = 600
        atk = 35
        curMana = 10
        fullMana = 70
        aspd = .75
        armor = 20
        mr = 20
        super().__init__('Twisted Fate', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.is_kingpin = False
        self.default_traits = ['Syndicate', 'Rapidfire']
        self.items = [buffs.TFUlt()]
        self.castTime = 1
        self.num_targets = 2
        self.notes = "kingpin alternates red and blue; targets is for red card. syndicate 7 not in yet"
        self.red_card = True

    def abilityScaling(self, level, AD, AP):
        apScale = [160, 240, 375]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [260, 390, 610]
        mult = 1 if self.red_card else 0.5
        return apScale[level - 1] * AP * mult

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 2, self.abilityScaling, 'magical', 1)

        if self.is_kingpin:
            if self.red_card:
                self.multiTargetSpell(opponents, items,
                                      time, self.num_targets,
                                      self.extraAbilityScaling,
                                      'magical')
                self.red_card = False
            else:    
                self.multiTargetSpell(opponents, items,
                                      time, 1,
                                      self.extraAbilityScaling,
                                      'magical')
                self.multiTargetSpell(opponents, items,
                                      time, 1,
                                      self.extraAbilityScaling,
                                      'true')
                self.red_card = True


class Vayne(Champion):
    def __init__(self, level):
        hp = 550
        atk = 50
        curMana = 40
        fullMana = 80
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Vayne', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Slayer']
        self.items = [buffs.VayneUlt()]
        self.ultAutos = 0
        self.manalockDuration = 15
        self.castTime = 0
        self.notes = "ult gives her 2x as for 3 autos"

    def abilityScaling(self, level, AD, AP):
        adScale = [.5, .5, .5]
        return adScale[level - 1] * AD

    def thirdAbilityScaling(self, level, AD, AP):
        apScale = [10, 15, 25]
        adScale = [1.6, 1.6, 1.6]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.ultAutos = 3
        self.aspd.mult = 2
        self.aspd.as_cap = 10
        self.nextAttackTime = time + .01


class Veigar(Champion):
    def __init__(self, level):
        hp = 550
        atk = 35
        curMana = 0
        fullMana = 40
        aspd = .7
        armor = 20
        mr = 20
        super().__init__('Veigar', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cyberboss', 'Techie']
        self.cyberboss_upgrade = False
        self.castTime = 1
        self.num_targets = 2
        self.true_bonus = .4 if self.level == 3 else .25
        self.notes = "Does 40% true dmg if 3*, 25\% otherwise"

    def abilityScaling(self, level, AD, AP):
        apScale = [320, 420, 560]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [125, 170, 240]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                              time, 1, lambda x, y, z: self.true_bonus * self.abilityScaling(x, y, z), 'true')
        if self.cyberboss_upgrade:
            if self.num_targets > 1: 
                self.multiTargetSpell(opponents, items,
                                      time, self.num_targets - 1, self.extraAbilityScaling, 'magical')
                self.multiTargetSpell(opponents, items,
                                      time, self.num_targets - 1, lambda x, y, z: self.true_bonus * self.extraAbilityScaling(x, y, z), 'true')


class Draven(Champion):
    # unconfirmed: is spell 1 auto or 0
    def __init__(self, level):
        hp = 700
        atk = 53
        curMana = 30
        fullMana = 120
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Draven', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cypher', 'Rapidfire']
        self.castTime = 1
        self.num_targets = 3
        self.dmg_falloff = .8
        self.notes = "Draven will hit each target twice"

    def abilityScaling(self, level, AD, AP):
        adScale = [3.7, 3.7, 3.9]
        apScale = [30, 45, 80]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets * 2):
            # technically this is just hitting the 1st guy X times so we'll change it if it matters
            num_attacks = 1 if count == 0 else 0
            self.multiTargetSpell(opponents, items, time, 1,
                                  lambda x, y, z: self.dmg_falloff**(count) * self.abilityScaling(x, y, z), 'physical', num_attacks)


class Senna(Champion):
    def __init__(self, level):
        hp= 700
        atk = 85
        curMana = 0
        fullMana = 100
        aspd = .6
        armor = 25
        mr = 25
        super().__init__('Senna', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Divinicorp', 'Slayer']
        self.castTime = 2
        self.num_targets = 2
        self.items = [buffs.SennaUlt()]
        self.notes = "Passive will hit 1 other target. passive doesnt need ie to crit"

    def autoScaling(self, level, AD, AP):
        adScale = [.4, .4, .4]
        return adScale[level - 1] * AD

    def abilityScaling(self, level, AD, AP):
        adScale = [2.8, 2.8, 3]
        apScale = [20, 30, 45]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, self.num_targets,
                              self.abilityScaling,
                              'physical', 1)


class Jinx(Champion):
    def __init__(self, level):
        hp = 650
        atk = 55
        curMana = 0
        fullMana = 50
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Jinx', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Marksman']
        self.castTime = 2
        self.rockets = 5
        self.notes = "Cast time should slightly increase over time, not implemented yet."

    def abilityScaling(self, level, AD, AP):
        adScale = [1.4, 1.4, 1.5]
        apScale = [15, 25, 40]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.rockets

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', self.rockets // 2)
        self.rockets += 1


class Elise(Champion):
    def __init__(self, level):
        hp = 700
        atk = 40
        curMana = 0
        fullMana = 55
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Elise', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Dynamo']
        self.castTime = 1
        self.notes = "Does not include the flat MR reduction!"

    def abilityScaling(self, level, AD, AP):
        apScale = [54, 81, 125]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        # 8 lasers
        self.multiTargetSpell(opponents, items,
                              time, 4,
                              self.abilityScaling,
                              'magical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 4,
                              self.abilityScaling,
                              'magical', 1)
        


class Varus(Champion):
    def __init__(self, level):
        hp= 700
        atk = 35
        curMana = 15
        fullMana = 75
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Varus', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Exotech', 'Executioner']
        self.castTime = 1


    def abilityScaling(self, level, AD, AP):
        apScale = [200, 300, 480]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [100, 150, 240]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'magical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 3,
                              self.abilityScaling,
                              'magical', 1)


class Aphelios(Champion):
    def __init__(self, level):
        hp= 800
        atk = 63
        curMana = 0
        fullMana = 60
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Aphelios', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['GoldenOx', 'Marksman']
        self.items = [buffs.ApheliosUlt()]
        self.num_targets = 4
        self.ultAutos = 0
        self.base_chakrams = 4
        self.chakrams = 0
        self.manalockDuration = 999
        self.castTime = 1
        self.notes = "Ox force not coded in yet, use glass cannon instead"

    def abilityScaling(self, level, AD, AP):
        apScale = [20, 30, 100]
        adScale = [2.2, 2.2, 5]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def chakramAbilityScaling(self, level, AD, AP):
        adScale = [.07, .07, .2]
        return adScale[level - 1] * AD * self.chakrams

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, self.num_targets,
                              self.abilityScaling,
                              'physical', 1)
        self.chakrams = self.base_chakrams + self.num_targets
        self.ultAutos = 6


class Xayah(Champion):
    # TODO: How many autos is her ult?
    def __init__(self, level):
        hp = 800
        atk = 60
        curMana = 25
        fullMana = 75
        aspd = .8
        armor = 30
        mr = 30
        super().__init__('Xayah', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'Marksman']
        self.castTime = 2
        self.num_feathers = 6
        self.notes = "Feathers are instant, will apply on same target"

    def abilityScaling(self, level, AD, AP):
        apScale = [20, 30, 200]
        adScale = [1.5, 1.5, 4]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.num_feathers

    def extraAbilityScaling(self, level, AD, AP):
        adScale = [.35, .35, 1]
        return adScale[level - 1] * AD * self.num_feathers

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.abilityScaling,
                              'physical', 1)
        self.multiTargetSpell(opponents, items,
                              time, 1,
                              self.extraAbilityScaling,
                              'physical', 1)


class Zeri(Champion):
    def __init__(self, level):
        hp= 800
        atk = 65
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Zeri', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Exotech', 'Rapidfire']
        self.castTime = .2
        self.items = [buffs.ZeriUlt()]
        self.queued_autos = []
        self.duration = [5, 5, 10]

    def abilityScaling(self, level, AD, AP):
        adScale = [.4, .4, 2]
        return adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        heapq.heappush(self.queued_autos,
                       (time, (self.atk.stat, self.aspd.stat,
                       time + self.duration[self.level - 1] * self.ap.stat,
                       time)))
        return 0


class MissFortune(Champion):
    def __init__(self, level):
        hp= 700
        atk = 50
        curMana = 50
        fullMana = 150
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Miss Fortune', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Syndicate', 'Dynamo']
        self.is_kingpin = False

        self.castTime = 2.2 # this is probably lower without syndicate
        self.num_targets_fixed = 4 # no need for customization
        # self.num_bullets = 8
        self.dmg_falloff = .75
        self.notes = "8 bullets in each wave, assume every bullet hits. \
                      fixed at 4 targets, each getting hit by 2 bullets. no 7 syndicate yet"

    def abilityScaling(self, level, AD, AP):
        adScale = [.5, .5, 1.35]
        apScale = [8, 12, 100]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        num_waves = 12 if self.is_kingpin else 8
        for wave in range(num_waves):
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets_fixed,
                                  self.abilityScaling,
                                  'physical', 1)
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets_fixed,
                                  lambda x, y, z: self.dmg_falloff * self.abilityScaling(x, y, z),
                                  'physical', 1)


class Annie(Champion):
    def __init__(self, level):
        hp= 850
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Annie', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Golden Ox', 'AMP']
        self.amp_level = 0  # amp_level gets modified by AMP
        self.castTime = 1
        self.num_targets = 2
        self.notes = "# targets is for tibbers; doesn't account for tibbers' dmg so don't trust this at all"

    def abilityScaling(self, level, AD, AP):
        apScale = [210, 315, 1200]
        return apScale[level - 1] * AP

    def fireballAbilityScaling(self, level, AD, AP):
        apScale = [30, 45, 240]
        return apScale[level - 1] * AP

    def tibbersAbilityScaling(self, level, AD, AP):
        apScale = [270, 405, 1215]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        if self.numCasts % 4 == 0:
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets,
                                  self.tibbersAbilityScaling, 'magical')
        else:
            self.multiTargetSpell(opponents, items,
                                  time, 1, self.abilityScaling,
                                  'magical')
            self.multiTargetSpell(opponents, items,
                                  time, self.amp_level + 2,
                                  self.fireballAbilityScaling, 'magical')

class Brand(Champion):
    def __init__(self, level):
        hp= 800
        atk = 35
        curMana = 25
        fullMana = 70
        aspd = .7
        armor = 30
        mr = 30
        super().__init__('Brand', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['StreetDemon', 'Techie']
        self.castTime = 2
        self.num_targets = 3

    def abilityScaling(self, level, AD, AP):
        apScale = [260, 390, 1500]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [80, 120, 600]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                time, self.num_targets, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                time, 4, self.abilityScaling, 'magical')

class Yuumi(Champion):
    def __init__(self, level):
        hp= 650
        atk = 35
        curMana = 0
        fullMana = 30
        aspd = .75
        armor = 25
        mr = 25
        super().__init__('Yuumi', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['AnimaSquad', 'AMP', 'Strategist']
        self.items.append(buffs.YuumiUlt())
        self.amp_level = 0
        self.castTime = 1
        self.marked = False
        self.notes = "Every other cast will be marked"

    def abilityScaling(self, level, AD, AP):
        mult = 1.75 if self.marked else 1
        apScale = [95, 145, 220]
        return apScale[level - 1] * AP * mult

    def secondaryAbilityScaling(self, level, AD, AP):
        mult = 1.75 if self.marked else 1
        apScale = [55, 85, 125]
        return apScale[level - 1] * AP * mult

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling, 'magical')
        self.multiTargetSpell(opponents, items,
                              time, 1, self.secondaryAbilityScaling, 'magical')
        self.marked = not self.marked


class Vex(Champion):
    def __init__(self, level):
        hp = 800
        atk = 30
        curMana = 0
        fullMana = 30
        aspd = .8
        armor = 30
        mr = 30
        super().__init__('Vex', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Divinicorp', 'Executioner']
        self.items = [buffs.VexUlt()]
        self.omnivamp.addStat(.15)
        self.castTime = 1
        self.num_targets = 2
        self.convert_true = False
        self.notes = "Always overheals; gunblade ally healing doesn't overheal."

    def abilityScaling(self, level, AD, AP):
        apScale = [190, 285, 1100]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [100, 150, 600]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.convert_true = True
        self.multiTargetSpell(opponents, items,
                              time, 1, self.abilityScaling, 'magical')
        if self.num_targets > 1:
            self.multiTargetSpell(opponents, items,
                                  time, self.num_targets - 1,
                                  self.extraAbilityScaling, 'magical')
        self.convert_true = False


class Ziggs(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 20
        fullMana = 70
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Ziggs', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.default_traits = ['Cyberboss', 'Strategist']
        self.cyberboss_upgrade = False
        self.castTime = 1
        self.num_targets = 3
        self.num_extra_targets = 2
        self.notes = "Num targets is for center, extra targets is for further away"

    def abilityScaling(self, level, AD, AP):
        apScale = [250, 375, 1500]
        return apScale[level - 1] * AP

    def extraAbilityScaling(self, level, AD, AP):
        apScale = [130, 200, 900]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items,
                              time, self.num_targets,
                              self.abilityScaling, 'magical')
        if self.cyberboss_upgrade:
            self.multiTargetSpell(opponents, items,
                                  time, self.num_extra_targets,
                                  self.extraAbilityScaling, 'magical')


class ZeroResistance(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 0
        mr = 0
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def performAbility(self, opponents, items, time):
        return 0


class DummyTank(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 100
        mr = 100
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def performAbility(self, opponents, items, time):
        return 0


class SuperDummyTank(Champion):
    def __init__(self, level):
        hp = 2000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 200
        mr = 200
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5
        
    def performAbility(self, opponents, items, time):
        return 0

