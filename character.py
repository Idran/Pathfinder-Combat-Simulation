class Foundation:
    """Base stats and data"""

    import random
    import equip
    import textwrap

    def __init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, subtype, size, reach, fort, ref, will, hands):
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
        self.fort = fort
        self.ref = ref
        self.will = will
        self.hands = hands

        self.bab = 0
        self.arcane = False
        self.divine = False
        self.CL = 0
        self.hit_die = 10
        self.damage = 0
        self.damage_con = "Normal"
        self.weap_list = []
        self.melee_weaps = []
        self.ranged_weaps = []
        self.weap = -1
        self.weap_off = -1
        self.armor_list = []
        self.armor = -1
        self.shield = -1
        self.conditions = dict()
        self.ftr_wt = []
        self.ftr_mast = None
        self.rgr_fe = []
        self.sa = []
        self.sq = []
        self.da = []

###################################################################
#
# General calculation functions

    def current_hp(self):
        return self.get_hp() - self.damage

    def range_pen(self, dist):
        pen = (dist / self.weap_range()) * -2

        if pen < -10:
            pen = -10

        return pen

    def stat_bonus(self, stat):
        if stat >= 0:
            return (stat - 10) / 2
        else:
            return 0

    def tile_in_token(self, tile):
        x_dist = tile[0] - self.loc[0]
        y_dist = tile[1] - self.loc[1]

        return (x_dist in range(0,self.tilesize[0]) and y_dist in range(0,self.tilesize[1]))

    def TWF_pen(self, weap):
        if self.weap_off == -1:
            return 0

        if weap == self.weap_off:
            pen = -10
            if self.two_weapon_fighting():
                pen += self.two_weapon_fighting_bon()[1]
        else:
            pen = -10
            if self.two_weapon_fighting():
                pen += self.two_weapon_fighting_bon()[0]

        if "L" in self.weap_type(self.weap_off):
            pen += 2

        return pen


