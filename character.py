class Foundation:
    """Base stats and data"""

    import random
    import equip

    def __init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, subtype, size, reach):
        self.name = name
        self.side = side
        self.AC = AC
        self.move = move
        self.startloc = loc
        self.loc = loc
        self.hp = hp
        self.tilesize = tilesize
        self.str = str
        self.dex = dex
        self.con = con
        self.int = int
        self.wis = wis
        self.cha = cha
        self.feat_list = feat_list
        self.type = type
        self.subtype = subtype
        self.size = size
        self.reach = reach
        self.bab = 0
        self.arcane = False
        self.divine = False
        self.CL = 0
        self.HD = 1
        self.hit_die = 10
        self.init = 0
        self.damage = 0
        self.damage_con = "Normal"
        self.weap = -1
        self.weap_list = []
        self.armor = -1
        self.shield = -1
        self.conditions = []
        self.armor_list = []
        self.ftr_wt = []
        self.rgr_fe = []

###################################################################
#
# General calculation functions

    def stat_bonus(self, stat):
        return (stat - 10) / 2

    def range_pen(self, dist):
        pen = (dist / self.weap_range()) * -2

        if pen < -10:
            pen = -10

        return pen

    def current_hp(self):
        return self.hp - self.damage

    def tile_in_token(self, tile):
        x_dist = tile[0] - self.loc[0]
        y_dist = tile[1] - self.loc[1]

        return (x_dist in range(0,self.tilesize[0]) and y_dist in range(0,self.tilesize[1]))

###################################################################
#
# Import functions

    def add_weapon(self, weapon, active=False):
        self.weap_list.append(weapon)
        if active:
            self.set_weapon(len(self.weap_list) - 1)

    def add_armor(self, armor, active=False):
        self.armor_list.append(armor)
        if active:
            self.set_armor(len(self.armor_list) - 1)

    def add_shield(self, shield, active=False):
        self.armor_list.append(shield)
        if active:
            self.set_shield(len(self.armor_list) - 1)

###################################################################
#
# Active equipment data retrieval functions

    def weap_name(self):
        return self.weap_list[self.weap].name

    def weap_group(self):
        return self.weap_list[self.weap].group

    def weap_type(self):
        return self.weap_list[self.weap].atk_type

    def weap_dmg(self):
        return self.weap_list[self.weap].atk_damage

    def weap_range(self):
        return self.weap_list[self.weap].range

    def weap_crit_range(self):
        return self.weap_list[self.weap].crit_range

    def weap_crit_mult(self):
        return self.weap_list[self.weap].crit_mult

    def weap_bon(self):
        return self.weap_list[self.weap].weap_bon

    def weap_reach(self):
        return self.weap_list[self.weap].reach


    def armor_name(self):
        return self.armor_list[self.armor].name

    def armor_type(self):
        return self.armor_list[self.armor].type

    def armor_armor_bon(self):
        return self.armor_list[self.armor].armor_bon

    def armor_max_dex(self):
        return self.armor_list[self.armor].max_dex

    def armor_armor_check(self):
        return self.armor_list[self.armor].armor_check

    def armor_asf(self):
        return self.armor_list[self.armor].asf


    def shield_name(self):
        return self.armor_list[self.shield].name

    def shield_type(self):
        return self.armor_list[self.shield].type

    def shield_shield_bon(self):
        return self.armor_list[self.shield].shield_bon

###################################################################
#
# Value-setting functions

    def set_weapon(self, weap_num):
        self.weap = weap_num

    def set_armor(self, armor_num):
        self.armor = armor_num

    def set_shield(self, shield_num):
        self.shield = shield_num

    def take_damage(self, dmg):

        self.damage = self.damage + dmg

        if self.damage == self.hp:
            self.damage_con = "Disabled"
        if self.damage > self.hp:
            self.damage_con = "Dying"
        if self.damage > self.hp + self.contot():
            self.damage_con = "Dead"

    def set_init(self):
        self.init = self.stat_bonus(self.dextot())

        if "Improved Initiative" in self.feat_list:
            self.init = self.init + 4

    def set_condition(self, condition):
        if condition not in self.conditions:
            self.conditions.append(condition)

    def drop_condition(self, condition):
        if condition in self.conditions:
            self.conditions.remove(condition)

