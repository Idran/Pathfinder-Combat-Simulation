class Weapon:
    """Weapon data structure"""

    def __init__(self, name=None, group=[], atk_type="M", atk_damage=[1,8], range=5, crit_range=20, crit_mult=2, weap_bon=0, reach=False):
        self.name = name
        self.group = group
        self.atk_type = atk_type
        self.atk_damage = atk_damage
        self.range = range
        self.crit_range = crit_range
        self.crit_mult = crit_mult
        self.weap_bon = weap_bon
        self.reach = reach

class Armor:
    """Armor data structure"""

    def __init__(self, name=None, type="Light", armor_bon=0, shield_bon=0, max_dex=99, asf=0, armor_check=0):
        self.name = name
        self.type = type
        self.armor_bon = armor_bon
        self.shield_bon = shield_bon
        self.max_dex = max_dex
        self.asf = asf
        self.armor_check = armor_check