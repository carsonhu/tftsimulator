class Item(object):
    def __init__(self, name, hp=0, ad=0, ap=0, 
                 aspd=0, armor=0, mr=0, crit=0,
                 dodge=0, mana=0, dmgMultiplier=0, omnivamp=0, has_radiant=False, item_type='Craftable', phases=None):
        self.name = name
        self.hp = hp
        self.ad = ad
        self.ap = ap
        self.aspd = aspd
        self.armor = armor
        self.mr = mr
        self.crit = crit
        self.dodge = dodge
        self.mana = mana
        self.dmgMultiplier = dmgMultiplier
        self.omnivamp = omnivamp
        self.has_radiant = has_radiant
        self.phases = phases


    def performAbility(self, phases, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method for {}".format(self.name))       

    def ability(self, phase, time, champion, input_=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def hashFunction(self):
        return (self.name,)

    def __hash__(self):
        return hash(self.hash_function())