###################################################################
#
# Feat effect functions

    def arcane_strike_bon(self):
        if not self.arcane:
            return 0
        else:
            return (self.CL / 5) + 1

    def bullseye_bon(self, FRA):
        if "Point-Blank Shot" in self.feat_list and "Precise Shot" in self.feat_list and self.bab[0] >=5 and not FRA and self.weap_type() in ["R","RT"]:
            return 4
        else:
            return 0

    def critical_focus_bon(self):
        if self.bab[0] >= 9:
            return 4
        else:
            return 0

    def deadly_aim_bon(self):
        if self.dextot() < 13 or self.bab[0] < 1 or self.weap_type() in ["M","O","2"]:
            return 0

        da_bon = ((self.bab[0] / 5) + 1) * 2

        return da_bon

    def deadly_aim_pen(self):
        if self.dextot() < 13 or self.bab[0] < 1 or self.weap_type() in ["M","O","2"]:
            return 0

        return ((self.bab[0] / 5) + 1) * -1

    def dodge_bon(self):
        if self.dextot() < 13:
            return 0
        else:
            return 1

    def favored_defense_bon(self, type):
        if charClass == "Ranger" and type in self.ranger_fe_types():
            return self.ranger_fe_bon(type) / 2

    def manyshot(self):
        return "Point-Blank Shot" in self.feat_list and "Rapid Shot" in self.feat_list and self.bab[0] >= 6 and self.weap_type() in ["R","RT"]

    def power_attack_bon(self):
        if self.strtot() < 13 or self.bab[0] < 1 or self.weap_type() in ["R","RT"]:
            return 0

        pa_bon = ((self.bab[0] / 5) + 1) * 2

        if self.weap_type() == "2":
            pa_bon = pa_bon * 3 / 2
        elif self.weap_type() == "O":
            pa_bon = pa_bon / 2

        return pa_bon

    def power_attack_pen(self):
        if self.strtot() < 13 or self.bab[0] < 1 or self.weap_type() in ["R","RT"]:
            return 0

        return ((self.bab[0] / 5) + 1) * -1

    def pbs_bon(self, dist):
        if dist < 30 and self.weap_type() in ["R","RT"]:
            return 1
        else:
            return 0

    def rapid_shot(self, FRA):
        return "Point-Blank Shot" in self.feat_list and self.dextot() >= 13 and FRA and self.weap_type() in ["R","RT"]

    def rapid_shot_pen(self, FRA):
        if "Point-Blank Shot" in self.feat_list and self.dextot() >= 13 and FRA and self.weap_type() in ["R","RT"]:
            return -2
        else:
            return 0

    def snap_shot(self):
        return self.dextot() >= 13 and "Point-Blank Shot" in self.feat_list and "Rapid Shot" in self.feat_list and "Weapon Focus ({})".format(self.weap_name()) in self.feat_list and self.bab[0]>=6

    def snap_shot_imp(self):
        return self.dextot() >= 15 and "Point-Blank Shot" in self.feat_list and "Rapid Shot" in self.feat_list and "Snap Shot" in self.feat_list and "Weapon Focus ({})".format(self.weap_name()) in self.feat_list and self.bab[0]>=9

    def toughness_bon(self):
        if self.HD <= 3:
            bon = 3
        else:
            bon = self.HD

        return bon

###################################################################
#
# Generic class ability functions

    def uncanny_dodge(self):
        if self.charClass == "Rogue" and self.level >= 4:
            return True
        if self.charClass == "Barbarian" and self.level >= 2:
            return True
        return False

    def improved_uncanny_dodge(self):
        if self.charClass == "Rogue" and self.level >= 8:
            return True
        if self.charClass == "Barbarian" and self.level >= 5:
            return True
        return False

