from enum import Enum


class Role(Enum):
    ATTACK_FIGHTER = "Attack Fighter"
    ATTACK_TANK = "Attack Tank"
    ATTACK_SPECIALIST = "Attack Specialist"
    ATTACK_ASSASSIN = "Attack Assassin"
    ATTACK_MARKSMAN = "Attack Marksman"
    ATTACK_CASTER = "Attack Caster"
    MAGIC_SPECIALIST = "Magic Specialist"
    MAGIC_TANK = "Magic Tank"
    MAGIC_CASTER = "Magic Caster"
    MAGIC_ASSASSIN = "Magic Assassin"
    MAGIC_MARKSMAN = "Magic Marksman"
    MAGIC_FIGHTER = "Magic Fighter"
    HYBRID_FIGHTER = "Hybrid Fighter"

    @property
    def is_magic(self):
        return self.value.startswith("Magic")

    @property
    def is_attack(self):
        return self.value.startswith("Attack")

    @property
    def archetype(self):
        return self.value.split()[-1]