###################################################################
#
# Import functions

    def add_weapon(self, weapon, active=False, off=False):
        self.weap_list.append(weapon)

        if "M" in weapon.atk_type:
            self.melee_weaps.append(len(self.weap_list) - 1)
        if "R" in weapon.atk_type:
            self.ranged_weaps.append(len(self.weap_list) - 1)

        if active:
            self.set_weapon(len(self.weap_list) - 1)

        if off:
            self.set_off(len(self.weap_list) - 1)

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

    def weap_basename(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return ""

        return self.weap_list[val].name

    def weap_name(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return ""

        return self.weap_list[val].fullname()

    def weap_group(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return []

        return self.weap_list[val].group

    def weap_type(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return ""

        return self.weap_list[val].atk_type

    def weap_dmg(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return [1,1]

        return self.weap_list[val].atk_damage

    def weap_range(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return 0

        return self.weap_list[val].range

    def weap_crit_range(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return 0

        crit_rng = self.weap_list[val].crit_range

        if self.improved_critical(val):
            crit_rng = 21 - ((21 - crit_rng) * 2)

        return crit_rng

    def weap_crit_mult(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return 0

        crit_mult = self.weap_list[val].crit_mult

        if self.ftr_wm():
            crit_mult += 1

        return crit_mult

    def weap_bon(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return 0

        return self.weap_list[val].weap_bon

    def weap_reach(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return False

        return self.weap_list[val].reach

    def weap_mwk(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return False

        return self.weap_list[val].mwk

    def weap_hands(self, val=None):
        if val == None:
            val = self.weap
        if val < 0:
            return 0

        return self.weap_list[val].hands


    def armor_name(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return ""

        return self.armor_list[val].fullname()

    def armor_type(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return ""

        return self.armor_list[val].type

    def armor_armor_bon(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return 0

        return self.armor_list[val].armor_bon + self.armor_list[val].ench_bon

    def armor_max_dex(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return 0

        return self.armor_list[val].max_dex

    def armor_armor_check(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return 0

        return self.armor_list[val].armor_check

    def armor_asf(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return 0

        return self.armor_list[val].asf

    def armor_ench_bon(self, val=None):
        if val == None:
            val = self.armor
        if val < 0:
            return 0

        return self.armor_list[val].ench_bon


    def shield_name(self, val=None):
        if val == None:
            val = self.shield
        if val < 0:
            return ""

        return self.armor_list[val].fullname()

    def shield_type(self, val=None):
        if val == None:
            val = self.shield
        if val < 0:
            return ""

        return self.armor_list[val].type

    def shield_shield_bon(self, val=None):
        if val == None:
            val = self.shield
        if val < 0:
            return 0

        return self.armor_list[val].shield_bon + self.armor_list[val].ench_bon

    def shield_ench_bon(self, val=None):
        if val == None:
            val = self.shield
        if val < 0:
            return 0

        return self.armor_list[val].ench_bon

    def shield_hands(self, val=None):
        if val == None:
            val = self.shield
        if val < 0:
            return 0

        return self.armor_list[val].hands

###################################################################
#
# Weapon selection functions

    def best_weap(self, target):
        return len(self.weap_list) - 1

    def best_melee_weap(self, target):
        if not self.melee_weaps:
            return -1
        else:
            return self.melee_weaps[-1]

    def best_ranged_weap(self, target):
        if not self.ranged_weaps:
            return -1
        else:
            return self.ranged_weaps[-1]

###################################################################
#
# Value-setting functions

    def set_weapon(self, weap_num):
        if self.weap_hands(weap_num) + self.weap_hands(self.weap_off) + self.shield_hands() > self.hands:
            raise StandardError("Cannot set main weapon: too many hands")
        self.weap = weap_num

    def drop_weapon(self):
        self.weap = 1

    def set_off(self, weap_num):
        if self.weap_hands() + self.weap_hands(weap_num) + self.shield_hands() > self.hands:
            raise StandardError("Cannot set offhand weapon: too many hands")
        self.weap_off = weap_num

    def drop_off(self):
        self.weap_off = -1

    def set_armor(self, armor_num):
        self.armor = armor_num

    def drop_armor(self):
        self.armor = 1

    def set_shield(self, shield_num):
        if self.weap_hands() + self.weap_hands(self.weap_off) + self.shield_hands(shield_num) > self.hands:
            raise StandardError("Cannot set shield: too many hands")
        self.shield = shield_num

    def drop_shield(self):
        self.shield = 2

    def take_damage(self, dmg):

        self.damage = self.damage + dmg

        self.check_hp()

    def check_hp():
        if self.damage == self.get_hp():
            self.damage_con = "Disabled"
        if self.damage > self.get_hp():
            self.damage_con = "Dying"
            if self.has("Raging"):
                self.drop_rage()
        if self.damage > self.get_hp() + self.contot():
            self.damage_con = "Dead"
            if self.has("Raging"):
                self.drop_rage()

    def set_condition(self, condition, duration=-1):
        if condition not in self.conditions.keys():
            if condition == "Fatigued" and "Exhausted" in self.conditions.keys():
                self.conditions["Exhausted"] = max(self.conditions["Exhausted"],duration)
            else:
                self.conditions[condition] = duration
        elif condition == "Fatigued":
            self.conditions["Exhausted"] = max(self.conditions["Fatigued"],duration)
            self.drop_condition("Fatigued")

    def drop_condition(self, condition):
        if condition in self.conditions.keys():
            del self.conditions[condition]

    def add_sq(self, quality):
        if quality not in self.sq:
            self.sq.append(quality)

    def del_sq(self, quality):
        if quality in self.sq:
            self.sq.remove(quality)

    def add_sa(self, quality):
        if quality not in self.sa:
            self.sa.append(quality)

    def del_sa(self, quality):
        if quality in self.sa:
            self.sa.remove(quality)

    def add_da(self, quality):
        if quality not in self.da:
            self.da.append(quality)

    def del_da(self, quality):
        if quality in self.da:
            self.da.remove(quality)

###################################################################
#
# Feat effect functions

    def arcane_strike(self):
        return "Arcane Strike" in self.feat_list

    def arcane_strike_bon(self):
        if self.arcane:
            return (self.CL / 5) + 1
        else:
            return 0

    def bullseye_shot(self):
        return "Bullseye Shot" in self.feat_list and self.point_blank_shot() and self.precise_shot() and self.bab[0]>=5

    def bullseye_shot_bon(self, FRA):
        if self.bullseye_shot():
            return 4
        else:
            return 0

    def combat_reflexes(self):
        return "Combat Reflexes" in self.feat_list

    def critical_focus(self):
        return "Critical Focus" in self.feat_list and self.bab[0] >= 9

    def critical_focus_bon(self):
        if self.critical_focus():
            return 4
        else:
            return 0

    def deadly_aim():
        return "Deadly Aim" in self.feat_list and self.dextot() >= 13 and self.bab >= 1

    def deadly_aim_bon(self):
        if self.deadly_aim() and "R" in self.weap_type():
            return ((self.bab[0] / 5) + 1) * 2
        else:
            return 0

    def deadly_aim_pen(self):
        if self.deadly_aim:
            return ((self.bab[0] / 5) + 1) * -1
        else:
            return 0

    def dodge(self):
        return "Dodge" in self.feat_list and self.dextot >= 13

    def dodge_bon(self):
        if self.dodge():
            return 1
        else:
            return 0

    def favored_defense(self, type="", subtype=""):
        return "Favored Defense ({})".format(type) in self.feat_list or "Favored Defense ({} ({}))".format(type,subtype) in self.feat_list

    def favored_defense_bon(self, type, subtype):
        if self.favored_defense(type, subtype) and type in self.ranger_fe_types():
            return self.ranger_fe_bon(type) / 2
        else:
            return 0

    def great_fortitude(self):
        return "Great Fortitude" in self.feat_list

    def great_fortitude_bon(self):
        if self.great_fortitude():
            return 2
        else:
            return 0

    def improved_critical(self, weap=None):
        if weap == None:
            weap = self.weap

        return "Improved Critical ({})".format(self.weap_basename(weap)) in self.feat_list

    def improved_initiative(self):
        return "Improved Initiative" in self.feat_list

    def improved_initiative_bon(self):
        if self.improved_initiative():
            return 4
        else:
            return 0

    def iron_will(self):
        return "Iron Will" in self.feat_list

    def iron_will_bon(self):
        if self.iron_will():
            return 2
        else:
            return 0

    def lightning_reflexes(self):
        return "Lightning Reflexes" in self.feat_list

    def lightning_reflexes_bon(self):
        if self.lightning_reflexes():
            return 2
        else:
            return 0

    def manyshot(self):
        return "Manyshot" in self.feat_list and self.point_blank_shot() and self.rapid_shot() and self.bab[0] >= 6

    def power_attack(self):
        return "Power Attack" in self.feat_list and self.strtot() >= 13 and self.bab[0] >= 1

    def power_attack_bon(self, off=False):
        if not self.power_attack():
            return 0

        pa_bon = ((self.bab[0] / 5) + 1) * 2

        if self.weap_hands() == "2":
            pa_bon = pa_bon * 3 / 2
        elif off:
            pa_bon = pa_bon / 2

        return pa_bon

    def power_attack_pen(self):
        if not self.power_attack():
            return 0

        return ((self.bab[0] / 5) + 1) * -1

    def point_blank_shot(self):
        return "Point-Blank Shot" in self.feat_list()

    def pbs_bon(self):
        if self.point_blank_shot():
            return 1
        else:
            return 0

    def quick_draw(self):
        return "Quick Draw" in self.feat_list and self.bab[0] >= 1

    def rapid_shot(self):
        return "Rapid Shot" in self.feat_list and self.point_blank_shot() and self.dextot() >= 13

    def rapid_shot_pen(self):
        if self.rapid_shot():
            return -2
        else:
            return 0

    def snap_shot(self):
        return "Snap Shot" in self.feat_list and self.dextot() >= 13 and self.point_blank_shot() and self.rapid_shot() and self.weapon_focus() and self.bab[0]>=6

    def snap_shot_imp(self):
        return "Improved Snap Shot" in self.feat_list and self.dextot() >= 15 and self.point_blank_shot() and self.rapid_shot() and self.weapon_focus() and self.bab[0]>=9

    def toughness(self):
        return "Toughness" in self.feat_list

    def toughness_bon(self):
        if self.toughness():
            if self.HD <= 3:
                return 3
            else:
                return self.HD
        else:
            return 0

    def two_weapon_fighting(self):
        return "Two-Weapon Fighting" in self.feat_list and self.dextot() >= 15

    def two_weapon_fighting_bon(self):
        if self.two_weapon_fighting():
            return [2,6]
        else:
            return [0,0]

    def weapon_focus(self, weap=None):
        if weap == None:
            weap = self.weap

        return "Weapon Focus ({})".format(self.weap_basename(weap)) in self.feat_list and self.bab[0] >= 1
        #and self.weap_prof(weap)

###################################################################
#
# Generic class ability functions

    def trap_sense_bon(self):
        if self.charClass != "Barbarian" and self.charClass != "Rogue":
            return 0
        else:
            return self.level / 3

    def uncanny_dodge(self):
        return "uncanny dodge" in self.da or "improved uncanny dodge" in self.da

    def uncanny_dodge_imp(self):
        return "improved uncanny dodge" in self.da

###################################################################
#
# Barbarian class ability functions

    def barbarian_rage_rds(self):

        rds = 4

        rds += self.stat_bonus(self.contot())

        rds += (self.level - 1) * 2

        return rds

    def set_rage(self):
        if not self.has("Fatigued") and not self.has("Exhausted"):
            self.set_condition("Raging",self.barbarian_rage_rds())
            self.rage_dur = 0
            if "R" in self.weap_type():
                self.set_weapon(self.best_melee_weap(None))
            return True
        else:
            return False

    def drop_rage(self):
        self.drop_condition("Raging")
        if self.level < 17:
            self.set_condition("Fatigued",2 * self.rage_dur)
        self.check_hp()

    def rage_bon(self):
        if self.charClass != "Barbarian":
            return 0
        elif self.level < 11:
            return 4
        elif self.level < 20:
            return 6
        else:
            return 8

    def rage_bon_indom_will(self):
        if self.charClass != "Barbarian" or level < 14:
            return 0
        else:
            return 4

        # Note: conditional save bonuses not yet implemented

    def barbarian_dr(self):
        return max((self.level - 4) / 3, 0)

###################################################################
#
# Fighter class ability functions

    def fighter_bravery(self):
        if self.charClass != "Fighter":
            return 0
        return (self.level + 2) / 4

        # Note: conditional save bonuses not yet implemented

    def fighter_armor_training(self):
        if self.charClass != "Fighter":
            return 0
        return (self.level + 1) / 4

    def set_fighter_weap_train(self, groups):
        if self.charClass != "Fighter":
            raise StandardError("Cannot set Fighter options for non-Fighter")
        if len(groups) != (self.level - 1) / 4:
            raise StandardError("Wrong number of groups set for Weapon Training")
        self.ftr_wt = groups

        train_text = []
        for group in groups:
            train_text.append("{} {:+d}".format(group.lower(),groups[::-1].index(group) + 1))
        self.add_sa("weapon training ({})".format(', '.join(train_text)))

    def fighter_wt_bon(self, groups):
        if self.charClass != "Fighter":
            return 0
        matching_groups = list(set(groups).intersection(self.ftr_wt))
        if not matching_groups:
            return 0
        wt = self.ftr_wt[::-1]
        wt_bon = map(lambda x:wt.index(x) + 1, matching_groups)
        return max(wt_bon)

    def set_fighter_weap_mast(self, weapon):
        if self.charClass != "Fighter":
            raise StandardError("Cannot set Fighter options for non-Fighter")
        self.ftr_mast = weapon
        self.add_sa("weapon mastery ({})".format(weapon))

    def ftr_am(self):
        return self.charClass == "Fighter" and self.level >= 19 and (self.armor_name() != "No armor" or self.shield_name() != "No shield")

    def ftr_wm(self):
        return self.charClass == "Fighter" and self.level >= 20 and self.weap_basename() == self.ftr_mast

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

        fe_text = []
        for type in types:
            if len(type) == 3:
                if type[0] == "Outsider":
                    text = "{} {} {:+d}".format(type[2].lower(), type[0].lower(), type[1])
                else:
                    text = "{} {:+d}".format(type[2].lower(),type[1])
            else:
                text = "{} {:+d}".format(type[0].lower(),type[1])
            fe_text.append(text)

        fe_text = sorted(fe_text)
        self.add_sa("favored enemy ({})".format(', '.join(fe_text)))

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
        if self.str == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.str)

        if self.has("Exhausted"):
            self.add_bon(stat_bon,"untyped",-6)
        if self.has("Fatigued"):
            self.add_bon(stat_bon,"untyped",-2)
        if self.has("Raging"):
            self.add_bon(stat_bon,"morale",self.rage_bon())

        return sum(stat_bon.itervalues())

    def dextot(self):
        if self.dex == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.dex)

        if self.has("Exhausted"):
            self.add_bon(stat_bon,"untyped",-6)
        if self.has("Fatigued"):
            self.add_bon(stat_bon,"untyped",-2)

        return sum(stat_bon.itervalues())

    def contot(self):
        if self.con == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.con)

        if self.has("Raging"):
            self.add_bon(stat_bon,"morale",self.rage_bon())

        return sum(stat_bon.itervalues())

    def inttot(self):
        if self.int == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.int)

        return sum(stat_bon.itervalues())

    def wistot(self):
        if self.wis == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.wis)

        return sum(stat_bon.itervalues())

    def chatot(self):
        if self.cha == None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon,"stat",self.cha)

        return sum(stat_bon.itervalues())

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

        self.add_bon(AC_bon,"dodge",self.dodge_bon())

        self.add_bon(AC_bon,"dodge",self.favored_defense_bon(type, subtype))

        if self.has("Raging"):
            self.add_bon(AC_bon,"rage",-2)

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
        if self.combat_reflexes():
            return self.stat_bonus(self.dextot())
        else:
            return 1

    #############################
    #
    # Attack roll functions

    def get_atk_bon(self, dist, FRA, type, subtype, weap=None, nofeat=False):

        atk_bon = dict()

        #############################
        #
        # Stat bonus

        if "M" in self.weap_type(weap):
            self.add_bon(atk_bon,"stat",self.stat_bonus(self.strtot()))
            self.add_bon(atk_bon,"untyped",self.TWF_pen(weap))
        elif "R" in self.weap_type(weap):
            self.add_bon(atk_bon,"stat",self.stat_bonus(self.dextot()))
            self.add_bon(atk_bon,"untyped",self.range_pen(dist))

        #############################
        #
        # Feat bonuses, all attacks

        if not nofeat:

            if "M" in self.weap_type():
                self.add_bon(atk_bon,"untyped",self.power_attack_pen())
            elif "R" in self.weap_type():
                self.add_bon(atk_bon,"untyped",self.deadly_aim_pen())
                if FRA:
                    self.add_bon(atk_bon,"untyped",self.rapid_shot_pen())

        atk_bon = self.get_attack_roll_mods(atk_bon, dist, FRA, type, subtype, weap, nofeat)

        atk_bon_tot = sum(atk_bon.itervalues())

        atk_bon_list = map(lambda x: x + atk_bon_tot, self.bab)

        #############################
        #
        # Feat bonuses, single attacks

        if not nofeat:
            if "R" in self.weap_type():
                if FRA:
                    if self.rapid_shot():
                        atk_bon_list.insert(0,atk_bon_list[0])
                else:
                    atk_bon_list[0] = atk_bon_list[0] + self.bullseye_shot_bon(FRA)

        if FRA:
            return atk_bon_list
        else:
            return atk_bon_list[0:1]

    def CMB(self, dist=0, FRA=True, type=None, subtype=None, weap=None, nofeat=False):

        cmb = dict()

        self.add_bon(cmb,"BAB",self.bab[0])

        self.add_bon(cmb,"Str",self.stat_bonus(self.strtot()))

        size_bon = 0

        if self.size == "Fine":
            size_bon = -8
        elif self.size == "Diminutive":
            size_bon = -4
        elif self.size == "Tiny":
            size_bon = -2
        elif self.size == "Small":
            size_bon = -1
        elif self.size == "Medium":
            size_bon = 0
        elif self.size == "Large":
            size_bon = 1
        elif self.size == "Huge":
            size_bon = 2
        elif self.size == "Gargantuan":
            size_bon = 4
        elif self.size == "Colossal":
            size_bon = 8

        self.add_bon(cmb,"Size",size_bon)

        cmb = self.get_attack_roll_mods(cmb, dist, FRA, type, subtype, weap, nofeat)

        cmb_tot = sum(cmb.itervalues())

        return cmb_tot

    def get_attack_roll_mods(self, atk_bon, dist, FRA, type, subtype, weap=None, nofeat=False):

        #############################
        #
        # Enchantment/masterwork bonus

        if self.weap_mwk(weap):
            if self.weap_bon(weap) == 0:
                self.add_bon(atk_bon,"enhancement",1)
            else:
               self.add_bon(atk_bon,"enhancement",self.weap_bon(weap))

        #############################
        #
        # Class bonuses, all attacks

        if self.charClass == "Fighter" and self.level >= 5:
            self.add_bon(atk_bon,"untyped",self.fighter_wt_bon(self.weap_group(weap)))

        if self.charClass == "Ranger":
            self.add_bon(atk_bon,"untyped",self.ranger_fe_bon(type, subtype))

        #############################
        #
        # Feat bonuses
        if not nofeat:

            if "M" in self.weap_type():
                pass
            elif "R" in self.weap_type():
                if dist < 30:
                    self.add_bon(atk_bon,"untyped",self.pbs_bon())

        return atk_bon

    #############################
    #
    # CMD functions

    def CMD(self, type=None, subtype=None, FF=False):
        cmd = dict()

        self.add_bon(cmd,"BAB",self.bab[0])

        self.add_bon(cmd,"Str",self.stat_bonus(self.strtot()))

        self.add_bon(cmd,"Dex",self.stat_bonus(self.dextot()))

        size_bon = 0

        if self.size == "Fine":
            size_bon = -8
        elif self.size == "Diminutive":
            size_bon = -4
        elif self.size == "Tiny":
            size_bon = -2
        elif self.size == "Small":
            size_bon = -1
        elif self.size == "Medium":
            size_bon = 0
        elif self.size == "Large":
            size_bon = 1
        elif self.size == "Huge":
            size_bon = 2
        elif self.size == "Gargantuan":
            size_bon = 4
        elif self.size == "Colossal":
            size_bon = 8

        self.add_bon(cmd,"Size",size_bon)

        AC_bons = self.get_AC_bons(type, subtype)

        if self.has("Flat-Footed") or FF:
            AC_bons = self.get_FF_AC_bons(AC_bons)

        for key in AC_bons.keys():
            if key in ["circumstance","deflection", "dodge", "insight", "luck", "morale", "profane", "sacred"]:
                self.add_bon(cmd,key,AC_bons[key])

        cmd_tot = 10 + sum(cmd.itervalues())

        return cmd_tot

    #############################
    #
    # Condition functions

    def has(self, condition):
        return condition in self.conditions.keys() and self.conditions[condition] != 0

    def round_pass(self):
        cond = dict(self.conditions)
        for condition in cond.keys():
            if condition == "Raging":
                self.rage_dur += 1
            if self.conditions[condition] > 0:
                self.conditions[condition] -= 1
            if self.conditions[condition] == 0:
                if condition == "Raging":
                    self.drop_rage()
                else:
                    self.drop_condition(condition)

    #############################
    #
    # Damage bonus functions

    def get_base_dmg_bon(self, dist, type, subtype, weap=None, nofeat=False):

        #############################
        #
        # Enchantment/masterwork bonus

        dmg_bon = self.weap_bon(weap)

        #############################
        #
        # Stat bonus

        str_bon = self.stat_bonus(self.strtot())
        dex_bon = self.stat_bonus(self.dextot())

        if weap == self.weap_off:
            if str_bon > 0:
                dmg_bon = dmg_bon + str_bon / 2
            else:
                dmg_bon = dmg_bon + str_bon
        elif self.weap_hands(weap) == 2 and "R" not in self.weap_type(weap):
            if str_bon > 0:
                dmg_bon = dmg_bon + str_bon * 3 / 2
            else:
                dmg_bon = dmg_bon + str_bon
        elif self.ambi and "R" in self.weap_type(weap):
            dmg_bon = dmg_bon + dex_bon
        elif "M" in self.weap_type(weap) or "T" in self.weap_type(weap):
            dmg_bon = dmg_bon + str_bon

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

        if not nofeat:
            dmg_bon = dmg_bon + self.arcane_strike_bon()

            if "M" in self.weap_type():
                dmg_bon = dmg_bon + self.power_attack_bon()
            elif "R" in self.weap_type():
                dmg_bon = dmg_bon + self.deadly_aim_bon()
                dmg_bon = dmg_bon + self.pbs_bon(dist)

        return dmg_bon

    #############################
    #
    # DR functions

    def get_dr(self):

        if self.ftr_am():
            return [5,["-"],""]

        if self.charClass == "Barbarian" and self.level >= 7:
            return [self.barbarian_dr(),["-"],""]

        return []

    #############################
    #
    # HP functions

    def get_hp_bon(self):

        hp_bon = 0

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

        hp_bon += hp_stat_bon

        #############################
        #
        # Feat bonus

        hp_bon += self.toughness_bon()

        #############################
        #
        # FC bonus

        hp_bon += self.fc.count("h")

        return hp_bon

    def get_hp(self):
        return max(self.hp + self.get_hp_bon(),self.HD)

    #############################
    #
    # Initiative functions

    def get_init(self):
        init = self.stat_bonus(self.dextot())

        init += self.improved_initiative_bon()

        return init

    #############################
    #
    # Saving throw functions

    def get_fort(self):

        speed = self.fort

        if speed == "Fast":
            save = (self.HD / 2) + 2
        else:
            save = (self.HD / 3)

        save_bon = dict()

        self.add_bon(save_bon,"base",save)
        self.add_bon(save_bon,"stat",self.stat_bonus(self.contot()))
        self.add_bon(save_bon,"untyped",self.great_fortitude_bon())

        return sum(save_bon.itervalues())

    def get_ref(self):

        speed = self.ref

        if speed == "Fast":
            save = (self.HD / 2) + 2
        else:
            save = (self.HD / 3)

        save_bon = dict()

        self.add_bon(save_bon,"base",save)
        self.add_bon(save_bon,"stat",self.stat_bonus(self.dextot()))
        self.add_bon(save_bon,"untyped",self.lightning_reflexes_bon())

        return sum(save_bon.itervalues())

    def get_will(self):

        speed = self.will

        if speed == "Fast":
            save = (self.HD / 2) + 2
        else:
            save = (self.HD / 3)

        save_bon = dict()

        self.add_bon(save_bon,"base",save)
        self.add_bon(save_bon,"stat",self.stat_bonus(self.wistot()))
        self.add_bon(save_bon,"untyped",self.iron_will_bon())
        if self.has("Raging"):
            self.add_bon(save_bon,"morale",self.rage_bon() / 2)

        return sum(save_bon.itervalues())

    #############################
    #
    # Speed functions

    def get_move(self):

        move = self.move

        if "fast movement" in self.sq and self.armor_type() != "Heavy":
            move += 10

        if self.has("Exhausted"):
            move /= 2

        return move

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
            if self.snap_shot():
                tr = [5,5]
            if self.snap_shot_imp():
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

            if atk_roll >= crit_rng and hit_miss[i] == 1:
                conf_roll = self.random.randint(1,20)

                conf_bon = atk_bon[i]

                conf_bon = conf_bon + self.critical_focus_bon()

                if conf_roll == 20 or (conf_roll + conf_bon) >= targ_AC or self.ftr_wm():
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

        self.hp = hp

    def weap_swap(self):
        if self.quick_draw():
            return "free"
        else:
            return "move"

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

                if self.manyshot() and "R" in self.weap_type() and atk_count == 0:

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

    def print_dmg(self, dist, type, subtype, weap=None, nofeat=False):

        if weap==None:
            weap = self.weap

        out = "{}d{}".format(self.weap_dmg(weap)[0],self.weap_dmg(weap)[1])

        dmg_bon = self.get_base_dmg_bon(dist, type, subtype, weap, nofeat)

        if dmg_bon != 0:
            out = out + "{:+d}".format(dmg_bon)

        return out

    def print_AC_bons(self, type=None, subtype=None):

        AC_bons = self.get_AC_bons(type, subtype)

        AC_keys = sorted(AC_bons.keys(), key=lambda x:x.lower())

        AC_out = ""

        for AC_type in AC_keys:
            if AC_bons[AC_type] != 0:
                AC_out = AC_out + "{:+d} {}, ".format(AC_bons[AC_type],AC_type)

        return AC_out[:-2]

    def print_AC_line(self, type=None, subtype=None):

        return "AC {}, touch {}, flat-footed {} ({})".format(self.get_AC(), self.get_AC(touch=True), self.get_AC(FF=True), self.print_AC_bons())

    def print_atk_line(self, dist=0, FRA=True, type=None, subtype=None, weap=None, nofeat=False):

        if weap==None:
            weap = self.weap

        atk_out = "{} ".format(self.weap_name(weap))

        atk_bon = self.get_atk_bon(dist, FRA, type, subtype, weap, nofeat)

        if len(atk_bon) == 1:
            temp = "{:+d}".format(atk_bon[0])
        else:
            temp = "/".join(map(lambda x:"{:+d}".format(x), atk_bon))

        atk_out += temp + " (" + self.print_dmg(dist,type,subtype,weap,nofeat)

        crit_rng = self.weap_crit_range(weap)

        if crit_rng != 20 or self.weap_crit_mult(weap) != 2:
            atk_out += ", "
            if crit_rng == 20:
                temp = "20"
            else:
                temp = "{}-20".format(crit_rng)

            atk_out += temp

            if self.weap_crit_mult(weap) != 2:
                atk_out += "/x" + str(self.weap_crit_mult(weap))

        atk_out += ")"

        return atk_out

    def print_HD(self):
        out = "{}d{}".format(self.HD,self.hit_die)

        hp_bon = self.get_hp_bon()

        if hp_bon != 0:
            out += "{:+d}".format(hp_bon)

        return out

    def print_hp(self):
        return "{}/{}".format(self.get_hp() - self.damage,self.get_hp())

    def print_save_line(self):
        return "Fort {:+d}, Ref {:+d}, Will {:+d}".format(self.get_fort(),self.get_ref(),self.get_will())

###################################################################

class Character(Foundation):
    """NPC stats and data"""

    def __init__(self, name=None, side=1, AC=10, move=30, loc=[0,0], tilesize=[1,1], level=1, charClass="Fighter", hp=1, str=10, dex=10, con=10, int=10, wis=10, cha=10, feat_list=[], ambi=False, type="Humanoid", subtype=["human"], size="Medium", reach=5, fort=None, ref=None, will=None, race="Human", hands=2, fc=[]):
        if fc == []:
            fc = ["s" for i in range(level)]

        self.race = race
        self.level = level
        self.HD = level
        self.charClass = charClass
        self.ambi = ambi
        self.fc = fc

        save_array = [fort,ref,will]
        save_array = self.set_saves(save_array)

        Foundation.__init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, subtype, size, reach, save_array[0], save_array[1], save_array[2], hands)

        self.set_bab()
        self.set_spellcast_stats()
        self.set_hit_die()

        if hp == 0:
            self.roll_hp_tot()

        self.equip_unarmed()
        self.equip_no_armor()
        self.equip_no_shield()

        self.set_class_abilities()

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
            if not self.bab:
                self.bab = [self.level]
        elif self.charClass in ["Bard", "Cleric", "Druid", "Monk", "Rogue"]:
            self.bab = range(self.level * 3 / 4, 1, -5)
            if not self.bab:
                self.bab = [self.level * 3 / 4]
        else:
            self.bab = range(self.level / 2, 1, -5)
            if not self.bab:
                self.bab = [self.level / 2]

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

    def set_saves(self, save_array):
        fort, ref, will = save_array

        if not fort:
            if self.charClass in ["Barbarian", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger"]:
                fort = "Fast"
            else:
                fort = "Slow"

        if not ref:
            if self.charClass in ["Bard", "Monk", "Ranger", "Rogue"]:
                ref = "Fast"
            else:
                ref = "Slow"

        if not will:
            if self.charClass in ["Bard", "Cleric", "Druid", "Monk", "Paladin", "Sorcerer", "Wizard"]:
                will = "Fast"
            else:
                will = "Slow"

        return [fort, ref, will]

    def set_class_abilities(self):
        if self.charClass == "Barbarian":
            self.add_sq("fast movement")
            if self.level < 11:
                self.add_sa("rage ({} rounds/day)".format(self.barbarian_rage_rds()))
            elif self.level < 20:
                self.add_sa("greater rage ({} rounds/day)".format(self.barbarian_rage_rds()))
            else:
                self.add_sa("mighty rage ({} rounds/day)".format(self.barbarian_rage_rds()))
            if self.level >= 2:
                if "uncanny dodge" in self.da:
                    self.del_da("uncanny dodge")
                    self.add_da("improved uncanny dodge")
                else:
                    self.add_da("uncanny dodge")
            if self.level >= 3:
                self.add_da("trap sense {:+d}".format(self.trap_sense_bon()))
            if self.level >= 5:
                self.del_da("uncanny dodge")
                self.add_da("improved uncanny dodge")

            if self.level >= 14:
                self.add_da("indomitable will")
            if self.level >= 17:
                self.add_sq("tireless rage")

        elif self.charClass == "Fighter":
            if self.level >= 2:
                self.add_da("bravery {:+d}".format(self.fighter_bravery()))
            if self.level >= 3:
                self.add_sq("armor training {}".format(self.fighter_armor_training()))
            if self.level >= 19:
                self.add_sq("armor mastery")


    def update(self):

        self.set_bab()
        self.set_spellcast_stats()

    def reset(self):

        self.damage = 0
        self.damage_con = "Normal"
        self.loc = self.startloc

    ############################################

    def print_stat_block(self, textwidth=60):

        stats = [self.strtot(), self.dextot(), self.contot(), self.inttot(), self.wistot(), self.chatot()]

        stats = map(lambda x:x if x > 0 else "-", stats)

        da_line = ""
        if self.da:
            da_line += "Defensive Abilities {}".format(", ".join(sorted(self.da)))
        dr = self.get_dr()
        if dr:
            if da_line != "":
                da_line += "; "
            da_line += "DR {}/{}".format(dr[0],dr[2].join(sorted(dr[1])))

        melee_set = []
        if "M" in self.weap_type(self.weap):
            base_atk_line = self.print_atk_line(nofeat=True)
            if self.weap_off != -1:
                base_atk_line += ", " + self.print_atk_line(nofeat=True,weap=self.weap_off)
            melee_set.append(base_atk_line)
        for weapon in self.melee_weaps:
            if weapon == self.weap or weapon == self.weap_off:
                continue
            if weapon == 0:
                if len(self.melee_weaps) > 1 and self.charClass != "Monk":
                    continue
            melee_set.append(self.print_atk_line(weap=weapon,nofeat=True))
        for i in range(len(melee_set[0:-1])):
            melee_set[i] += " or"

        ranged_set = []
        if "R" in self.weap_type(self.weap):
            base_atk_line = self.print_atk_line(nofeat=True)
            ranged_set.append(base_atk_line)
        for weapon in self.ranged_weaps:
            if weapon == self.weap:
                continue
            ranged_set.append(self.print_atk_line(weap=weapon,nofeat=True))
        for i in range(len(ranged_set[0:-1])):
            ranged_set[i] += " or"
        ranged_line = "Ranged {}".format(" or ".join(ranged_set))

        wordwrap = self.textwrap.TextWrapper(subsequent_indent="  ", width=textwidth)
        wordwrap_indent = self.textwrap.TextWrapper(initial_indent="  ", subsequent_indent="    ", width=textwidth)
        separator = "=" * textwidth

        out = []

        out.append(separator)
        out.append(wordwrap.fill("{}".format(self.name)))
        out.append(wordwrap.fill("{} {} {}".format(self.race, self.charClass, self.level)))
        out.append(wordwrap.fill("{} {} ({})".format(self.size, self.type.lower(), ', '.join(self.subtype))))
        out.append("")
        out.append(wordwrap.fill("Init {:+d}".format(self.get_init())))
        out.append(separator)
        out.append(wordwrap.fill("DEFENSE"))
        out.append(separator)
        out.append(wordwrap.fill(self.print_AC_line()))
        out.append(wordwrap.fill("hp {} ({})".format(self.get_hp(),self.print_HD())))
        out.append(wordwrap.fill(self.print_save_line()))
        if da_line:
            out.append(wordwrap.fill(da_line))
        out.append(separator)
        out.append(wordwrap.fill("OFFENSE"))
        out.append(separator)
        out.append(wordwrap.fill("Speed {} ft.".format(self.get_move())))
        if melee_set:
            out.append(wordwrap.fill("Melee {}".format(melee_set[0])))
            for melee in melee_set[1:]:
                out.append(wordwrap_indent.fill(melee))
        if ranged_set and not self.has("Raging"):
            out.append(wordwrap.fill("Ranged {}".format(ranged_set[0])))
            for ranged in ranged_set[1:]:
                out.append(wordwrap_indent.fill(ranged))
        if self.sa:
            out.append(wordwrap.fill("Special Attacks {}".format(", ".join(sorted(self.sa)))))
        out.append(separator)
        out.append(wordwrap.fill("STATISTICS"))
        out.append(separator)
        out.append(wordwrap.fill("Str {}, Dex {}, Con {}, Int {}, Wis {}, Cha {}".format(*stats)))
        out.append(wordwrap.fill("Base Atk {:+d}; CMB {:+d}; CMD {}".format(self.bab[0],self.CMB(),self.CMD())))
        out.append(wordwrap.fill(wordwrap.fill("Feats {}".format(', '.join(sorted(self.feat_list))))))
        if self.sq:
            out.append(wordwrap.fill("SQ {}".format(", ".join(sorted(self.sq)))))
        out.append(separator)

        return '\n'.join(out)

###################################################################

class Monster(Foundation):
    """Monster stats and data"""

    def __init__(self, name=None, side=1, AC=10, move=30, loc=[0,0], tilesize=[1,1], HD=1, type="Humanoid", subtype=[], size="Medium", hp=1, str=10, dex=10, con=10, int=10, wis=10, cha=10, feat_list=[], arcane=False, divine=False, CL=0, reach=5, fort=None, ref=None, will=None, hands=2):

        self.level = 0
        self.charClass = None
        self.HD = HD
        self.arcane = arcane
        self.divine = divine
        self.CL = CL
        self.weap_bon = 0
        self.fc = []

        Foundation.__init__(self, name, side, AC, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, size, reach, fort, ref, will, hands)

        self.set_bab()
        self.set_hit_die()

        if hp == 0:
            self.roll_hp_tot()

    def set_bab(self):

        if self.type in ["Construct", "Dragon", "Magical Beast", "Monstrous Humanoid", "Outsider"]:
            self.bab = range(self.HD, 1, -5)
            if not self.bab:
                self.bab = [self.HD]
        elif self.type in ["Aberration", "Animal", "Humanoid", "Ooze", "Plant", "Undead", "Vermin"]:
            self.bab = range(self.HD * 3 / 4, 1, -5)
            if not self.bab:
                self.bab = [self.HD * 3 / 4]
        else:
            self.bab = range(self.HD / 2, 1, -5)
            if not self.bab:
                self.bab = [self.HD / 2]

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