###################################################################
#
# Fighter class ability functions

    def set_fighter_weap_train(self, groups):
        if self.charClass != "Fighter":
            raise StandardError("Cannot set Fighter options for non-Fighter")
        if len(groups) != (self.level - 1) / 4:
            raise StandardError("Wrong number of groups set for Weapon Training")
        self.ftr_wt = groups

    def fighter_wt_bon(self, groups):
        if self.charClass != "Fighter":
            return 0
        matching_groups = list(set(groups).intersection(self.ftr_wt))
        if not matching_groups:
            return 0
        wt = self.ftr_wt[::-1]
        wt_bon = map(lambda x:wt.index(x) + 1, matching_groups)
        return max(wt_bon)

###################################################################
#
# Ranger class ability functions

    def set_ranger_favored_enemy(self, types):
        if self.charClass != "Ranger":
            raise StandardError("Cannot set Ranger options for non-Ranger")
        tot_bon_count = (self.level * 4 / 5) + 2
        if sum([x[1] for x in types]) != tot_bon_count:
            raise StandardError("Wrong bonus assignment for Favored Enemy")
        self.rgr_fe = types

    def ranger_fe_types(self):
        return [x[0] for x in self.rgr_fe]

    def ranger_fe_bon(self, type, subtype=[]):
        match_types = [i for i, x in enumerate(self.rgr_fe) if x[0]==type]

        if type not in ["Humanoid","Outsider"]:
            if match_types:
                return self.rgr_fe[match_types[0]][1]
            else:
                return 0
        else:
            match_subtypes = [i for i, x in enumerate(self.rgr_fe) if x[0]==type and x[2] in subtype]

            if match_subtypes:
                return self.rgr_fe[match_subtypes[0]][1]
            else:
                return 0

