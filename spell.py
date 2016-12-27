import copy
import re
import random


class Spell:
    """Spell data structure"""

    def __init__(self, name="", level=None, school=None, subschool=None, desc=None, cast_time="std", comp="V",
                 spl_range="0", aim=None, dur=0, sr=True, effect=None):
        if subschool is None:
            subschool = []
        if desc is None:
            desc = []
        if level is None:
            level = "s1w1"
        if school is None:
            school = "di"
        if aim is None:
            aim = ["t", 0]

        self.name = name
        self.level = level
        self.school = school
        self.subschool = subschool
        self.cast_time = cast_time
        self.comp = comp
        self.spl_range = spl_range
        self.aim = aim
        self.dur = dur
        self.sr = sr

        self.targ_num = 0

        self.buff = []
        self.debuff = []
        self.dmg = []

        self.save = False

        self.class_parse = {"b": "Bard", "c": "Cleric", "d": "Druid", "i": "Inquisitor", "m": "Magus", "o": "Oracle",
                            "p": "Paladin", "r": "Ranger", "s": "Sorcerer", "u": "Summoner", "w": "Wizard"}
        self.type_parse = {"f": "Fire", "o": "Force"}
        self.save_parse = {"F": "Fortitude", "R": "Reflex", "W": "Will"}

        self.effect_parse(effect)

    #############################
    #
    # Parsing functions

    def lvl_parse(self, level=None):

        if level is None:
            level = self.level

        lvl_int = {}
        temp_class = ""
        for c in level:
            if c.isalpha():
                temp_class = self.class_parse[c]
                continue
            lvl_int[temp_class] = int(c)

        return lvl_int

    def targ_parse(self, caster, targ_val=None):
        if self.aim[0] != "t":
            return 0

        if targ_val is None:
            targ_val = self.aim[1]

        cl = caster.cl()

        if targ_val.isdigit():
            return int(targ_val)

        if targ_val[0] == "L":
            return cl

        if targ_val[0] == "R":
            targ_calc = targ_val[1:].split(',')
            for i, val in enumerate(targ_calc):
                targ_calc[i] = int(val)
            min_l, max_l, skip_l = targ_calc
            targ_count = 0

            if cl > max_l:
                cl = max_l
            if cl < min_l:
                cl = min_l

            while True:
                cl -= skip_l
                targ_count += 1
                if cl < min_l:
                    break

            return targ_count

    def effect_parse(self, effect):
        effect_list = effect.split(";")

        for eff in effect_list:
            eff_type = eff.split(" ")
            if eff_type[0] == "damage":
                damage = eff_type[1].split(",")

                dice = re.split('[d+]', damage[0])
                for c in enumerate(dice):
                    if c[1].isdigit() or c[1][0] == "-":
                        dice[c[0]] = int(c[1])
                    else:
                        dice[c[0]] = c[1]

                if len(dice) == 2:
                    # noinspection PyTypeChecker
                    dice.append(0)

                damage[0] = dice
                if damage[1] == "":
                    damage[1] = 0
                else:
                    damage[1] = int(damage[1])

                self.dmg.append(
                    damage)  # damage dice in index 0 (L=level variable), max dice in index 1, save in index 2, damage type in index 3

                save_data = damage[2]

                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True

            if eff_type[0] == "buff":
                buff = eff_type[1].split(",")

                self.buff.append(buff)

                save_data = buff[3]

                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True

            if eff_type[0] == "debuff":
                debuff = eff_type[1].split(",")

                save_data = debuff[3]

                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True

    #############################
    #
    # Spell data

    def is_single(self):
        if self.aim[0] == "t" and self.aim[1] == 1:
            return True
        else:
            return False

    def is_multi(self):
        return not self.is_single()

    def has_save(self):

        return self.save

    def is_valid_target(self, target):
        if self.aim[0] != "t":
            return True

        valid = False

        # Targeting restrictions

        # Effect-based restrictions

        if self.dmg:
            valid = True

        if self.debuff:
            for debuff in self.debuff:
                if debuff[1] == "cond":
                    if debuff[3] == "end" and target.has(debuff[2]):
                        valid = True
                    if debuff[3] != "end" and not target.has(debuff[2]):
                        valid = True

        return valid

    def get_dc(self, caster):
        level_list = self.lvl_parse()
        sl = level_list[caster.char_class]
        cast_bon = caster.stat_bonus(caster.casttot())

        return 10 + sl + cast_bon

    def get_range(self, caster):
        cl = caster.cl()

        spl_range = 0

        if self.spl_range == "close":
            spl_range = 25 + 5 * (cl // 2)
        elif self.spl_range == "medium":
            spl_range = 100 + 10 * cl
        elif self.spl_range == "long":
            spl_range = 400 + 40 * cl
        elif self.spl_range == "unlimited":
            spl_range = 9999
        elif self.spl_range.isdigit():
            spl_range = int(self.spl_range)

        return spl_range

    def get_area(self, caster):
        area_set = []

        spell_rng = self.get_range(caster)

        if self.aim[1] == "L":
            area_set = self.get_line_area(spell_rng)
        elif self.aim[1][0] == "C":
            area_set = self.get_cone_area(spell_rng)

        return area_set

    @staticmethod
    def get_quarter_circle_sweep(spell_rng, filled=False):

        outer_point_set = []

        square_count = spell_rng // 5

        for y_mod in range(1, square_count + 1):
            y = square_count - y_mod
            diag = int((y_mod - 1) * 2 / 3)
            point = [diag, y + diag]
            outer_point_set.append(point)

        for x in range(1, square_count):
            x_diag = square_count - x
            diag = int((x_diag - 1) * 2 / 3)
            point = [x + diag, diag]
            outer_point_set.append(point)

        if filled:
            for x1, y1 in outer_point_set:
                for y in range(0, y1):
                    if [x1, y] not in outer_point_set:
                        outer_point_set.append([x1, y])

        outer_point_set.sort(key=lambda i: i[0])
        outer_point_set.sort(key=lambda i: i[1], reverse=True)

        return outer_point_set

    @staticmethod
    def get_quarter_circle_sweep_tilted(spell_rng, filled=False):

        outer_point_set = []
        outer_point_set_2 = []

        square_count = spell_rng // 5

        for y_mod in range(1, square_count + 1):
            y = square_count - y_mod
            diag = int((y_mod - 1) * 2 / 3)
            point = [diag, y + diag]
            outer_point_set.append(point)

        for x1, y1 in outer_point_set:
            outer_point_set_2.append([-x1 - 1, y1])

        if filled:
            for x1, y1 in outer_point_set:
                for y in range(x1, y1):
                    if [x1, y] not in outer_point_set:
                        outer_point_set.append([x1, y])

            for x1, y1 in outer_point_set_2:
                for y in range(-(x1 + 1), y1):
                    if [x1, y] not in outer_point_set_2:
                        outer_point_set_2.append([x1, y])

        outer_point_set += outer_point_set_2

        outer_point_set.sort(key=lambda i: i[0])
        outer_point_set.sort(key=lambda i: i[1], reverse=True)

        return outer_point_set

    def get_cone_area(self, spell_rng):
        area_set = []

        # Diagonal cones

        base_area = self.get_quarter_circle_sweep(spell_rng, True)

        area_set.append(base_area[:])  # NE cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([x1, -y1 - 1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # SE cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([-x1 - 1, y1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # NW cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([-x1 - 1, -y1 - 1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # SW cone

        # Straight cones

        base_area = self.get_quarter_circle_sweep_tilted(spell_rng, True)

        area_set.append(base_area[:])  # N cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([x1, -y1 - 1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # S cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([y1, x1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # E Cone

        temp_area = []
        for x1, y1 in base_area:
            temp_area.append([-y1 - 1, x1])

        temp_area.sort(key=lambda i: i[0])
        temp_area.sort(key=lambda i: i[1], reverse=True)

        area_set.append(temp_area[:])  # W Cone

        area_set_2 = [area_set, ["NE", "SE", "NW", "SW", "N", "S", "E", "W"]]

        return area_set_2

    @staticmethod
    def get_line_area(spell_rng):
        area_set = []

        # Calculate outer point

        outer_point_set = []

        return area_set

    def avg_damage(self, caster, target):
        if not self.dmg:
            return 0

        cl = caster.cl()

        avg_dmg_tot = 0

        for damage in self.dmg:
            [dice, lvlmax, save, types] = damage

            if dice[0] == "L":
                if lvlmax == 0:
                    dice[0] = cl
                else:
                    dice[0] = min(cl, lvlmax)

            avg_dmg = (dice[0] + (dice[0] * dice[1])) / 2 + dice[2]

            for l in types:
                dmgtype = self.type_parse[l]

                if target.is_weak(dmgtype):
                    avg_dmg *= 1.5
                    # print("Weak to {}".format(dmgtype))
                elif target.res_amt(dmgtype) > 0:
                    avg_dmg -= target.res_amt(dmgtype)
                    if avg_dmg < 0:
                        avg_dmg = 0
                        # print("Resistance {} against {}".format(target.res_amt(dmgtype),dmgtype))
                elif target.is_immune(dmgtype):
                    avg_dmg = 0
                    # print("Immune to {}".format(dmgtype))

            if self.sr:
                sr_goal_score = target.get_sr() - cl

                chance_sr = max(min((20 - sr_goal_score + 1) / 20, 1), 0)

                avg_dmg *= chance_sr

            if save != "N" and avg_dmg != 0:
                avg_dmg_fail = avg_dmg
                avg_dmg_pass = avg_dmg

                if save[0] == "R" and "improved evasion" in target.da:
                    avg_dmg_fail = avg_dmg / 2
                else:
                    avg_dmg_fail = avg_dmg

                if len(save) > 1:
                    if save[1] == "2":
                        if save[0] == "R" and "evasion" in target.da:
                            avg_dmg_pass = 0
                        else:
                            avg_dmg_pass = avg_dmg / 2
                    if save[1] == "0":
                        avg_dmg_pass = 0

                save_bon = 0

                if save != "N" and (len(save) == 2 or save[2] != "h"):
                    save_bon = self.get_save_bon(save, target)

                save_goal_score = self.get_dc(caster) - save_bon

                chance_pass = max(min((20 - save_goal_score + 1) / 20, 0.95), 0.05)

                avg_dmg = (avg_dmg_pass * chance_pass) + (avg_dmg_fail * (1 - chance_pass))

                # print("Average damage on pass: {}".format(avg_dmg_pass))
                # print("Average damage on fail: {}".format(avg_dmg_fail))
                # print("dc: {}".format(self.get_dc(caster)))
                # print("Target save bon: {}".format(save_bon))
                # print("Goal score: {}".format(save_goal_score))
                # print("Chance to pass: {}".format(chance_pass))

            # print("Average damage: {}".format(avg_dmg))

            avg_dmg_tot += avg_dmg

        return avg_dmg_tot

    def cast_on(self, target, caster):

        cl = caster.cl()

        spell_dmg = 0
        spell_log = []

        target_sr = target.get_sr()

        if self.sr and target_sr > 0:
            spell_log.append("{0} is making a caster level check against sr {1}".format(caster.name, target_sr))

            sr_goal_score = target_sr - cl

            sr_roll = random.randint(1, 20)

            if sr_roll < sr_goal_score:
                spell_log.append("{0} failed their caster level check ({1})".format(caster.name, sr_roll + cl))
                return [spell_dmg, spell_log]
            else:
                spell_log.append("{0} passed their caster level check ({1})".format(caster.name, sr_roll + cl))

        for damage in self.dmg:

            spell_sub_dmg = 0

            [dice, lvlmax, save, types] = damage

            if dice[0] == "L":
                if lvlmax == 0:
                    dice[0] = cl
                else:
                    dice[0] = min(cl, lvlmax)

            log_line = "{0} is dealing {1}d{2}".format(caster.name, dice[0], dice[1])
            if dice[2] != 0:
                log_line += "{:+d}".format(dice[2])
            log_line += " damage"
            if types:
                log_line += " ("
                type_array = []
                for l in types:
                    type_array.append(self.type_parse[l])
                log_line += ", ".join(type_array)
                log_line += ")"
            log_line += " to {}".format(target.name)

            spell_log.append(log_line)

            for i in range(0, dice[0]):
                spell_sub_dmg += random.randint(1, dice[1])

            spell_sub_dmg += dice[2]

            for l in types:
                dmgtype = self.type_parse[l]

                if target.is_weak(dmgtype):
                    spell_log.append("{0} is vulnerable to {1}; {0} takes 1.5x damage".format(target.name, dmgtype))
                    spell_sub_dmg *= 1.5
                elif target.res_amt(dmgtype) > 0:
                    spell_log.append("{0} has {1} resistance {2}".format(target.name, dmgtype, target.res_amt(dmgtype)))
                    spell_sub_dmg -= target.res_amt(dmgtype)
                    if spell_sub_dmg < 0:
                        spell_sub_dmg = 0
                elif target.is_immune(dmgtype):
                    spell_log.append("{0} is immune to {1}".format(target.name, dmgtype))
                    spell_sub_dmg = 0

            if save != "N" and (len(save) == 2 or save[2] != "h"):

                save_bon = self.get_save_bon(save, target)
                dc = self.get_dc(caster)

                spell_log.append(
                    "{} is making a {} save against dc {}".format(target.name, self.save_parse[save[0]], dc))

                [save_pass, save_roll] = target.check_save(save[0], dc)

                if not save_pass:
                    spell_log.append("{} failed their save ({})".format(target.name, save_roll))
                    if save_roll == "No save":
                        pass
                    elif save[0] == "R" and "improved evasion" in target.da:
                        spell_log.append("{} has improved evasion and so takes half damage".format(target.name))
                        spell_sub_dmg //= 2
                else:
                    spell_log.append("{} passed their save ({})".format(target.name, save_roll))
                    if save[1] == "2":
                        if save[0] == "R" and "evasion" in target.da:
                            spell_log.append("{} has evasion and so takes no damage".format(target.name))
                            spell_sub_dmg = 0
                        else:
                            spell_log.append("{} takes half damage".format(target.name))
                            spell_sub_dmg //= 2
                            spell_sub_dmg = max(1, spell_sub_dmg)
                    if save[1] == "0":
                        spell_log.append("{} takes no damage".format(target.name))
                        spell_sub_dmg = 0

            spell_dmg += spell_sub_dmg

        return [spell_dmg, spell_log]

    #############################
    #
    # Utility functions

    @staticmethod
    def get_save_bon(save, target):
        save_bon = 0

        if save[0] == "F":
            save_bon = target.get_fort()
        if save[0] == "R":
            save_bon = target.get_ref()
        if save[0] == "W":
            save_bon = target.get_will()

        return save_bon

    def copy(self):
        return copy.copy(self)
