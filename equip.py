import copy

class Weapon:
    """Weapon data structure"""

    def __init__(self, name=None, type="Simple", group=[], atk_type="M", atk_damage=[1,8], range=5, crit_range=20, crit_mult=2, weap_bon=0, reach=False, spb="S", material=None, mwk=False, enchants=[], ammo=0, hands=1, disarm=False, trip=False):
        self.name = name
        self.item = "weapon"
        self.default = False
        self.type = type
        self.group = group
        self.atk_type = atk_type
        self.atk_damage = atk_damage
        self.range = range
        self.crit_range = crit_range
        self.crit_mult = crit_mult
        self.weap_bon = weap_bon
        self.reach = reach
        self.spb = spb
        self.material = material
        self.mwk = mwk
        self.enchants = enchants
        self.ammo = ammo
        self.hands = hands
        self.disarm = disarm
        self.trip = trip

    def avg_dmg(self):
        return int(((self.atk_damage[0]) + (self.atk_damage[0] * self.atk_damage[1])) / 2 + self.weap_bon)

    def fullname(self):

        out = ""

        if self.weap_bon > 0:
            out = "{:+d} ".format(self.weap_bon)
        elif self.mwk:
            out = "mwk "

        if self.material:
            out += "{} ".format(self.material)

        out += self.name

        return out

    def set_type(self, type):
        self.atk_type = type

    def set_mwk(self):
        if self.mwk:
            return None
        self.mwk = True

    def set_bon(self, bon):
        self.set_mwk()
        self.weap_bon = bon

    def set_mat(self, mat):
        self.material = mat

    def set_ammo(self, ammo):
        self.ammo = ammo

    def copy(self):
        return copy.copy(self)

class Armor:
    """Armor data structure"""

    def __init__(self, name=None, type="Light", armor_bon=0, shield_bon=0, max_dex=99, asf=0, armor_check=0, material=None, mwk=False, ench_bon=0, enchants=[], hands=0):
        self.name = name
        self.item = "armor"
        self.default = False
        self.type = type
        self.armor_bon = armor_bon
        self.shield_bon = shield_bon
        self.max_dex = max_dex
        self.asf = asf
        self.armor_check = armor_check
        self.material = material
        self.mwk = mwk
        self.ench_bon = ench_bon
        self.enchants = enchants
        self.hands = 0

    def fullname(self):

        out = ""

        if self.ench_bon > 0:
            out = "{:+d} ".format(self.ench_bon)
        elif self.mwk:
            out = "mwk "

        if self.material:
            out += "{} ".format(self.material)

        out += self.name

        return out

    def set_mwk(self):
        if self.mwk:
            return None
        self.mwk = True
        self.armor_check = min(0,self.armor_check + 1)

    def set_bon(self, bon):
        self.set_mwk()
        self.ench_bon = bon

    def set_mat(self, mat):
        self.material = mat

    def copy(self):
        return copy.copy(self)