###################################################################
#
# Statistic value functions

    def add_bon(self, bon_list, bon_type, bon_val):
        if not bon_type in bon_list:
            bon_list[bon_type] = bon_val
        else:
            if bon_type in ["dodge","racial","untyped","circumstance"]:
                bon_list[bon_type] = bon_list[bon_type] + bon_val
            else:
                bon_list[bon_type] = max(bon_list[bon_type],bon_val)

    #############################
    #
    # Base stat functions

    def strtot(self):
        stat = self.str

        return stat

    def dextot(self):
        stat = self.dex

        return stat

    def contot(self):
        stat = self.con

        return stat

    def inttot(self):
        stat = self.int

        return stat

    def wistot(self):
        stat = self.wis

        return stat

    def chatot(self):
        stat = self.cha

        return stat

    #############################
    #
    # AC functions

    def get_AC_bons(self, type=None, subtype=None):

        AC_bon = dict()

        stat_bon = min(self.armor_max_dex(), self.stat_bonus(self.dextot()))

        self.add_bon(AC_bon,"Dex",stat_bon)

        #############################
        #
        # Equipment bonus

        self.add_bon(AC_bon,"armor",self.armor_armor_bon())

        self.add_bon(AC_bon,"shield",self.shield_shield_bon())

        #############################
        #
        # Feat bonuses

        if "Dodge" in self.feat_list:
            self.add_bon(AC_bon,"dodge",self.dodge_bon())

        if "Favored Defense ({})".format(type) in self.feat_list or "Favored Defense ({} ({}))".format(type,subtype) in self.feat_list:
            self.add_bon(AC_bon,"dodge",self_favored_defense_bon(type, subtype))

        return AC_bon

    def get_AC(self, type=None, subtype=None, FF=False, touch=False):

        temp_AC_bons = self.get_AC_bons(type=type, subtype=subtype)

        if self.has("Flat-Footed") or FF:
            temp_AC_bons = self.get_FF_AC_bons(temp_AC_bons)
        if touch:
            temp_AC_bons = self.get_touch_AC_bons(temp_AC_bons)

        return 10 + sum(temp_AC_bons.itervalues())

    def get_FF_AC_bons(self, temp_AC_bons):

        if not self.uncanny_dodge():
            temp_AC_bons.pop("Dex",None)
            temp_AC_bons.pop("dodge",None)

        return temp_AC_bons

    def get_touch_AC_bons(self, temp_AC_bons):

        temp_AC_bons.pop("armor",None)
        temp_AC_bons.pop("natural",None)
        temp_AC_bons.pop("shield",None)

        return temp_AC_bons

    #############################
    #
    # AoO functions

    def can_aoo(self):
        return not self.has("Flat-Footed") or self.uncanny_dodge()

    def get_aoo_count(self):
        if "Combat Reflexes" in self.feat_list:
            return self.stat_bonus(self.dextot())
        else:
            return 1

    #############################
    #
    # Attack bonus functions

    def get_atk_bon(self, dist, FRA, type, subtype):

        # Note: rewrite to return dictionary of bonus types to account for possible same-type issues

        atk_bon = dict()

        #############################
        #
        # Enchantment/masterwork bonus

        if self.weap_bon() == -13:
            self.add_bon(atk_bon,"enhancement",1)
        else:
            self.add_bon(atk_bon,"enhancement",self.weap_bon())

        #############################
        #
        # Stat bonus

        if self.weap_type() in ["M","O","2"]:
            self.add_bon(atk_bon,"stat",self.stat_bonus(self.strtot()))
        elif self.weap_type() in ["R","RT"]:
            self.add_bon(atk_bon,"stat",self.stat_bonus(self.dextot()))
            self.add_bon(atk_bon,"untyped",self.range_pen(dist))

        #############################
        #
        # Class bonuses, all attacks

        if self.charClass == "Fighter" and self.level >= 5:
            self.add_bon(atk_bon,"untyped",self.fighter_wt_bon(self.weap_group()))

        if self.charClass == "Ranger":
            self.add_bon(atk_bon,"untyped",self.ranger_fe_bon(type, subtype))

        #############################
        #
        # Feat bonuses, all attacks

        if "Deadly Aim" in self.feat_list:
            self.add_bon(atk_bon,"untyped",self.deadly_aim_pen())

        if "Point-Blank Shot" in self.feat_list:
            self.add_bon(atk_bon,"untyped",self.pbs_bon(dist))

        if "Power Attack" in self.feat_list:
            self.add_bon(atk_bon,"untyped",self.power_attack_pen())

        if "Rapid Shot" in self.feat_list:
            self.add_bon(atk_bon,"untyped",self.rapid_shot_pen(FRA))

        atk_bon_tot = sum(atk_bon.itervalues())

        atk_bon_list = map(lambda x: x + atk_bon_tot, self.bab)

        #############################
        #
        # Feat bonuses, single attacks

        if "Rapid Shot" in self.feat_list and self.rapid_shot(FRA):
            atk_bon_list.insert(0,atk_bon_list[0])

        if "Bullseye Shot" in self.feat_list:
            atk_bon_list[0] = atk_bon_list[0] + self.bullseye_bon(FRA)

        if FRA:
            return atk_bon_list
        else:
            return atk_bon_list[0:1]

    #############################
    #
    # Damage bonus functions

    def get_base_dmg_bon(self, dist, type, subtype):

        #############################
        #
        # Enchantment/masterwork bonus

        if self.weap_bon() == -13:
            dmg_bon = 0
        else:
            dmg_bon = self.weap_bon()

        #############################
        #
        # Stat bonus

        str_bon = self.stat_bonus(self.strtot())
        dex_bon = self.stat_bonus(self.dextot())

        if self.weap_type() in ["M","RT"]:
            dmg_bon = dmg_bon + str_bon
        elif self.weap_type() == "O":
            if str_bon > 0:
                dmg_bon = dmg_bon + str_bon / 2
            else:
                dmg_bon = dmg_bon + str_bon
        elif self.weap_type() == "2":
            if str_bon > 0:
                dmg_bon = dmg_bon + str_bon * 3 / 2
            else:
                dmg_bon = dmg_bon + str_bon
        elif self.ambi and self.weap_type() == "R":
            dmg_bon = dmg_bon + dex_bon

        #############################
        #
        # Class bonuses

        if self.charClass == "Fighter" and self.level >= 5:
            dmg_bon = dmg_bon + self.fighter_wt_bon(self.weap_group())

        if self.charClass == "Ranger":
            dmg_bon = dmg_bon + self.ranger_fe_bon(type, subtype)

        #############################
        #
        # Feat bonuses

        if "Arcane Strike" in self.feat_list:
            dmg_bon = dmg_bon + self.arcane_strike_bon()

        if "Deadly Aim" in self.feat_list:
            dmg_bon = dmg_bon + self.deadly_aim_bon()

        if "Point-Blank Shot" in self.feat_list:
            dmg_bon = dmg_bon + self.pbs_bon(dist)

        if "Power Attack" in self.feat_list:
            dmg_bon = dmg_bon + self.power_attack_bon()

        return dmg_bon

    #############################
    #
    # Condition functions

    def has(self, condition):
        return condition in self.conditions

    #############################
    #
    # Threat range functions

    def threat_range(self):
        tr = [0,0]

        if self.weap_type() in ["M","2","O"]:
            tr = [5, self.reach]
            if self.weap_reach():
                tr = [self.reach + 5, self.reach * 2]
        else:
            if "Snap Shot" in self.feat_list and self.snap_shot():
                tr = [5,5]
            if "Improved Snap Shot" in self.feat_list and self.snap_shot_imp():
                tr = [5,15]

        return tr

