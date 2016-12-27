import copy
import sys
import random
import equip
import textwrap
import feat
import satk_list as satk
import ai as ai_class
import uuid


class Foundation:
    """Base stats and data"""

    def __init__(self, name, side, armor_class, move, loc, hp, tilesize, stg, dex, con, inl, wis, cha, feat_list, type_mon,
                 subtype, size, reach, fort, ref, will, hands, legs):
        self.name = name
        self.id = uuid.uuid4()
        self.model = False
        self.side = side
        self.ambi = False

        self.armor_class = armor_class
        self.move = move
        self.startloc = loc
        self.loc = loc
        self.hp = hp
        self.tilesize = tilesize
        self.stg = stg
        self.dex = dex
        self.con = con
        self.inl = inl
        self.wis = wis
        self.cha = cha
        self.feat_list = feat_list
        self.type_mon = type_mon
        self.subtype = subtype
        self.size = size
        self.reach = reach
        self.fort = fort
        self.ref = ref
        self.will = will
        self.hands = hands
        self.legs = legs

        self.ai = None

        self.race = ""
        self.bab = [0]
        self.hd = 0
        self.level = 0
        self.char_class = ""
        self.fc = []
        self.arcane = False
        self.divine = False
        self.hit_die = 10
        self.damage = 0
        self.temp_dmg = 0
        self.damage_con = "Normal"

        self.equip_list = []
        self.melee_weaps = []
        self.ranged_weaps = []
        self.slots = {"armor": None, "belts": None, "body": None, "chest": None, "eyes": None, "feet": None,
                      "hands": None, "head": None, "headband": None, "neck": None, "ring": [None, None],
                      "shoulders": None, "wield": [None for i in range(self.hands)], "wrists": None}
        self.unarmed = equip.Weapon(name="unarmed strike", group=["Monk", "Natural"], atk_damage=[1, 3])

        self.conditions = dict()

        self.ftr_wt = []
        self.ftr_mast = None

        self.rage_dur = 0

        self.ki_pool = 0
        self.ki_spent = 0
        self.ki_types = []

        self.rgr_fe = []

        self.sa = []
        self.sa_list = []
        self.sq = []
        self.sq_list = []
        self.da = []
        self.da_list = []
        self.vuln = []
        self.res = {}
        self.immune = []

        self.cast_stat = None

        self.spell_list_mem = [{} for i in range(0, 10)]
        self.spell_mem_max = [0 for i in range(0, 10)]
        self.sla_list = []
        self.max_spell_lvl = 0

        self.lang = []
        self.lang_spec = []

        self.dropped = []

    def __sizeof__(self):
        return object.__sizeof__(self) + \
               sum(sys.getsizeof(v) for v in self.__dict__.values())

    def copy(self):
        return copy.copy(self)

    def model_copy(self):
        model_copy = copy.copy(self)
        del model_copy.ai
        model_copy.model = True

        return model_copy

    ###################################################################
    #
    # Initialization functions

    def set_ai(self, mat):
        if self.ai is None:
            self.ai = ai_class.AI(self, mat)
        else:
            self.ai.mat = mat

    def set_tactic(self, tactic):
        if self.ai is None:
            pass
        else:
            self.ai.set_tactic(tactic)

    def set_targeting(self, target):
        if self.ai is None:
            pass
        else:
            self.ai.target = target

    ###################################################################
    #
    # General calculation functions

    def current_hp(self):
        return self.get_hp() - self.damage

    def range_pen(self, dist):
        pen = int(dist / self.weap_range()) * -2

        if pen < -10:
            pen = -10

        return pen

    @staticmethod
    def stat_bonus(stat):
        if stat >= 0:
            return int((stat - 10) / 2)
        else:
            return 0

    def tile_in_token(self, tile):
        x_dist = tile[0] - self.loc[0]
        y_dist = tile[1] - self.loc[1]

        return x_dist in range(0, self.tilesize[0]) and y_dist in range(0, self.tilesize[1])

    def two_weap_pen(self, weap, bon_calc=False, off=False, light=False):

        offhand = self.slots["wield"][1]

        off = ((weap == offhand and not bon_calc) or off)

        light = (("L" in self.weap_type(offhand) and not bon_calc) or light)

        if not self.has_offhand() and not bon_calc:
            return 0
        elif off:
            pen = -10
            pen += feat.two_weapon_fighting_bon(self)[1]
        else:
            pen = -6
            pen += feat.two_weapon_fighting_bon(self)[0]

        if light:
            pen += 2

        return pen

    ###################################################################
    #
    # Import functions

    def add_weapon(self, weapon, active=False, off=False):
        self.equip_list.append(weapon)

        if "M" in weapon.atk_type:
            self.melee_weaps.append(len(self.equip_list) - 1)
        if "R" in weapon.atk_type:
            self.ranged_weaps.append(len(self.equip_list) - 1)

        if active:
            self.set_weapon(len(self.equip_list) - 1)

        if off:
            self.set_off(len(self.equip_list) - 1)

    def add_armor(self, armor, active=False):
        self.equip_list.append(armor)
        if active:
            self.set_armor(len(self.equip_list) - 1)

    def add_shield(self, shield, active=False):
        self.equip_list.append(shield)
        if active:
            self.set_shield(len(self.equip_list) - 1)

    def add_spell_mem(self, spell, count=1):
        level_list = spell.lvl_parse()
        if self.char_class not in level_list:
            raise Exception("This spell cannot be used by class {}".format(self.char_class))

        spell_lev = level_list[self.char_class]
        spells_mem = self.spell_list_mem[spell_lev].values()
        if sum(i[1] for i in spells_mem) + count > self.spell_mem_max[spell_lev]:
            raise Exception("Not enough free spell slots of level {} to add spell".format(spell_lev))

        if spell.name not in self.spell_list_mem[spell_lev]:
            self.spell_list_mem[spell_lev][spell.name] = [spell, count]
        else:
            cur_count = self.spell_list_mem[spell_lev][spell.name][1]
            self.spell_list_mem[spell_lev][spell.name] = [spell, cur_count + count]

            ###################################################################
            #
            # Equipment data retrieval functions

    def item_type(self, val):
        return self.equip_list[val].item

    def default(self, val):
        if val is None:
            return True
        return self.equip_list[val].default

    def equip_unarmed(self):

        if self.char_class == "Monk":
            if self.level < 4:
                self.unarmed.atk_damage = [1, 6]
            elif self.level < 8:
                self.unarmed.atk_damage = [1, 8]
            elif self.level < 12:
                self.unarmed.atk_damage = [1, 10]
            elif self.level < 16:
                self.unarmed.atk_damage = [2, 6]
            elif self.level < 20:
                self.unarmed.atk_damage = [2, 8]
            else:
                self.unarmed.atk_damage = [2, 10]
        self.unarmed.default = True

        self.add_weapon(self.unarmed, active=True)

    def weap_basename(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.name

        return self.equip_list[val].name

    def weap_name(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.fullname()

        return self.equip_list[val].fullname()

    def weap_group(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.group

        return self.equip_list[val].group

    def weap_type(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.atk_type

        return self.equip_list[val].atk_type

    def weap_dmg(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.atk_damage

        return self.equip_list[val].atk_damage

    def weap_avg_dmg(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.atk_damage

        return self.equip_list[val].avg_dmg()

    def weap_range(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.weap_range

        return self.equip_list[val].weap_range

    def weap_crit_range(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            crit_rng = self.unarmed.crit_range
        else:
            crit_rng = self.equip_list[val].crit_range

        if feat.improved_critical(self, val):
            crit_rng = 21 - ((21 - crit_rng) * 2)

        return crit_rng

    def weap_crit_mult(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            crit_mult = self.unarmed.crit_mult
        else:
            crit_mult = self.equip_list[val].crit_mult

        if self.ftr_wm():
            crit_mult += 1

        return crit_mult

    def weap_bon(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.weap_bon

        return self.equip_list[val].weap_bon

    def weap_disarm(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.disarm

        return self.equip_list[val].disarm

    def weap_reach(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.reach

        return self.equip_list[val].reach

    def weap_trip(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.trip

        return self.equip_list[val].trip

    def weap_mwk(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.mwk

        return self.equip_list[val].mwk

    def weap_hands(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None or val < 0 or self.item_type(val) != "weapon":
            return self.unarmed.hands

        return self.equip_list[val].hands

    def has_weapon(self):
        return self.weap_name() != "unarmed strike"

    def has_offhand(self):
        main = self.slots["wield"][0]
        offhand = self.slots["wield"][1]

        return offhand is not None and offhand != main and self.item_type(offhand) == "weapon"

    def curr_weap(self):
        return self.slots["wield"][0]

    # weap_list: returns list of weapons wielded (as array for future functionality expansion)

    def weap_list(self, no_array=False):
        wield_list = []
        i = 0

        while i < len(self.slots["wield"]):  # Using while loop in order to vary index step by weapon hands
            item = self.slots["wield"][i]
            if item is not None and self.item_type(item) == "weapon":
                if no_array:
                    wield_list.append(item)
                else:
                    wield_list.append([item])
            i += self.weap_hands(item)

        return wield_list

    def weap_list_all(self):
        wield_list = []

        for item in range(len(self.equip_list)):
            if self.equip_list[item] is not None and self.item_type(item) == "weapon":
                wield_list.append(item)

        return wield_list

    def owns_weapon(self, weap_name):
        for item in range(len(self.equip_list)):
            if self.equip_list[item] is not None and self.item_type(item) == "weapon" and self.weap_name(
                    item) == weap_name:
                return [True, item]

        return [False, None]

    ##################################################################################

    def armor_name(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return ""

        return self.equip_list[val].fullname()

    def armor_type(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return ""

        return self.equip_list[val].weap_type

    def armor_armor_bon(self, val=None, public=False):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        bon = self.equip_list[val].armor_bon

        if not public:
            bon += self.equip_list[val].ench_bon

        return bon

    def armor_max_dex(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None:
            return 99  # no max dex when unarmored
        if val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].max_dex

    def armor_armor_check(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].armor_check

    def armor_asf(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].asf

    def armor_ench_bon(self, val=None):
        if val is None:
            val = self.slots["armor"]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].ench_bon

    def has_armor(self):
        return self.armor_name() != ""

    ##################################################################################

    def shield_name(self, val=None):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return ""

        return self.equip_list[val].fullname()

    def shield_type(self, val=None):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return ""

        return self.equip_list[val].type

    def shield_shield_bon(self, val=None, public=False):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        bon = self.equip_list[val].shield_bon

        if not public:
            bon += self.equip_list[val].ench_bon

        return bon

    def shield_armor_check(self, val=None):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].armor_check

    def shield_ench_bon(self, val=None):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].ench_bon

    def shield_hands(self, val=None):
        if val is None:
            val = self.slots["wield"][1]
        if val is None or val < 0 or self.item_type(val) != "armor":
            return 0

        return self.equip_list[val].hands

    def has_shield(self):
        return self.shield_name() != ""

    ###################################################################
    #
    # Spell data retrieval functions

    def spell_list(self, spl_type="All", target="All", min_level=0, max_level="Max"):

        spell_list = self.mem_spell_list(spl_type, target)

        return spell_list

    def mem_spell_list(self, spl_type="All", target="All", min_level=0, max_level="Max"):
        spell_list = []
        spell_list_temp = []

        if max_level == "Max":
            max_level = self.max_spell_lvl

        if max_level > 9:
            max_level = 9

        if min_level > 9:
            min_level = 9

        if min_level > max_level:
            min_level = max_level

        if max_level < 0:
            max_level = self.max_spell_lvl + max_level
            if max_level < 0:
                max_level = 0

        if min_level < 0:
            min_level = max_level + min_level
            if min_level < 0:
                min_level = 0

        for sl in range(max_level, min_level - 1, -1):
            spell_list_temp = self.spell_list_mem[sl].copy()
            if len(spell_list_temp) == 0:
                continue

            for spell_name, spells_memd in spell_list_temp.items():

                [spell, count] = spells_memd
                # print("spell: {}, count: {}".format(spell.name,count))
                if count <= 0:
                    continue
                if spl_type == "All":
                    spell_list.append(spell)
                    continue
                if spl_type == "Damage" and spell.dmg:
                    spell_list.append(spell)
                    continue
                if spl_type == "Buff" and spell.buff:
                    spell_list.append(spell)
                    continue
                if spl_type == "Debuff" and spell.debuff:
                    spell_list.append(spell)
                    continue

            spell_list_temp = spell_list[:]
            spell_list = []

            for spell in spell_list_temp:
                if target == "All":
                    spell_list.append(spell)
                    continue
                if target == "Single" and spell.is_single():
                    spell_list.append(spell)
                    continue
                if target == "Multi" and spell.is_multi():
                    spell_list.append(spell)
                    continue

        return spell_list

    ###################################################################
    #
    # Attack selection functions

    def avg_weap_dmg(self, weap, target, dist=0, full_attack=True, offhand=False, oh_calc=False, light=False,
                     fob=False):

        avg_dmg = 0
        weap_bon = self.get_atk_bon(dist, full_attack, target.type_mon, target.subtype, weap=weap, offhand=offhand,
                                    bon_calc=oh_calc, light=light, fob=fob)
        dmg_bon = self.get_base_dmg_bon(dist, target.type_mon, target.subtype, weap=weap, offhand=offhand)
        armor_class = target.get_ac(self.type_mon, self.subtype, atk_type=self.weap_type(weap))
        avg_base_dmg = self.weap_avg_dmg(weap)

        for attack in weap_bon:
            chance_to_hit = (21 - (armor_class - attack)) / 20.0
            if chance_to_hit <= 0:
                chance_to_hit = 0.05
            if chance_to_hit >= 1:
                chance_to_hit = 0.95
            chance_to_threat = (21 - self.weap_crit_range(weap)) / 20.0
            if chance_to_threat <= 0:
                chance_to_threat = 0.05
            if chance_to_threat >= chance_to_hit:
                chance_to_threat = chance_to_hit

            avg_hit_dmg = avg_base_dmg + dmg_bon

            if avg_hit_dmg < 0:
                avg_hit_dmg = 0

            avg_crit_bonus_dmg = avg_base_dmg * (self.weap_crit_mult(weap) - 1)

            avg_dmg += (chance_to_hit * avg_hit_dmg) + (chance_to_threat * chance_to_hit * avg_crit_bonus_dmg)

        return avg_dmg

    def avg_weap_dmgs(self, target, dist=0, weap_list=None, full_attack=True, offhand=False, prn=False, oh_calc=False,
                      light=False, fob=False):
        if weap_list is None:
            weap_list = self.weap_list_all()

        avg_dmgs = []

        for weap_i in weap_list:
            avg_dmg = self.avg_weap_dmg(weap_i, target, dist, full_attack, offhand, oh_calc, light, fob)

            avg_dmgs.append([weap_i, avg_dmg])

        avg_dmgs.sort(key=lambda i: i[1], reverse=True)

        if not prn:
            return avg_dmgs
        else:
            output_list = dict()
            for [weap, avg] in avg_dmgs:
                output_list[self.weap_name(weap)] = avg

            return output_list

    def best_weap(self, target, dist=0, weap_list=None, full_attack=True, offhand=False, dmg_val=False, fob=False):
        if weap_list is None:
            weap_list = self.weap_list()

        if dmg_val:
            return self.avg_weap_dmgs(target, dist, weap_list, full_attack, offhand=offhand, fob=fob)[0]
        else:
            return self.avg_weap_dmgs(target, dist, weap_list, full_attack, offhand=offhand, fob=fob)[0][0]

    #############################
    #
    # Melee attack selection functions

    def best_melee_opt(self, target, dist=0, full_attack=True, prn=False):
        melee_opts = []

        best_weap_val = self.best_melee_equip(target, dist, full_attack, dmg_val=True)

        if best_weap_val:
            best_weap = ["weap", best_weap_val[0], best_weap_val[1]]
            melee_opts.append(best_weap)

        if "flurry of blows" in self.sa and full_attack:
            best_fob_val = self.best_melee_fob(target, dist, full_attack, dmg_val=True)

            if best_fob_val:
                best_fob = ["fob", best_fob_val[0], best_fob_val[1]]
                melee_opts.append(best_fob)

        melee_opts.sort(key=lambda i: i[2], reverse=True)

        if not prn:
            return melee_opts[0]
        else:
            output_list = dict()
            for [atk_type, weap, avg] in melee_opts:
                weap_name = ""
                if atk_type == "weap":
                    if type(weap) is list:
                        weap_name = self.weap_name(weap[0]) + ' and ' + self.weap_name(weap[1])
                    else:
                        weap_name = self.weap_name(weap)
                elif atk_type == "fob":
                    weap_name = self.weap_name(weap) + " flurry of blows"
                output_list[weap_name] = avg

            return output_list

    def best_melee_weap(self, target, dist=0, full_attack=True, dmg_val=False):
        if not self.melee_weaps:
            return None
        else:
            return self.best_weap(target, dist, self.melee_weaps, full_attack, dmg_val=dmg_val)

    def best_mainhand_weap(self, target, dist=0, full_attack=True, dmg_val=False):
        if not self.melee_weaps:
            return None

        mainhand_weaps = []

        for weap in self.weap_list_all():
            if self.weap_hands(weap) == 1 and "M" in self.weap_type(weap):
                mainhand_weaps.append(weap)

        if not mainhand_weaps:
            return None

        return self.best_weap(target, dist, mainhand_weaps, full_attack, False, dmg_val=dmg_val)

    def best_twohand_weap(self, target, dist=0, full_attack=True, dmg_val=False):
        if not self.melee_weaps:
            return None

        twohand_weaps = []

        for weap in self.weap_list_all():
            if self.weap_hands(weap) == 2 and "M" in self.weap_type(weap):
                twohand_weaps.append(weap)

        if not twohand_weaps:
            return None

        return self.best_weap(target, dist, twohand_weaps, full_attack, False, dmg_val=dmg_val)

    def best_dual_wield(self, target, dist=0, full_attack=True, dmg_val=False, prn=False):
        if len(self.melee_weaps) < 2:
            return None

        dw_weaps = []

        for weap1 in self.weap_list_all():
            for weap2 in self.weap_list_all():
                if weap1 == weap2:
                    continue
                if self.weap_hands(weap1) == 1 and "M" in self.weap_type(weap1) and self.weap_hands(
                        weap2) == 1 and "M" in self.weap_type(weap2):
                    dw_weaps.append([weap1, weap2])

        if not dw_weaps:
            return None

        dw_weaps_dmg = []

        for [weap1, weap2] in dw_weaps:
            light = ("L" in self.weap_type(weap2))
            weap1_dmg = self.avg_weap_dmg(weap1, target, dist, full_attack, False, True, light)
            weap2_dmg = self.avg_weap_dmg(weap1, target, dist, full_attack, True, True, light)
            dw_weaps_dmg.append([[weap1, weap2], weap1_dmg + weap2_dmg])

        dw_weaps_dmg.sort(key=lambda i: i[1], reverse=True)

        if not prn:
            if dmg_val:
                return dw_weaps_dmg[0]
            else:
                return dw_weaps_dmg[0][0]
        else:
            output_list = dict()
            for [weap, avg] in dw_weaps_dmg:
                if type(weap) is list:
                    weap_name = self.weap_name(weap[0]) + ' and ' + self.weap_name(weap[1])
                else:
                    weap_name = self.weap_name(weap)
                output_list[weap_name] = avg

            return output_list

    def best_melee_equip(self, target, dist=0, full_attack=True, prn=False, dmg_val=False):
        if not self.melee_weaps:
            return None

        best_opts = []

        #############################
        #
        # One-handed single-weapon attack

        best_opts.append(self.best_mainhand_weap(target, dist, full_attack, True))

        #############################
        #
        # Two-handed single-weapon attack

        best_opts.append(self.best_twohand_weap(target, dist, full_attack, True))

        #############################
        #
        # Dual-wield attack

        best_opts.append(self.best_dual_wield(target, dist, full_attack, True))

        while None in best_opts:
            best_opts.remove(None)

        best_opts.sort(key=lambda i: i[1], reverse=True)

        if not prn:
            if dmg_val:
                return best_opts[0]
            else:
                return best_opts[0][0]
        else:
            output_list = dict()
            for [weap, avg] in best_opts:
                if type(weap) is list:
                    weap_name = self.weap_name(weap[0]) + ' and ' + self.weap_name(weap[1])
                else:
                    weap_name = self.weap_name(weap)
                output_list[weap_name] = avg

            return output_list

    #############################
    #
    # Melee class attack selection functions

    def best_melee_fob(self, target, dist=0, prn=False, dmg_val=False):
        if not self.melee_weaps:
            return None

        monk_melee_weaps = []

        for weap in self.melee_weaps:
            if "Monk" in self.weap_group(weap):
                monk_melee_weaps.append(weap)

        if not monk_melee_weaps:
            return None

        return self.best_weap(target, dist, monk_melee_weaps, full_attack=True, offhand=False, dmg_val=dmg_val,
                              fob=True)

    #############################
    #
    # Ranged attack selection functions

    def best_ranged_weap(self, target, dist=0, full_attack=True):
        if not self.ranged_weaps:
            return None
        else:
            return self.best_weap(target, dist, self.ranged_weaps, full_attack)

            ###################################################################
            #
            # Value-setting functions

    def set_weapon(self, weap_num):
        if type(weap_num) is list:
            self.set_weapon(weap_num[0])
            self.set_off(weap_num[1])
            return

        if self.weap_hands(weap_num) == 1:
            self.slots["wield"][0] = weap_num
            offhand = self.slots["wield"][1]
            if offhand and self.weap_hands(offhand) == 2:
                self.slots["wield"][1] = None
        else:
            offhand = self.slots["wield"][1]
            if offhand and self.weap_hands(offhand) == 1:
                raise Exception("Cannot equip two-handed weapon: offhand occupied")
            else:
                self.slots["wield"][0] = weap_num
                self.slots["wield"][1] = weap_num

    def set_off(self, weap_num, hand=1):
        if self.weap_hands(weap_num) == 2:
            raise Exception("Cannot equip two-handed weapon to offhand")
        if hand >= self.hands:
            raise Exception("Cannot equip offhand weapon to hand {}: does not exist".format(hand))
        offhand = self.slots["wield"][hand]
        if offhand and self.weap_hands(offhand) == 2:
            raise Exception("Cannot equip offhand weapon: two-handed weapon equipped")
        self.slots["wield"][hand] = weap_num

    def set_armor(self, armor_num):
        self.slots["armor"] = armor_num

    def set_shield(self, shield_num, hand=1):
        if hand >= self.hands:
            raise Exception("Cannot equip shield to hand {}: does not exist".format(hand))
        elif self.shield_hands(shield_num) == 2 and hand > self.hands:
            raise Exception("Cannot equip two-handed shield to hand {}: hand {} does not exist".format(hand, hand + 1))
        offhand = self.slots["wield"][hand]
        if offhand and self.item_type(offhand) == "weapon" and self.weap_hands(offhand) == 2:
            raise Exception("Cannot equip shield: two-handed weapon equipped")
        self.slots["wield"][hand] = shield_num
        if self.shield_hands(shield_num) == 2:
            self.slots["wield"][hand + 1] = shield_num

    def drop(self, slot):
        slot_loc = slot.split(',')
        if len(slot_loc) == 1:
            place = slot_loc[0]
            i = self.slots[place]
            if not self.default(i):
                gear = self.equip_list[i]
                self.slots[place] = None
                if gear.item == "weapon":
                    if "M" in gear.atk_type:
                        self.melee_weaps.remove(i)
                    elif "R" in gear.atk_type:
                        self.ranged_weaps.remove(i)
                self.equip_list[i] = None
                return gear
            else:
                return None
        elif len(slot_loc) == 2:
            place = slot_loc[0]
            num = int(slot_loc[1])
            i = self.slots[place][num]
            if not self.default(i):
                gear = self.equip_list[i]
                self.slots[place][num] = None
                if gear.hands == 2:
                    self.slots[place][num + 1] = None
                if gear.item == "weapon":
                    if "M" in gear.atk_type:
                        self.melee_weaps.remove(i)
                    elif "R" in gear.atk_type:
                        self.ranged_weaps.remove(i)
                self.equip_list[i] = None
                return gear
            else:
                return None

    def take_damage(self, dmg):

        self.damage = self.damage + dmg

        self.check_hp()

    def check_hp(self):
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

    def set_condition(self, condition, duration=14400):
        if condition not in self.conditions.keys():
            if condition == "Fatigued" and "Exhausted" in self.conditions.keys():
                self.conditions["Exhausted"] = max(self.conditions["Exhausted"], duration)
            elif condition == "Stunned":
                self.conditions["Stunned"] = duration
                for i in range(self.hands):
                    self.drop("wield,{}".format(i))
            else:
                self.conditions[condition] = duration
        elif condition == "Fatigued":
            self.conditions["Exhausted"] = max(self.conditions["Fatigued"], duration)

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

    def add_vuln(self, elem):
        if elem not in self.vuln:
            self.vuln.append(elem)

    def del_vuln(self, elem):
        if elem in self.vuln:
            self.vuln.remove(elem)

    def add_res(self, elem, amt):
        if elem not in self.res:
            self.res[elem] = amt

    def del_res(self, elem):
        if elem in self.res:
            del self.res[elem]

    def add_imm(self, elem):
        if elem not in self.immune:
            self.immune.append(elem)

    def del_imm(self, elem):
        if elem in self.immune:
            self.immune.remove(elem)

    def cast(self, spell):
        sl = spell.lvl_parse()[self.char_class]
        spl_name = spell.name

        if spl_name in self.spell_list_mem[sl]:
            self.spell_list_mem[sl][spl_name][1] -= 1

            ###################################################################
            #
            # Generic class ability functions

    def evasion(self):
        return "evasion" in self.da or "improved evasion" in self.da

    def trap_sense_bon(self):
        if self.char_class != "Barbarian" and self.char_class != "Rogue":
            return 0
        else:
            return int(self.level / 3)

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
            self.set_condition("Raging", self.barbarian_rage_rds())
            self.rage_dur = 0
            if "R" in self.weap_type():
                self.set_weapon(self.best_melee_weap(None))
            return True
        else:
            return False

    def drop_rage(self):
        self.drop_condition("Raging")
        if self.level < 17:
            self.set_condition("Fatigued", 2 * self.rage_dur)
        self.check_hp()

    def rage_bon(self):
        if self.char_class != "Barbarian":
            return 0
        elif self.level < 11:
            return 4
        elif self.level < 20:
            return 6
        else:
            return 8

    def rage_bon_indom_will(self):
        if self.char_class != "Barbarian" or self.level < 14:
            return 0
        else:
            return 4

            # Note: conditional save bonuses not yet implemented

    def barbarian_dr(self):
        return max(int((self.level - 4) / 3), 0)

    ###################################################################
    #
    # Fighter class ability functions

    def fighter_bravery(self):
        if self.char_class != "Fighter":
            return 0
        return int((self.level + 2) / 4)

        # Note: conditional save bonuses not yet implemented

    def fighter_armor_training(self):
        if self.char_class != "Fighter":
            return 0
        return int((self.level + 1) / 4)

    def set_fighter_weap_train(self, groups):
        if self.char_class != "Fighter":
            raise Exception("Cannot set Fighter options for non-Fighter")
        if len(groups) != int((self.level - 1) / 4):
            raise Exception("Wrong number of groups set for Weapon Training")
        self.ftr_wt = groups

        train_text = []
        for group in groups:
            train_text.append("{} {:+d}".format(group.lower(), groups[::-1].index(group) + 1))
        self.add_sa("weapon training ({})".format(', '.join(train_text)))

    def fighter_wt_bon(self, groups):
        if self.char_class != "Fighter":
            return 0
        matching_groups = list(set(groups).intersection(self.ftr_wt))
        if not matching_groups:
            return 0
        wt = self.ftr_wt[::-1]
        wt_bon = map(lambda x: wt.index(x) + 1, matching_groups)
        return max(wt_bon)

    def set_fighter_weap_mast(self, weapon):
        if self.char_class != "Fighter":
            raise Exception("Cannot set Fighter options for non-Fighter")
        self.ftr_mast = weapon
        self.add_sa("weapon mastery ({})".format(weapon))

    def ftr_am(self):
        return self.char_class == "Fighter" and self.level >= 19 and (self.has_armor() or self.has_shield())

    def ftr_wm(self):
        return self.char_class == "Fighter" and self.level >= 20 and self.weap_basename() == self.ftr_mast

    ###################################################################
    #
    # Monk class ability functions

    def monk_ki_tot(self):
        if self.char_class != "Monk":
            raise Exception("Cannot set Monk options for non-Monk")
        if self.level >= 4:
            self.ki_pool = int(self.level / 2) + self.stat_bonus(self.wistot())
        else:
            self.ki_pool = 0

            ###################################################################
            #
            # Ranger class ability functions

    def set_ranger_favored_enemy(self, types):
        if self.char_class != "Ranger":
            raise Exception("Cannot set Ranger options for non-Ranger")
        tot_bon_count = int(self.level * 4 / 5) + 2
        if sum([x[1] for x in types]) != tot_bon_count:
            raise Exception("Wrong bonus assignment for Favored Enemy")
        self.rgr_fe = types

        fe_text = []
        for type_mon in types:
            if len(type_mon) == 3:
                if type_mon[0] == "Outsider":
                    text = "{} {} {:+d}".format(type_mon[2].lower(), type_mon[0].lower(), type_mon[1])
                else:
                    text = "{} {:+d}".format(type_mon[2].lower(), type_mon[1])
            else:
                text = "{} {:+d}".format(type_mon[0].lower(), type_mon[1])
            fe_text.append(text)

        fe_text = sorted(fe_text)
        self.add_sa("favored enemy ({})".format(', '.join(fe_text)))

    def ranger_fe_types(self):
        return [x[0] for x in self.rgr_fe]

    def ranger_fe_bon(self, type_mon, subtype=None):
        if subtype is None:
            subtype = []
        match_types = [i for i, x in enumerate(self.rgr_fe) if x[0] == type_mon]

        if type_mon not in ["Humanoid", "Outsider"]:
            if match_types:
                return self.rgr_fe[match_types[0]][1]
            else:
                return 0
        else:
            match_subtypes = [i for i, x in enumerate(self.rgr_fe) if x[0] == type_mon and x[2] in subtype]

            if match_subtypes:
                return self.rgr_fe[match_subtypes[0]][1]
            else:
                return 0

                ###################################################################
                #
                # Statistic value functions

    @staticmethod
    def add_bon(bon_list, bon_type, bon_val):
        if bon_type not in bon_list:
            bon_list[bon_type] = bon_val
        else:
            if bon_type in ["dodge", "racial", "untyped", "circumstance", "feat", "condition", "class", "weapon"]:
                bon_list[bon_type] = bon_list[bon_type] + bon_val
            else:
                bon_list[bon_type] = max(bon_list[bon_type], bon_val)

    #############################
    #
    # Base stat functions

    def strtot(self):
        if self.stg is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.stg)

        if self.has("Exhausted"):
            self.add_bon(stat_bon, "untyped", -6)
        if self.has("Fatigued"):
            self.add_bon(stat_bon, "untyped", -2)
        if self.has("Raging"):
            self.add_bon(stat_bon, "morale", self.rage_bon())

        return sum(stat_bon.values())

    def dextot(self):
        if self.dex is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.dex)

        if self.has("Exhausted"):
            self.add_bon(stat_bon, "untyped", -6)
        if self.has("Fatigued"):
            self.add_bon(stat_bon, "untyped", -2)

        return sum(stat_bon.values())

    def contot(self):
        if self.con is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.con)

        if self.has("Raging"):
            self.add_bon(stat_bon, "morale", self.rage_bon())

        return sum(stat_bon.values())

    def inttot(self):
        if self.inl is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.inl)

        return sum(stat_bon.values())

    def wistot(self):
        if self.wis is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.wis)

        return sum(stat_bon.values())

    def chatot(self):
        if self.cha is None:
            return -999

        stat_bon = dict()

        self.add_bon(stat_bon, "stat", self.cha)

        return sum(stat_bon.values())

    def casttot(self):
        if self.cast_stat is None:
            return -999
        elif self.cast_stat == "i":
            return self.inttot()
        elif self.cast_stat == "w":
            return self.wistot()
        elif self.cast_stat == "h":
            return self.chatot()

    #############################
    #
    # armor_class functions

    def get_ac_bons(self, type_mon=None, subtype=None, atk_type="M", public=False):

        ac_bon = dict()

        stat_bon = min(self.armor_max_dex(), self.stat_bonus(self.dextot()))

        if not self.has("Stunned"):
            self.add_bon(ac_bon, "Dex", stat_bon)

        #############################
        #
        # Equipment bonus

        self.add_bon(ac_bon, "armor", self.armor_armor_bon(public=public))

        self.add_bon(ac_bon, "shield", self.shield_shield_bon(public=public))

        #############################
        #
        # Class bonuses

        if self.char_class == "Monk":
            self.add_bon(ac_bon, "Wis", self.stat_bonus(self.wistot()))
            self.add_bon(ac_bon, "monk", int(self.level / 4))

        #############################
        #
        # Feat bonuses

        self.add_bon(ac_bon, "dodge", feat.dodge_bon(self))

        self.add_bon(ac_bon, "dodge", feat.favored_defense_bon(self, type_mon, subtype))

        #############################
        #
        # Condition bonuses

        if self.has("Prone"):
            if "M" in atk_type:
                self.add_bon(ac_bon, "condition", -4)
            elif "R" in atk_type:
                self.add_bon(ac_bon, "condition", -4)

        if self.has("Raging"):
            self.add_bon(ac_bon, "rage", -2)

        if self.has("Stunned"):
            self.add_bon(ac_bon, "condition", -2)

        return ac_bon

    def get_ac(self, type_mon=None, subtype=None, ff=False, touch=False, atk_type="M", public=False):

        temp_ac_bons = self.get_ac_bons(type_mon=type_mon, subtype=subtype, atk_type=atk_type, public=public)

        if self.has("Flat-footed") or ff:
            temp_ac_bons = self.get_ff_ac_bons(temp_ac_bons)
        if touch:
            temp_ac_bons = self.get_touch_ac_bons(temp_ac_bons)

        return 10 + sum(temp_ac_bons.values())

    def get_ff_ac_bons(self, temp_ac_bons):

        if not self.uncanny_dodge():
            temp_ac_bons.pop("Dex", None)
            temp_ac_bons.pop("dodge", None)

        return temp_ac_bons

    # noinspection PyMethodMayBeStatic
    def get_touch_ac_bons(self, temp_ac_bons):

        temp_ac_bons.pop("armor", None)
        temp_ac_bons.pop("natural", None)
        temp_ac_bons.pop("shield", None)

        return temp_ac_bons

    #############################
    #
    # AoO functions

    def can_aoo(self):

        active_check = self.is_active()

        if not active_check[0] or active_check[1] == "Disabled":
            return False

        if self.has("Flat-footed") and not self.uncanny_dodge():
            return False

        if "R" in self.weap_type() and not feat.snap_shot(self):
            return False

        return True

    def get_aoo_count(self):
        if feat.combat_reflexes(self):
            return self.stat_bonus(self.dextot())
        else:
            return 1

    #############################
    #
    # Attack roll functions

    def get_atk_bon(self, dist, full_attack, type_mon, subtype, weap=None, nofeat=False, offhand=False, fob=False,
                    bon_calc=False, off=False, light=False):
        if weap is None:
            weap = self.slots["wield"][0]

        atk_bon = dict()

        if "Monk" not in self.weap_group(weap):
            fob = False  # just to be safe

        if fob:  # flurry of blows BAB
            bab = [i - 2 for i in range(self.level, 0, -5)]
            bab.insert(1, self.level - 2)
            if self.level >= 8:
                bab.insert(3, self.level - 7)
                if self.level >= 15:
                    bab.insert(5, self.level - 12)

        elif offhand:  # offhand BAB
            bab = [self.bab[0]]
            if feat.two_weapon_fighting_imp(self):
                bab.append(self.bab[0] - 5)
                if feat.two_weapon_fighting_greater(self):
                    bab.append(self.bab[0] - 10)
        else:  # normal mainhand BAB
            bab = self.bab

        #############################
        #
        # Stat bonus

        if "M" in self.weap_type(weap):
            if feat.weapon_finesse(self) and feat.weapon_finesse_weap(self, weap):
                self.add_bon(atk_bon, "stat", self.stat_bonus(self.dextot()))
                if self.has_shield():
                    self.add_bon(atk_bon, "shield", self.shield_armor_check())
            else:
                self.add_bon(atk_bon, "stat", self.stat_bonus(self.strtot()))
            self.add_bon(atk_bon, "untyped", self.two_weap_pen(weap, bon_calc=bon_calc, off=offhand, light=light))
        elif "R" in self.weap_type(weap):
            self.add_bon(atk_bon, "stat", self.stat_bonus(self.dextot()))
            self.add_bon(atk_bon, "untyped", self.range_pen(dist))

        #############################
        #
        # Class bonus

        #############################
        #
        # Feat bonuses, all attacks

        if not nofeat:

            if "M" in self.weap_type():
                self.add_bon(atk_bon, "feat", feat.power_attack_pen(self))
            elif "R" in self.weap_type():
                self.add_bon(atk_bon, "feat", feat.deadly_aim_pen(self))
                if full_attack:
                    self.add_bon(atk_bon, "feat", feat.rapid_shot_pen(self))

        if feat.weapon_focus(self, weap):
            self.add_bon(atk_bon, "feat", 1)

        atk_bon = self.get_attack_roll_mods(atk_bon, dist, full_attack, type_mon, subtype, weap, nofeat)

        atk_bon_tot = sum(atk_bon.values())

        atk_bon_list = list(map(lambda x: x + atk_bon_tot, bab))

        #############################
        #
        # Feat bonuses, single attacks

        if not nofeat:
            if "R" in self.weap_type():
                if full_attack:
                    if feat.rapid_shot(self):
                        atk_bon_list.insert(0, atk_bon_list[0])
                else:
                    atk_bon_list[0] = atk_bon_list[0] + feat.bullseye_shot_bon(self)

        if full_attack:
            return atk_bon_list
        else:
            return atk_bon_list[0:1]

    def cmb(self, dist=5, type_mon=None, subtype=None, weap=None, nofeat=False, man=""):

        cmb = dict()

        if "maneuver training" in self.sq:
            self.add_bon(cmb, "BAB", self.level)
        else:
            self.add_bon(cmb, "BAB", self.bab[0])

        if feat.weapon_finesse(self) and feat.weapon_finesse_weap(self, weap) and man in ["Disarm", "Sunder", "Trip"]:
            self.add_bon(cmb, "stat", self.stat_bonus(self.dextot()))
            if self.has_shield():
                self.add_bon(cmb, "shield", self.shield_armor_check())
        else:
            self.add_bon(cmb, "stat", self.stat_bonus(self.strtot()))

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

        self.add_bon(cmb, "size", size_bon)

        cmb = self.get_attack_roll_mods(cmb, dist, False, type_mon, subtype, weap, nofeat)

        if man == "Disarm":
            self.add_bon(cmb, "feat", feat.improved_disarm_bon(self))
            if self.weap_name(weap) == "unarmed strike":
                self.add_bon(cmb, "untyped", -4)
            if self.weap_disarm():
                self.add_bon(cmb, "weapon", 2)
        elif man == "Trip":
            self.add_bon(cmb, "feat", feat.improved_trip_bon(self))

        cmb_tot = sum(cmb.values())

        return cmb_tot

    def get_attack_roll_mods(self, atk_bon, dist, full_attack, type_mon, subtype, weap=None, nofeat=False):

        #############################
        #
        # Enchantment/masterwork bonus

        if self.weap_mwk(weap):
            if self.weap_bon(weap) == 0:
                self.add_bon(atk_bon, "enhancement", 1)
            else:
                self.add_bon(atk_bon, "enhancement", self.weap_bon(weap))

        #############################
        #
        # Class bonuses, all attacks

        if self.char_class == "Fighter" and self.level >= 5:
            self.add_bon(atk_bon, "untyped", self.fighter_wt_bon(self.weap_group(weap)))

        if self.char_class == "Ranger":
            self.add_bon(atk_bon, "untyped", self.ranger_fe_bon(type_mon, subtype))

        #############################
        #
        # Feat bonuses

        if not nofeat:

            if "M" in self.weap_type():
                pass
            elif "R" in self.weap_type():
                if dist < 30:
                    self.add_bon(atk_bon, "feat", feat.pbs_bon(self))

        #############################
        #
        # Condition bonuses

        if self.has("Prone"):

            if "M" in self.weap_type():
                self.add_bon(atk_bon, "condition", -4)

        return atk_bon

    #############################
    #
    # cl functions

    def cl(self):

        cl = dict()

        if self.char_class in ["Bard", "Cleric", "Druid", "Sorcerer", "Wizard"]:
            self.add_bon(cl, "base", self.level)
        elif self.char_class in ["Paladin", "Ranger"] and self.level >= 4:
            self.add_bon(cl, "base", self.level - 3)
        else:
            return 0

        cl_tot = sum(cl.values())

        return cl_tot

    #############################
    #
    # cmd functions

    def cmd(self, type_mon=None, subtype=None, ff=False, man=None):

        cmd = dict()

        if "maneuver training" in self.sq:
            self.add_bon(cmd, "BAB", self.level)
        else:
            self.add_bon(cmd, "BAB", self.bab[0])

        self.add_bon(cmd, "Str", self.stat_bonus(self.strtot()))

        self.add_bon(cmd, "Dex", self.stat_bonus(self.dextot()))

        #############################
        #
        # Class bonuses

        if self.char_class == "Monk":
            self.add_bon(cmd, "Wis", self.stat_bonus(self.wistot()))
            self.add_bon(cmd, "monk", int(self.level / 4))

        #############################
        #
        # Condition bonuses

        if self.has("Stunned"):
            self.add_bon(cmd, "condition", -4)

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

        self.add_bon(cmd, "size", size_bon)

        if man == "Disarm":
            self.add_bon(cmd, "feat", feat.improved_disarm_bon(self))
        elif man == "Trip":
            self.add_bon(cmd, "feat", feat.improved_trip_bon(self))
            if self.legs > 2:
                self.add_bon(cmd, "untyped", (self.legs - 2) * 2)

        ac_bons = self.get_ac_bons(type_mon, subtype)

        if self.has("Flat-footed") or ff:
            ac_bons = self.get_ff_ac_bons(ac_bons)

        for key in ac_bons.keys():
            if key in ["circumstance", "deflection", "dodge", "insight", "luck", "morale", "profane", "sacred"]:
                self.add_bon(cmd, key, ac_bons[key])

        cmd_tot = 10 + sum(cmd.values())

        return cmd_tot

    #############################
    #
    # Concentration functions

    def concentration(self):

        conc = dict()

        self.add_bon(conc, "cl", self.cl())
        self.add_bon(conc, "Stat", self.stat_bonus(self.casttot()))

        conc_tot = sum(conc.values())

        return conc_tot

    #############################
    #
    # Condition functions

    def has(self, condition):
        return condition in self.conditions.keys() and self.conditions[condition] != 0

    def round_pass(self):
        if not self.model:
            self.ai.update_model()
        expire_conditions = []

        cond = dict(self.conditions)
        for condition in cond.keys():
            if condition == "Raging":
                self.rage_dur += 1
            if self.conditions[condition] > 0:
                self.conditions[condition] -= 1
            if self.conditions[condition] == 0:
                expire_conditions.append(condition)
                if condition == "Raging":
                    self.drop_rage()
                else:
                    self.drop_condition(condition)

        for spec_atk in self.sa_list:
            spec_atk.round()

        return [expire_conditions]

    def is_active(self):
        self.check_hp()

        if self.damage_con not in ["Normal", "Disabled"]:
            return [False, self.damage_con]
        else:
            return [True, self.damage_con]

    def can_act(self):

        active_check = self.is_active()

        if not active_check[0]:
            return active_check

        disable_list = ["Stunned", "Paralyzed", "Petrified", "Unconscious"]

        for condition in disable_list:
            if self.has(condition):
                return [False, condition]
        else:
            return [True, ""]

    #############################
    #
    # Damage bonus functions

    def get_base_dmg_bon(self, dist, type_mon, subtype, weap=None, offhand=False, nofeat=False):

        dmg_bon = dict()

        #############################
        #
        # Enchantment/masterwork bonus

        self.add_bon(dmg_bon, "enhancement", self.weap_bon(weap))

        #############################
        #
        # Stat bonus

        str_bon = self.stat_bonus(self.strtot())
        dex_bon = self.stat_bonus(self.dextot())

        if self.has_offhand() and not offhand:
            if str_bon > 0:
                self.add_bon(dmg_bon, "Str", int((str_bon / 2)))
            else:
                self.add_bon(dmg_bon, "Str", str_bon)
        elif self.weap_hands(weap) == 2 and "R" not in self.weap_type(weap):
            if str_bon > 0:
                self.add_bon(dmg_bon, "Str", int((str_bon * 3 / 2)))
            else:
                self.add_bon(dmg_bon, "Str", str_bon)
        elif self.ambi and "R" in self.weap_type(weap):
            self.add_bon(dmg_bon, "Dex", dex_bon)
        elif "M" in self.weap_type(weap) or "T" in self.weap_type(weap):
            self.add_bon(dmg_bon, "Str", str_bon)

        #############################
        #
        # Class bonuses

        if self.char_class == "Fighter" and self.level >= 5:
            self.add_bon(dmg_bon, "class", self.fighter_wt_bon(self.weap_group()))

        if self.char_class == "Ranger":
            self.add_bon(dmg_bon, "class", self.ranger_fe_bon(type_mon, subtype))

        #############################
        #
        # Feat bonuses

        if not nofeat:
            self.add_bon(dmg_bon, "feat", feat.arcane_strike_bon(self))

            if "M" in self.weap_type():
                self.add_bon(dmg_bon, "feat", feat.power_attack_bon(self))
            elif "R" in self.weap_type():
                self.add_bon(dmg_bon, "feat", feat.deadly_aim_bon(self))
                if dist <= 30:
                    self.add_bon(dmg_bon, "feat", feat.pbs_bon(self))

        return sum(dmg_bon.values())

    #############################
    #
    # Defensive ability functions

    def is_weak(self, atktype):

        return atktype in self.vuln

    def res_amt(self, atktype):

        if atktype in self.res:
            return self.res[atktype]

        return 0

    def is_immune(self, atktype):

        return atktype in self.immune

    #############################
    #
    # DR functions

    def get_dr(self):

        if self.ftr_am():
            return [5, ["-"], ""]

        if self.char_class == "Barbarian" and self.level >= 7:
            return [self.barbarian_dr(), ["-"], ""]

        if self.char_class == "Monk" and self.level >= 20:
            return [10, ["chaotic"], ""]

        return []

    #############################
    #
    # HP functions

    def get_hp_bon(self):

        hp_bon = 0

        #############################
        #
        # Stat bonus

        if self.type_mon == "Undead":
            hp_stat_bon = self.stat_bonus(self.chatot()) * self.hd
        elif self.type_mon == "Construct":
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
            hp_stat_bon = self.stat_bonus(self.contot()) * self.hd

        hp_bon += hp_stat_bon

        #############################
        #
        # Feat bonus

        hp_bon += feat.toughness_bon(self)

        #############################
        #
        # FC bonus

        hp_bon += self.fc.count("h")

        return hp_bon

    def get_hp(self):
        return max(self.hp + self.get_hp_bon(), self.hd)

    def get_hp_perc(self):
        max_hp = self.get_hp()
        cur_hp = max_hp - self.damage
        return max(cur_hp / max_hp, 0)

    def get_hp_temp_perc(self):
        max_hp = self.get_hp()
        cur_hp = max_hp - self.damage - self.temp_dmg
        return max(cur_hp / max_hp, 0)

    def temp_dmg_add(self, dmg):
        self.temp_dmg += dmg

    def temp_dmg_reset(self):
        self.temp_dmg = 0

    #############################
    #
    # Initiative functions

    def get_init(self):
        init = self.stat_bonus(self.dextot())

        init += feat.improved_initiative_bon(self)

        return init

    #############################
    #
    # Language functions

    def add_lang_spec(self, lang):
        if lang not in self.lang_spec:
            self.lang_spec.append(lang)

    def del_lang_spec(self, lang):
        if lang in self.lang_spec:
            self.lang_spec.remove(lang)

    #############################
    #
    # Movement functions

    def get_move(self):

        if self.has("Prone"):
            return 5

        move = self.move

        if "fast movement" in self.sq:
            if self.char_class == "Barbarian" and self.armor_type() != "Heavy":
                move += 10
            elif self.char_class == "Monk" and self.armor_name() == "":
                move += int(self.level / 3) * 10

        if self.has("Exhausted"):
            move /= 2

        return move

    def get_move_acts(self):

        if self.damage_con == "Disabled":
            return 1

        return 2

    #############################
    #
    # Saving throw functions

    def get_fort(self):

        speed = self.fort

        if speed == "Fast":
            save = int(self.hd / 2) + 2
        else:
            save = int(self.hd / 3)

        save_bon = dict()

        self.add_bon(save_bon, "base", save)
        self.add_bon(save_bon, "stat", self.stat_bonus(self.contot()))
        self.add_bon(save_bon, "untyped", feat.great_fortitude_bon(self))

        return sum(save_bon.values())

    def get_ref(self):

        speed = self.ref

        if speed == "Fast":
            save = int(self.hd / 2) + 2
        else:
            save = int(self.hd / 3)

        save_bon = dict()

        self.add_bon(save_bon, "base", save)
        self.add_bon(save_bon, "stat", self.stat_bonus(self.dextot()))
        self.add_bon(save_bon, "untyped", feat.lightning_reflexes_bon(self))

        return sum(save_bon.values())

    def get_will(self):

        speed = self.will

        if speed == "Fast":
            save = int(self.hd / 2) + 2
        else:
            save = int(self.hd / 3)

        save_bon = dict()

        self.add_bon(save_bon, "base", save)
        self.add_bon(save_bon, "stat", self.stat_bonus(self.wistot()))
        self.add_bon(save_bon, "untyped", feat.iron_will_bon(self))
        if self.has("Raging"):
            self.add_bon(save_bon, "morale", int(self.rage_bon() / 2))

        return sum(save_bon.values())

    #############################
    #
    # Spell resistance functions

    def get_sr(self):

        sr = 0

        if self.char_class == "Monk" and self.level >= 13:
            sr = max(sr, (self.level + 10))

        return sr

    #############################
    #
    # Threat range functions

    def threat_range(self, val=None):
        if val is None:
            val = self.slots["wield"][0]
        if val is None:
            return [[5, self.reach]]

        tr = []

        if type(val) is int:
            val = [val]

        for i in val:
            tr_temp = [0, 0]

            if "M" in self.weap_type(i):
                tr_temp = [5, self.reach]
                if self.weap_reach(i):
                    tr_temp = [self.reach + 5, self.reach * 2]
            else:
                if feat.snap_shot(self):
                    tr_temp = [5, 5]
                if feat.snap_shot_imp(self):
                    tr_temp = [5, 15]
            tr.append(tr_temp[:])

        return tr

    ###################################################################
    #
    # Mechanics functions

    def check_attack(self, targ_ac, dist, full_attack, type_mon, subtype, offhand=False, fob=False):

        weap_list = self.weap_list()
        atk_bon = [[] for i in range(len(weap_list))]

        for i in range(len(atk_bon)):
            offhand = (weap_list[i][0] != self.slots["wield"][0])

            atk_bon[i] = self.get_atk_bon(dist, full_attack, type_mon, subtype, fob=fob, weap=weap_list[i][0],
                                          offhand=offhand)

        #############################
        #
        # Set up hit_miss array
        #
        # Each occupied weapon slot (by self.weap_list) assigned to tens place, ones place
        # indicating specific iterative attack bonus
        #
        # e.g., character with two weapons and 4 iterative attacks with main weapon would
        # have bonus totals in array values 00, 01, 02, 03, and 10
        #
        # If a character for some reason has >10 attacks with a single weapon, assign
        # it as two or more weapons (but why would this ever happen)

        hit_miss = [None for i in range((len(atk_bon)) * 10)]

        for i in range(len(atk_bon)):
            weapon = weap_list[i][0]

            for j in range(len(atk_bon[i])):

                hm_ix = i * 10 + j

                hit_miss[hm_ix] = 0

                #############################
                #
                # Roll attack(s)

                atk_roll = random.randint(1, 20)

                if atk_roll == 20:
                    hit_miss[hm_ix] = 1
                elif (atk_roll + atk_bon[i][j]) >= targ_ac:
                    hit_miss[hm_ix] = 1

                #############################
                #
                # Check for critical

                crit_rng = self.weap_crit_range(weapon)

                if atk_roll >= crit_rng and hit_miss[hm_ix] == 1:
                    conf_roll = random.randint(1, 20)

                    conf_bon = atk_bon[i][j]

                    conf_bon = conf_bon + feat.critical_focus_bon(self)

                    if conf_roll == 20 or (conf_roll + conf_bon) >= targ_ac or self.ftr_wm():
                        hit_miss[hm_ix] = 2

        return hit_miss

    def check_cmb(self, targ_cmd, dist=5, type_mon=None, subtype=None, man=""):

        cmb = self.cmb(dist=dist, type_mon=type_mon, subtype=subtype, man=man)

        cmb_roll = random.randint(1, 20)

        result = (cmb_roll + cmb) - targ_cmd

        if cmb_roll == 20:
            return [True, result]
        elif cmb_roll == 1:
            return [False, result]
        else:
            return [result >= 0, result]

    def check_save(self, stype, dc):

        if self.damage_con not in ["Normal", "Disabled"]:
            return [False, "No save"]

        save_bon = 0

        if stype == "F":
            save_bon = self.get_fort()
        elif stype == "R":
            save_bon = self.get_ref()
        elif stype == "W":
            save_bon = self.get_will()

        save_roll = random.randint(1, 20) + save_bon

        save_pass = (save_roll >= dc)  # done this way rather than direct return to better support later expansion

        return [save_pass, save_roll]

    def check_conc(self, dc):

        conc_roll = random.randint(1, 20) + self.concentration()

        conc_pass = (conc_roll >= dc)

        return [conc_pass, conc_roll]

    def roll_dmg(self, dist, crit=False, type_mon=None, subtype=None, weap=None):

        if weap is None:
            weap = self.curr_weap()

        offhand = (weap != self.slots["wield"][0])

        #############################
        #
        # Crit multiplier

        if crit:
            roll_mult = self.weap_crit_mult(weap)
        else:
            roll_mult = 1

        dmg_bon = self.get_base_dmg_bon(dist, type_mon, subtype, weap=weap, offhand=offhand)

        #############################
        #
        # Damage roll

        dmg = 0
        for j in range(roll_mult):
            for i in range(self.weap_dmg(weap)[0]):
                dmg = dmg + random.randint(1, self.weap_dmg(weap)[1])
            dmg = dmg + dmg_bon

        if dmg < 0:
            dmg = 0

        return dmg

    def roll_hp_tot(self):
        hp = 0

        hit_roll = self.hd

        if self.level > 0:
            hit_roll -= 1
            hp = self.hit_die

        for i in range(hit_roll):
            hp = hp + random.randint(1, self.hit_die)

        self.hp = hp

    def weap_swap(self):
        if feat.quick_draw(self):
            return "free"
        else:
            return "move"

    def attack(self, targ_ac, dist=5, full_attack=True, type_mon=None, subtype=None, fob=False):

        dmg = 0
        hit_miss = self.check_attack(targ_ac, dist, full_attack, type_mon, subtype, fob=fob)
        dmg_vals = [0 for i in hit_miss]
        dmg_list_out = [None for i in hit_miss]

        weap_list = self.weap_list()
        for atk_count, atk_result in enumerate(hit_miss):
            if atk_result is None:
                continue
            weap = weap_list[atk_count // 10][0]
            if atk_result == 0:
                dmg_vals[atk_count] = 0
                dmg_list_out[atk_count] = "miss"
            elif atk_result == 1:
                dmg_vals[atk_count] = self.roll_dmg(dist, type_mon=type_mon, subtype=subtype)

                if feat.manyshot(self) and "R" in self.weap_type(weap) and atk_count == 0:
                    dmg_vals[atk_count] += self.roll_dmg(dist, type_mon=type_mon, subtype=subtype, weap=weap)
                dmg_list_out[atk_count] = str(dmg_vals[atk_count])
            elif atk_result == 2:
                dmg_vals[atk_count] = self.roll_dmg(dist, crit=True, type_mon=type_mon, subtype=subtype)

                if feat.manyshot(self) and "R" in self.weap_type(weap) and atk_count == 0:
                    dmg_vals[atk_count] += self.roll_dmg(dist, type_mon=type_mon, subtype=subtype, weap=weap)

                dmg_list_out[atk_count] = "*" + str(dmg_vals[atk_count])
        return sum(dmg_vals), dmg_list_out

    ###################################################################
    #
    # Output functions

    # ordinal: outputs the ordinal version of an integer input

    @staticmethod
    def ordinal(num):
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = suffixes.get(num % 10, 'th')

        return str(num) + suffix

    # base_presented_stats: the statistics visible to an outside party; used for AI mental models
    # (self, name, side, armor_class, move, loc, hp, tilesize, str, dex, con, int, wis, cha, feat_list, type, subtype, size, reach, fort, ref, will, hands, legs)

    def base_presented_stats(self, side):

        kwargstats = dict()

        kwargstats["name"] = "{} ({})".format(self.race, self.name)
        kwargstats["orig"] = self
        kwargstats["id"] = self.id

        kwargstats["type_mon"] = self.type_mon
        kwargstats["race"] = self.race
        kwargstats["size"] = self.size
        kwargstats["reach"] = self.reach
        kwargstats["hands"] = self.hands
        kwargstats["legs"] = self.legs

        kwargstats["stg"] = self.strtot()
        kwargstats["dex"] = self.dextot()
        kwargstats["con"] = self.contot()

        kwargstats["loc"] = self.loc
        kwargstats["tilesize"] = self.tilesize
        kwargstats["side"] = self.side

        return kwargstats

    # print_dmg: prints weapon damage for given weapon in standard format, with all current feats and buffs
    #            pass nofeat=True to not include feat bonuses

    def print_dmg(self, dist, type_mon, subtype, weap=None, nofeat=False):

        if weap is None:
            weap = self.slots["wield"][0]

        out = "{}d{}".format(self.weap_dmg(weap)[0], self.weap_dmg(weap)[1])

        dmg_bon = self.get_base_dmg_bon(dist, type_mon, subtype, weap, nofeat)

        if dmg_bon != 0:
            out += "{:+d}".format(dmg_bon)

        return out

    # print_ac_bons: prints all current armor_class bonuses in alphabetical order

    def print_ac_bons(self, type_mon=None, subtype=None):

        ac_bons = self.get_ac_bons(type_mon, subtype)

        ac_keys = sorted(ac_bons.keys(), key=lambda x: x.lower())

        ac_out = ""

        for AC_type in ac_keys:
            if ac_bons[AC_type] != 0:
                ac_out += "{:+d} {}, ".format(ac_bons[AC_type], AC_type)

        return ac_out[:-2]

    # print_ac_line: prints armor_class line in standard format, including base, touch, ff, and all current bonuses

    def print_ac_line(self, type_mon=None, subtype=None):

        return "armor_class {}, touch {}, flat-footed {} ({})".format(self.get_ac(), self.get_ac(touch=True),
                                                                      self.get_ac(ff=True), self.print_ac_bons())

    # print_all_atks: prints atk line for all current weapons

    def print_all_atks(self, dist=0, full_attack=True, type_mon=None, subtype=None, nofeat=False):
        weap_list = self.weap_list()
        output = ["" for i in range(len(weap_list))]

        for i, weap in enumerate(weap_list):
            output[i] = self.print_atk_line(dist, full_attack, type_mon, subtype, weap[0], nofeat)

        return '; '.join(output)

    # print_atk_dmg: takes damage array as returned in 1 index of attack, formats into human-readable format

    def print_atk_dmg(self, dmg):
        weap_list = self.weap_list()
        output = ["" for i in range(len(weap_list))]

        for i, weap in enumerate(weap_list):
            if dmg[i * 10] is None:
                continue
            output[i] += self.weap_name(weap[0]) + ": "
            output[i] += dmg[i * 10]

            j = 1
            while dmg[i * 10 + j] is not None and j < 10:
                output[i] += ", " + dmg[i * 10 + j]
                j += 1

        while output.count("") > 0:
            output.remove("")

        return '; '.join(output)

    # print_atk_line: prints attack line for a given weapon in standard format, with all current feats and buffs
    #                 pass nofeat=True to not include feat bonuses

    def print_atk_line(self, dist=0, full_attack=True, type_mon=None, subtype=None, weap=None, nofeat=False, fob=False):

        if weap is None:
            weap = self.slots["wield"][0]

        atk_out = "{} ".format(self.weap_name(weap))

        if fob:
            atk_out += "flurry of blows "

        atk_bon = self.get_atk_bon(dist, full_attack, type_mon, subtype, weap, nofeat, fob=fob)

        if len(atk_bon) == 1:
            temp = "{:+d}".format(atk_bon[0])
        else:
            temp = "/".join(map(lambda x: "{:+d}".format(x), atk_bon))

        atk_out += temp + " (" + self.print_dmg(dist, type_mon, subtype, weap, nofeat)

        crit_rng = self.weap_crit_range(weap)

        if crit_rng != 20 or self.weap_crit_mult(weap) != 2:
            atk_out += "/"
            if crit_rng == 20:
                temp = "20"
            else:
                temp = "{}-20".format(crit_rng)

            atk_out += temp

            if self.weap_crit_mult(weap) != 2:
                atk_out += "/x" + str(self.weap_crit_mult(weap))

        atk_out += ")"

        return atk_out

    # print_fob: prints flurry atk line for current weapon

    def print_fob(self, dist=0, type_mon=None, subtype=None, nofeat=False):
        weap_list = self.weap_list()
        output = ["" for i in range(len(weap_list))]

        for i, weap in enumerate(weap_list):
            output[i] = self.print_atk_line(dist, True, type_mon, subtype, weap[0], nofeat, fob=True)

        return '; '.join(output)

    # print_hd: prints hit dice of character in standard format

    def print_hd(self):
        out = "{}d{}".format(self.hd, self.hit_die)

        hp_bon = self.get_hp_bon()

        if hp_bon != 0:
            out += "{:+d}".format(hp_bon)

        return out

    # print_hp: prints (cur)/(max) hp

    def print_hp(self):
        return "{}/{}".format(self.get_hp() - self.damage, self.get_hp())

    # print_save_line: prints current saving throw bonuses

    def print_save_line(self):
        return "Fort {:+d}, Ref {:+d}, Will {:+d}".format(self.get_fort(), self.get_ref(), self.get_will())

    def print_spell_line(self):

        spell_line = [[] for i in range(0, self.max_spell_lvl + 1)]

        for i in range(self.max_spell_lvl, -1, -1):
            if i != 0:
                spell_line[i] = self.ordinal(i) + " - "
            else:
                spell_line[i] = "0 - "

            spell_text = []

            for spell_name in self.spell_list_mem[i].keys():
                spell = self.spell_list_mem[i][spell_name][0]
                spell_count = self.spell_list_mem[i][spell_name][1]

                spell_desc = spell_name

                if spell_count > 1:
                    spell_desc += " x{}".format(spell_count)

                if spell.has_save():
                    spell_desc += " (dc {})".format(10 + i + self.stat_bonus(self.casttot()))

                spell_text.append(spell_desc)

            spell_line[i] += ", ".join(sorted(spell_text))

        return spell_line


###################################################################

class Character(Foundation):
    """NPC stats and data"""

    def __init__(self, name=None, side=1, armor_class=10, move=None, loc=None, tilesize=None, level=1,
                 char_class="Fighter", hp=1, stg=10, dex=10, con=10, inl=10, wis=10, cha=10,
                 feat_list=None, ambi=False, type_mon="Humanoid",
                 subtype=None, size="Medium", reach=5, fort=None, ref=None, will=None, race="Human", hands=2, legs=2,
                 fc=None):
        if loc is None:
            loc = [0, 0]
        if tilesize is None:
            tilesize = [1, 1]
        if feat_list is None:
            feat_list = []
        if subtype is None:
            subtype = ["human"]
        if fc is None:
            fc = ["s" for i in range(level)]

        if move is None:
            move = 30

        save_array = [fort, ref, will]
        save_array = self.set_saves(save_array, char_class)

        Foundation.__init__(self, name, side, armor_class, move, loc, hp, tilesize, stg, dex, con, inl, wis, cha,
                            feat_list, type_mon, subtype, size, reach, save_array[0], save_array[1], save_array[2], hands,
                            legs)

        self.race = race
        self.hd = level
        self.fc = fc
        self.ambi = ambi

        self.char_class = char_class
        self.level = level

        self.set_bab()
        self.set_spellcast_stats()
        self.set_hit_die()

        self.start_equip_list = []
        self.start_melee_weaps = []
        self.start_ranged_weaps = []
        self.start_slots = []
        self.start_spell_list_mem = []
        self.start_conditions = []

        if hp == 0:
            self.roll_hp_tot()

        self.equip_unarmed()

        self.set_class_abilities()
        self.set_feat_abilities()

        self.model = False

    def set_bab(self):

        if self.char_class in ["Barbarian", "Fighter", "Paladin", "Ranger"]:
            self.bab = range(self.level, 0, -5)
        elif self.char_class in ["Bard", "Cleric", "Druid", "Monk", "Rogue"]:
            self.bab = range(int(self.level * 3 / 4), 0, -5)
            if not self.bab:
                self.bab = [int(self.level * 3 / 4)]
        else:
            self.bab = range(int(self.level / 2), 0, -5)
            if not self.bab:
                self.bab = [int(self.level / 2)]

    def set_spellcast_stats(self):

        if self.char_class in ["Bard", "Sorcerer"]:
            self.arcane = True
            self.cast_stat = "h"

        if self.char_class in ["Wizard"]:
            self.arcane = True
            self.cast_stat = "i"

        if self.char_class in ["Cleric", "Druid"]:
            self.divine = True
            self.cast_stat = "w"

        if self.char_class in ["Paladin"] and self.level >= 4:
            self.divine = True
            self.cast_stat = "h"

        if self.char_class in ["Ranger"] and self.level >= 4:
            self.divine = True
            self.cast_stat = "w"

    def set_hit_die(self):

        if self.char_class in ["Barbarian"]:
            self.hit_die = 12
        elif self.char_class in ["Fighter", "Paladin", "Ranger"]:
            self.hit_die = 10
        elif self.char_class in ["Bard", "Cleric", "Druid", "Monk", "Rogue"]:
            self.hit_die = 8
        else:
            self.hit_die = 6

    def set_saves(self, save_array, char_class=None):
        if char_class is None:
            char_class = self.char_class
        fort, ref, will = save_array

        if not fort:
            if char_class in ["Barbarian", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger"]:
                fort = "Fast"
            else:
                fort = "Slow"

        if not ref:
            if char_class in ["Bard", "Monk", "Ranger", "Rogue"]:
                ref = "Fast"
            else:
                ref = "Slow"

        if not will:
            if char_class in ["Bard", "Cleric", "Druid", "Monk", "Paladin", "Sorcerer", "Wizard"]:
                will = "Fast"
            else:
                will = "Slow"

        return [fort, ref, will]

    def set_class_abilities(self):
        if self.char_class == "Barbarian":
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

        elif self.char_class == "Fighter":
            if self.level >= 2:
                self.add_da("bravery {:+d}".format(self.fighter_bravery()))
            if self.level >= 3:
                self.add_sq("armor training {}".format(self.fighter_armor_training()))
            if self.level >= 19:
                self.add_sq("armor mastery")

        elif self.char_class == "Monk":
            if "Improved Unarmed Strike" not in self.feat_list:
                self.feat_list.append("Improved Unarmed Strike")
            if "Stunning Fist" not in self.feat_list:
                self.feat_list.append("Stunning Fist")
            self.add_sa("flurry of blows")
            if self.level >= 2:
                if "evasion" in self.da:
                    self.del_da("evasion")
                    self.add_da("improved evasion")
                else:
                    self.add_da("evasion")
            if self.level >= 3:
                self.add_sq("fast movement")
            if self.level >= 4:
                self.add_sq("maneuver training")
                self.monk_ki_tot()
                self.ki_types.append("magic")
            if self.level >= 5:
                self.add_sq("high jump")
                self.add_sq("purity of body")
                self.add_imm("disease")
            if self.level >= 7:
                self.ki_types.append("cold iron")
                self.ki_types.append("silver")
                self.add_sq("wholeness of body")
            if self.level >= 9:
                self.del_da("evasion")
                self.add_da("improved evasion")
            if self.level >= 10:
                self.ki_types.append("lawful")
            if self.level >= 11:
                self.add_sq("diamond body")
                self.add_imm("poison")
            if self.level >= 12:
                self.add_sq("abundant step")
            if self.level >= 13:
                self.add_sq("diamond soul")
            if self.level >= 15:
                self.add_sa(
                    "quivering palm (1/day, dc {})".format(10 + int(self.level / 2) + self.stat_bonus(self.wistot())))
            if self.level >= 16:
                self.ki_types.append("adamantine")
            if self.level >= 17:
                self.add_sq("timeless body")
                self.add_lang_spec("tongue of the sun and moon")
            if self.level >= 19:
                self.add_sq("empty body")
            if self.level >= 20:
                self.add_sq("perfect self")
                self.type_mon = "Outsider"

        elif self.char_class == "Wizard":
            if "Scribe Scroll" not in self.feat_list:
                self.feat_list.append("Scribe Scroll")

            if self.level == 1:
                self.spell_mem_max[0] = 3
            else:
                self.spell_mem_max[0] = 4

            cast_bon = self.stat_bonus(self.casttot())

            for i in range(1, 10):
                start_level = (2 * i) - 1
                if self.level < start_level:
                    continue
                elif self.level == start_level:
                    self.spell_mem_max[i] = 1
                elif self.level <= start_level + 2:
                    self.spell_mem_max[i] = 2
                elif self.level <= start_level + 5:
                    self.spell_mem_max[i] = 3
                else:
                    self.spell_mem_max[i] = 4

                if cast_bon < i:
                    pass
                else:
                    self.spell_mem_max[i] += ((cast_bon - i) // 4 + 1)

                self.max_spell_lvl = i

    def set_feat_abilities(self):
        if feat.stunning_fist(self):
            self.add_sa(
                "stunning fist ({}/day, dc {})".format(self.level if self.char_class == "Monk" else int(self.level / 4),
                                                       10 + int(self.level / 2) + self.stat_bonus(self.wistot())))
            stun_fist = satk.stunning_fist.copy()
            if self.char_class == "Monk":
                uses_day = self.level
            else:
                uses_day = self.level // 4
            stun_fist.set_uses(uses_day, "day")
            self.sa_list.append(stun_fist)

    def update(self):

        self.set_bab()
        self.set_spellcast_stats()
        if self.char_class == "Monk":
            self.monk_ki_tot()
            # self.monk_ki_check()

    def save_state(self):

        self.freeze_equip()
        self.freeze_spells()
        self.freeze_conditions()

    def freeze_equip(self):
        self.start_equip_list = copy.deepcopy(self.equip_list)
        self.start_melee_weaps = copy.deepcopy(self.melee_weaps)
        self.start_ranged_weaps = copy.deepcopy(self.ranged_weaps)
        self.start_slots = copy.deepcopy(self.slots)

    def freeze_spells(self):

        self.start_spell_list_mem = copy.deepcopy(self.spell_list_mem)

    def freeze_conditions(self):

        self.start_conditions = copy.deepcopy(self.conditions)

    def reset(self):

        self.damage = 0
        self.damage_con = "Normal"
        del self.conditions
        self.conditions = copy.deepcopy(self.start_conditions)
        self.loc = self.startloc

        self.rage_dur = 0
        self.ki_spent = 0

        del self.equip_list
        self.equip_list = copy.deepcopy(self.start_equip_list)
        del self.melee_weaps
        self.melee_weaps = copy.deepcopy(self.start_melee_weaps)
        del self.ranged_weaps
        self.ranged_weaps = copy.deepcopy(self.start_ranged_weaps)
        del self.slots
        self.slots = copy.deepcopy(self.start_slots)

        del self.spell_list_mem
        self.spell_list_mem = copy.deepcopy(self.start_spell_list_mem)

    ############################################

    def print_stat_block(self, textwidth=60):

        stats = [self.strtot(), self.dextot(), self.contot(), self.inttot(), self.wistot(), self.chatot()]

        stats = map(lambda x: x if x > 0 else "-", stats)

        da_line = ""
        if self.da:
            da_line += "Defensive Abilities {}".format(", ".join(sorted(self.da)))
        dr = self.get_dr()
        if dr:
            if da_line != "":
                da_line += "; "
            da_line += "DR {}/{}".format(dr[0], dr[2].join(sorted(dr[1])))
        if self.immune:
            if da_line != "":
                da_line += "; "
            da_line += "Immune {}".format(", ".join(sorted(self.immune)))
        sr = self.get_sr()
        if sr > 0:
            if da_line != "":
                da_line += "; "
            da_line += "SR {}".format(sr)

        melee_set = []
        fob_set = []
        if "M" in self.weap_type():
            base_atk_line = self.print_atk_line(nofeat=True)
            if self.has_offhand():
                # noinspection PyTypeChecker
                base_atk_line += ", " + self.print_atk_line(nofeat=True, weap=self.slots["wield"][1])
            melee_set.append(base_atk_line)
            if "Monk" in self.weap_group() and self.char_class == "Monk":
                fob_set.append(self.print_atk_line(nofeat=True, fob=True))
        for weapon in self.melee_weaps:
            # noinspection PyTypeChecker,PyTypeChecker
            if weapon == self.slots["wield"][0] or weapon == self.slots["wield"][1]:
                continue
            if weapon == 0:
                if len(self.melee_weaps) > 1 and self.char_class != "Monk":
                    continue
            melee_set.append(self.print_atk_line(weap=weapon, nofeat=True))
            if "Monk" in self.weap_group(weapon) and self.char_class == "Monk":
                fob_set.append(self.print_atk_line(weap=weapon, nofeat=True, fob=True))
        melee_set += fob_set
        for i in range(len(melee_set[0:-1])):
            melee_set[i] += " or"

        ranged_set = []
        fob_set = []
        if "R" in self.weap_type():
            base_atk_line = self.print_atk_line(nofeat=True)
            ranged_set.append(base_atk_line)
            if "Monk" in self.weap_group() and self.char_class == "Monk":
                fob_set.append(self.print_atk_line(nofeat=True, fob=True))
        for weapon in self.ranged_weaps:
            # noinspection PyTypeChecker
            if weapon == self.slots["wield"][0]:
                continue
            ranged_set.append(self.print_atk_line(weap=weapon, nofeat=True))
            if "Monk" in self.weap_group(weapon) and self.char_class == "Monk":
                fob_set.append(self.print_atk_line(weap=weapon, nofeat=True, fob=True))
        ranged_set += fob_set
        for i in range(len(ranged_set[0:-1])):
            ranged_set[i] += " or"
        ranged_line = "Ranged {}".format(" or ".join(ranged_set))

        spell_type = ""
        if self.cl() > 0:
            if self.char_class in ["Cleric", "Wizard", "Paladin", "Ranger"]:
                spell_type = "Prepared"
            elif self.char_class in ["Bard", "Sorcerer"]:
                spell_type = "Known"

        spell_line = self.print_spell_line()

        wordwrap = textwrap.TextWrapper(subsequent_indent="  ", width=textwidth)
        wordwrap_indent = textwrap.TextWrapper(initial_indent="  ", subsequent_indent="    ", width=textwidth)
        separator = "=" * textwidth

        out = []

        out.append(separator)
        out.append(wordwrap.fill("{}".format(self.name)))
        out.append(wordwrap.fill("{} {} {}".format(self.race, self.char_class, self.level)))
        out.append(wordwrap.fill("{} {} ({})".format(self.size, self.type_mon.lower(), ', '.join(self.subtype))))
        out.append("")
        out.append(wordwrap.fill("Init {:+d}".format(self.get_init())))
        out.append(separator)
        out.append(wordwrap.fill("DEFENSE"))
        out.append(separator)
        out.append(wordwrap.fill(self.print_ac_line()))
        out.append(wordwrap.fill("hp {} ({})".format(self.get_hp(), self.print_hd())))
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
        if self.cl() > 0:
            out.append(wordwrap.fill(
                "{} Spells {} (cl {}; concentration {:+d})".format(self.char_class, spell_type, self.ordinal(self.cl()),
                                                                   self.concentration())))
            for i in range(self.max_spell_lvl, -1, -1):
                out.append(wordwrap_indent.fill(spell_line[i]))
        out.append(separator)
        out.append(wordwrap.fill("STATISTICS"))
        out.append(separator)
        out.append(wordwrap.fill("Str {}, Dex {}, Con {}, Int {}, Wis {}, Cha {}".format(*stats)))
        out.append(wordwrap.fill("Base Atk {:+d}; cmb {:+d}; cmd {}".format(self.bab[0], self.cmb(), self.cmd())))
        out.append(wordwrap.fill("Feats {}".format(', '.join(sorted(self.feat_list)))))
        lang_list = ", ".join(sorted(self.lang))
        if lang_list:
            lang_list += "; "
        lang_list += ", ".join(sorted(self.lang_spec))
        if lang_list:
            out.append(wordwrap.fill("Languages {}".format(lang_list)))
        if self.sq:
            out.append(wordwrap.fill("SQ {}".format(", ".join(sorted(self.sq)))))
        out.append(separator)

        return '\n'.join(out)


###################################################################

class Monster(Foundation):
    """Monster stats and data"""

    def __init__(self, name=None, side=1, armor_class=10, move=30, loc=None, tilesize=None, hd=1, type_mon="Humanoid",
                 subtype=None, size="Medium", hp=1, stg=10, dex=10, con=10, inl=10, wis=10, cha=10,
                 feat_list=None, arcane=False, divine=False, cl=0, reach=5, fort=None, ref=None, will=None, hands=2,
                 legs=2):

        if loc is None:
            loc = [0, 0]
        if tilesize is None:
            tilesize = [1, 1]
        if subtype is None:
            subtype = []
        if feat_list is None:
            feat_list = []

        Foundation.__init__(self, name, side, armor_class, move, loc, hp, tilesize, stg, dex, con, inl, wis, cha,
                            feat_list, type_mon, subtype, size, reach, fort, ref, will, hands, legs)

        self.level = 0
        self.char_class = None
        self.hd = hd
        self.arcane = arcane
        self.divine = divine
        self.cl = cl
        self.weap_bon = 0
        self.fc = []

        self.set_bab()
        self.set_hit_die()

        self.model = False

        if hp == 0:
            self.roll_hp_tot()

    def set_bab(self):

        if self.type_mon in ["Construct", "Dragon", "Magical Beast", "Monstrous Humanoid", "Outsider"]:
            self.bab = range(self.hd, 0, -5)
        elif self.type_mon in ["Aberration", "Animal", "Humanoid", "Ooze", "Plant", "Undead", "Vermin"]:
            self.bab = range(int(self.hd * 3 / 4), 0, -5)
            if not self.bab:
                self.bab = [int(self.hd * 3 / 4)]
        else:
            self.bab = range(int(self.hd / 2), 0, -5)
            if not self.bab:
                self.bab = [int(self.hd / 2)]

    def set_hit_die(self):

        if self.type_mon in ["Dragon"]:
            self.hit_die = 12
        elif self.type_mon in ["Construct", "Magical Beast", "Monstrous Humanoid", "Outsider"]:
            self.hit_die = 10
        elif self.type_mon in ["Aberration", "Animal", "Humanoid", "Ooze", "Plant", "Undead", "Vermin"]:
            self.hit_die = 8
        else:
            self.hit_die = 6

    def reset(self):

        self.damage = 0
        self.damage_con = "Normal"


###################################################################

class Charmodel(Foundation):
    """Mental model char framework"""

    def __init__(self, name=None, side=1, armor_class=10, bab=0, move=30, loc=None, tilesize=None, hd=1,
                 type_mon="Humanoid",
                 subtype=None, size="Medium", hp=1, stg=10, dex=10, con=10, inl=10, wis=10, cha=10,
                 feat_list=None, arcane=False, divine=False, cl=0, reach=5, fort=None, ref=None, will=None, hands=2,
                 legs=2, init=0, race=None, char_class=None, level=1,
                 fc=None, id=None, orig=None):

        if loc is None:
            loc = [0, 0]
        if tilesize is None:
            tilesize = [1, 1]
        if subtype is None:
            subtype = []
        if feat_list is None:
            feat_list = []
        if fc is None:
            fc = []

        Foundation.__init__(self, name, side, armor_class, move, loc, hp, tilesize, stg, dex, con, inl, wis, cha,
                            feat_list, type_mon, subtype, size, reach, fort, ref, will, hands, legs)
        self.model = True
        self.id = id
        self.orig = orig

        self.init = init

        if race:
            self.race = race
        else:
            self.race = "Unknown"

        if char_class is not None:
            self.char_class = char_class
        else:
            self.char_class = "Unknown"

        self.level = level

        self.hd = hd

        self.fc = fc

    def is_active(self):
        return self.orig.is_active()