###################################################################
#
# Mechanics functions

    def check_attack(self, targ_AC, dist, FRA, type, subtype):

        atk_bon = self.get_atk_bon(dist, FRA, type, subtype)
        hit_miss = [0 for i in range(len(atk_bon))]

        for i in range(len(atk_bon)):

            #############################
            #
            # Roll attack(s)

            atk_roll = self.random.randint(1,20)

            if atk_roll == 20:
                hit_miss[i] = 1
            elif (atk_roll + atk_bon[i]) >= targ_AC:
                hit_miss[i] = 1

            #############################
            #
            # Check for critical

            crit_rng = self.weap_crit_range()

            if "Improved Critical({})".format(self.weap_name()) in self.feat_list:
                crit_rng = 21 - ((21 - crit_rng) * 2)

            if atk_roll >= crit_rng and hit_miss[i] == 1:
                conf_roll = self.random.randint(1,20)

                conf_bon = atk_bon[i]

                if "Critical Focus" in self.feat_list:
                    conf_bon = conf_bon + self.critical_focus_bon()

                if conf_roll == 20 or (conf_roll + conf_bon) >= targ_AC:
                    hit_miss[i] = 2

        return hit_miss

    def roll_dmg(self, dist, crit=False, type=None, subtype=None):

        #############################
        #
        # Crit multiplier

        if crit == True:
            roll_mult = self.weap_crit_mult()
        else:
            roll_mult = 1

        dmg_bon = self.get_base_dmg_bon(dist, type, subtype)

        #############################
        #
        # Damage roll

        dmg = 0
        for j in range(roll_mult):
            for i in range(self.weap_dmg()[0]):
                dmg = dmg + self.random.randint(1,self.weap_dmg()[1])
            dmg = dmg + dmg_bon

        return dmg

    def roll_hp_tot(self):
        hp = 0

        hit_roll = self.HD

        if self.level > 0:
            hit_roll = hit_roll - 1
            hp = self.hit_die

        for i in range(hit_roll):
            hp = hp + self.random.randint(1,self.hit_die)

        #############################
        #
        # Stat bonus

        if self.type == "Undead":
            hp_stat_bon = self.stat_bonus(self.chatot()) * self.HD
        elif self.type == "Construct":
            if self.size == "Small":
                hp_stat_bon = 10
            elif self.size == "Medium":
                hp_stat_bon = 20
            elif self.size == "Large":
                hp_stat_bon = 30
            elif self.size == "Huge":
                hp_stat_bon = 40
            elif self.size == "Gargantuan":
                hp_stat_bon = 60
            elif self.size == "Colossal":
                hp_stat_bon = 80
            else:
                hp_stat_bon = 0
        else:
            hp_stat_bon = self.stat_bonus(self.contot()) * self.HD

        hp = hp + hp_stat_bon

        #############################
        #
        # Feat bonus

        if "Toughness" in self.feat_list:
            hp = hp + self.toughness_bon()

        if hp < self.HD:
            hp = self.HD

        self.hp = hp

    def attack(self, targ_AC, dist=5, FRA=True, type=None, subtype=None):

        dmg = 0
        hit_miss = self.check_attack(targ_AC, dist, FRA, type, subtype)
        dmg_vals = [0 for i in hit_miss]
        dmg_list_out = ["" for i in hit_miss]

        atk_count = 0
        for atk_result in hit_miss:
            if atk_result == 0:
                dmg_vals[atk_count] = 0
                dmg_list_out[atk_count] = "miss"
            elif atk_result == 1:
                dmg_vals[atk_count] = self.roll_dmg(dist, type=type, subtype=subtype)

                if "Manyshot" in self.feat_list and self.manyshot() and atk_count == 0:

                    dmg_vals[atk_count] = dmg_vals[atk_count] + self.roll_dmg(dist, type=type, subtype=subtype)

                dmg_list_out[atk_count] = str(dmg_vals[atk_count])
            elif atk_result == 2:
                dmg_vals[atk_count] = self.roll_dmg(dist, crit=True, type=type, subtype=subtype)

                if "Manyshot" in self.feat_list and self.manyshot() and atk_count == 0:

                    dmg_vals[atk_count] = dmg_vals[atk_count] + self.roll_dmg(dist, type=type, subtype=subtype)

                dmg_list_out[atk_count] = "*" + str(dmg_vals[atk_count])

            atk_count = atk_count + 1


        return (sum(dmg_vals),dmg_list_out)

###################################################################
#
# Output functions

    def print_dmg(self, dist, type, subtype):
        out = "{}d{}".format(self.weap_dmg()[0],self.weap_dmg()[1])

        dmg_bon = self.get_base_dmg_bon(dist, type, subtype)

        if dmg_bon != 0:
            out = out + "{:+d}".format(dmg_bon)

        return out

    def print_AC_bons(self, type=None, subtype=None):

        AC_bons = self.get_AC_bons(type, subtype)

        AC_keys = sorted(AC_bons.keys())

        AC_out = ""

        for AC_type in AC_keys:
            if AC_bons[AC_type] != 0:
                AC_out = AC_out + "{:+d} {}, ".format(AC_bons[AC_type],AC_type)

        return AC_out[:-2]

    def print_AC_line(self, type=None, subtype=None):

        return "AC {}, touch {}, flat-footed {} ({})".format(self.get_AC(), self.get_AC(touch=True), self.get_AC(FF=True), self.print_AC_bons())

    def print_atk_line(self, dist=0, FRA=True, type=None, subtype=None):

        atk_out = ""

        if self.weap_bon() > 0:
            atk_out = "{:+d} ".format(self.weap_bon())
        elif self.weap_bon == -13:
            atk_out = "mwk "

        atk_out = atk_out + "{} ".format(self.weap_name())

        atk_bon = self.get_atk_bon(dist, FRA, type, subtype)

        if len(atk_bon) == 1:
            temp = "{:+d}".format(atk_bon[0])
        else:
            temp = "/".join(map(lambda x:"{:+d}".format(x), atk_bon))

        atk_out = atk_out + temp + " (" + self.print_dmg(dist,type,subtype)

        crit_rng = self.weap_crit_range()

        if "Improved Critical ({})".format(self.weap_name()) in self.feat_list:
            crit_rng = 21 - ((21 - crit_rng) * 2)

        if crit_rng != 20 or self.weap_crit_mult() != 2:
            atk_out = atk_out + ", "
            if crit_rng == 20:
                temp = "20"
            else:
                temp = "{}-20".format(crit_rng)

            atk_out = atk_out + temp + "/x" + str(self.weap_crit_mult())

        if self.weap_type() in ["R","RT"]:
            atk_out = atk_out + ", Range: " + str(self.weap_range()) + " ft."

        atk_out = atk_out + ")"

        return atk_out

    def print_hp(self):
        return "{}/{}".format(self.hp - self.damage,self.hp)

###################################################################

class Character(Foundation):
    """NPC stats and data"""

    def __init__(self, name=None, side=1, AC=10, move=30, loc=[0,0], tilesize=[1,1], level=1, charClass="Fighter", hp=1, str=10, dex=10, con=10, int=10, wis=10, cha=10, feat_list=[], ambi=False, type="Humanoid", subtype=[], size="Medium", reach=5):

        Foundation.__init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, subtype, size, reach)

        self.level = level
        self.HD = level
        self.charClass = charClass
        self.ambi = ambi

        self.equip_unarmed()
        self.equip_no_armor()
        self.equip_no_shield()

        self.set_bab()
        self.set_spellcast_stats()
        self.set_hit_die()
        self.set_init()

        if hp == 0:
            self.roll_hp_tot()

    def equip_unarmed(self):

        self.unarmed = self.equip.Weapon(name="unarmed strike", group=["Monk","Natural"], atk_damage=[1,3])

        self.add_weapon(self.unarmed, active=True)

    def equip_no_armor(self):

        self.no_armor = self.equip.Armor(name="No armor")

        self.add_armor(self.no_armor, active=True)

    def equip_no_shield(self):

        self.no_shield = self.equip.Armor(name="No shield")

        self.add_shield(self.no_shield, active=True)

    def set_bab(self):

        if self.charClass in ["Barbarian", "Fighter", "Paladin", "Ranger"]:
            self.bab = range(self.level, 1, -5)
        elif self.charClass in ["Bard", "Cleric", "Druid", "Monk", "Rogue"]:
            self.bab = range(self.level * 3 / 4, 1, -5)
        else:
            self.bab = range(self.level / 2, 1, -5)

    def set_spellcast_stats(self):

        if self.charClass in ["Bard", "Sorcerer", "Wizard"]:
            self.arcane = True
            self.CL = self.level

        if self.charClass in ["Cleric", "Druid"]:
            self.divine = True
            self.CL = self.level

        if self.charClass in ["Paladin", "Ranger"] and self.level >= 4:
            self.divine = True
            self.CL = self.level - 3

    def set_hit_die(self):

        if self.charClass in ["Barbarian"]:
            self.hit_die = 12
        elif self.charClass in ["Fighter", "Paladin", "Ranger"]:
            self.hit_die = 10
        elif self.charClass in ["Bard", "Cleric", "Druid", "Monk", "Rogue"]:
            self.hit_die = 8
        else:
            self.hit_die = 6

    def update(self):

        self.set_bab()
        self.set_spellcast_stats()

    def reset(self):

        self.damage = 0
        self.damage_con = "Normal"
        self.loc = self.startloc

###################################################################

class Monster(Foundation):
    """Monster stats and data"""

    def __init__(self, name=None, side=1, AC=10, move=30, loc=[0,0], tilesize=[1,1], HD=1, type="Humanoid", subtype=[], size="Medium", hp=1, str=10, dex=10, con=10, int=10, wis=10, cha=10, feat_list=[], arcane=False, divine=False, CL=0, reach=5):

        Foundation.__init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, size, reach)

        self.level = 0
        self.charClass = None
        self.HD = HD
        self.arcane = arcane
        self.divine = divine
        self.CL = CL
        self.weap_bon = 0

        self.set_bab()
        self.set_hit_die()

        if hp == 0:
            self.roll_hp_tot()

    def set_bab(self):

        if self.type in ["Construct", "Dragon", "Magical Beast", "Monstrous Humanoid", "Outsider"]:
            self.bab = range(self.HD, 1, -5)
        elif self.type in ["Aberration", "Animal", "Humanoid", "Ooze", "Plant", "Undead", "Vermin"]:
            self.bab = range(self.HD * 3 / 4, 1, -5)
        else:
            self.bab = range(self.HD / 2, 1, -5)

    def set_hit_die(self):

        if self.type in ["Dragon"]:
            self.hit_die = 12
        elif self.type in ["Construct", "Magical Beast", "Monstrous Humanoid", "Outsider"]:
            self.hit_die = 10
        elif self.type in ["Aberration", "Animal", "Humanoid", "Ooze", "Plant", "Undead", "Vermin"]:
            self.hit_die = 8
        else:
            self.hit_die = 6

    def reset(self):

        self.damage = 0
        self.damage_con = "Normal"