def arcane_strike(self):
    return "Arcane Strike" in self.feat_list

def arcane_strike_bon(self):
    if self.arcane:
        return int(self.CL / 5) + 1
    else:
        return 0

def bullseye_shot(self):
    return "Bullseye Shot" in self.feat_list and point_blank_shot(self) and precise_shot(self) and self.bab[0]>=5

def bullseye_shot_bon(self, FRA):
    if bullseye_shot(self):
        return 4
    else:
        return 0

def combat_expertise(self):
    return "Combat Expertise" in self.feat_list and self.inttot() >= 13

def combat_reflexes(self):
    return "Combat Reflexes" in self.feat_list

def critical_focus(self):
    return "Critical Focus" in self.feat_list and self.bab[0] >= 9

def critical_focus_bon(self):
    if critical_focus(self):
        return 4
    else:
        return 0

def deadly_aim(self):
    return "Deadly Aim" in self.feat_list and self.dextot() >= 13 and self.bab >= 1

def deadly_aim_bon(self):
    if deadly_aim(self) and "R" in self.weap_type():
        return int((self.bab[0] / 5) + 1) * 2
    else:
        return 0

def deadly_aim_pen(self):
    if deadly_aim(self):
        return int((self.bab[0] / 5) + 1) * -1
    else:
        return 0

def dodge(self):
    return "Dodge" in self.feat_list and self.dextot() >= 13

def dodge_bon(self):
    if dodge(self):
        return 1
    else:
        return 0

def favored_defense(self, type="", subtype=""):
    return "Favored Defense ({})".format(type) in self.feat_list or "Favored Defense ({} ({}))".format(type,subtype) in self.feat_list

def favored_defense_bon(self, type, subtype):
    if favored_defense(self, type, subtype) and type in self.ranger_fe_types():
        return int(self.ranger_fe_bon(type) / 2)
    else:
        return 0

def great_fortitude(self):
    return "Great Fortitude" in self.feat_list

def great_fortitude_bon(self):
    if great_fortitude(self):
        return 2
    else:
        return 0

def imp_unarmed_strike(self):
    return "Improved Unarmed Strike" in self.feat_list

def improved_critical(self, weap=None):
    if weap == None:
        weap = self.slots["wield"][0]

    return "Improved Critical ({})".format(self.weap_basename(weap)) in self.feat_list

def improved_disarm(self):
    return "Improved Disarm" in self.feat_list and self.inttot() >= 13 and combat_expertise(self)

def improved_disarm_bon(self):
    if improved_disarm(self):
        return 2
    else:
        return 0

def improved_trip(self):
    return "Improved Trip" in self.feat_list and self.inttot() >= 13 and combat_expertise(self)

def improved_trip_bon(self):
    if improved_trip(self):
        return 2
    else:
        return 0

def improved_initiative(self):
    return "Improved Initiative" in self.feat_list

def improved_initiative_bon(self):
    if improved_initiative(self):
        return 4
    else:
        return 0

def iron_will(self):
    return "Iron Will" in self.feat_list

def iron_will_bon(self):
    if iron_will(self):
        return 2
    else:
        return 0

def lightning_reflexes(self):
    return "Lightning Reflexes" in self.feat_list

def lightning_reflexes_bon(self):
    if lightning_reflexes(self):
        return 2
    else:
        return 0

def manyshot(self):
    return "Manyshot" in self.feat_list and point_blank_shot(self) and rapid_shot(self) and self.bab[0] >= 6

def power_attack(self):
    return "Power Attack" in self.feat_list and self.strtot() >= 13 and self.bab[0] >= 1

def power_attack_bon(self, off=False):
    if not power_attack(self):
        return 0

    pa_bon = int((self.bab[0] / 5) + 1) * 2

    if self.weap_hands() == "2":
        pa_bon = int(pa_bon * 3 / 2)
    elif off:
        pa_bon = int(pa_bon / 2)

    return pa_bon

def power_attack_pen(self):
    if not power_attack(self):
        return 0

    return int((self.bab[0] / 5) + 1) * -1

def point_blank_shot(self):
    return "Point-Blank Shot" in self.feat_list

def pbs_bon(self):
    if point_blank_shot(self):
        return 1
    else:
        return 0

def quick_draw(self):
    return "Quick Draw" in self.feat_list and self.bab[0] >= 1

def rapid_shot(self):
    return "Rapid Shot" in self.feat_list and point_blank_shot(self) and self.dextot() >= 13

def rapid_shot_pen(self):
    if rapid_shot(self):
        return -2
    else:
        return 0

def snap_shot(self):
    return "Snap Shot" in self.feat_list and self.dextot() >= 13 and point_blank_shot(self) and rapid_shot(self) and weapon_focus(self) and self.bab[0] >= 6

def snap_shot_imp(self):
    return "Improved Snap Shot" in self.feat_list and self.dextot() >= 15 and point_blank_shot(self) and rapid_shot(self) and weapon_focus(self) and self.bab[0] >= 9

def stunning_fist(self):
    return "Stunning Fist" in self.feat_list and (self.dextot() >= 13 and self.wistot() >= 13 and imp_unarmed_strike(self) and self.bab[0] >= 8) or (self.charClass == "Monk")

def toughness(self):
    return "Toughness" in self.feat_list

def toughness_bon(self):
    if toughness(self):
        if self.HD <= 3:
            return 3
        else:
            return self.HD
    else:
        return 0

def two_weapon_fighting(self):
    return "Two-Weapon Fighting" in self.feat_list and self.dextot() >= 15

def two_weapon_fighting_bon(self, override=False):
    if two_weapon_fighting(self) or override:
        return [2,6]
    else:
        return [0,0]

def two_weapon_fighting_greater(self):
    return "Greater Two-Weapon Fighting" in self.feat_list and two_weapon_fighting(self) and self.two_weapon_fighting_imp and self.bab[0]>=11

def two_weapon_fighting_imp(self):
    return "Improved Two-Weapon Fighting" in self.feat_list and two_weapon_fighting(self) and self.bab[0]>=6

def weapon_finesse(self):
    return "Weapon Finesse" in self.feat_list

def weapon_finesse_weap(self, weap):
    if "L" in self.weap_type(weap) or "Natural" in self.weap_group(weap):
        return True
    if self.weap_name(weap) in ["elven curve blade","rapier","whip","spiked chain"]:
        return True
    
    return False

def weapon_focus(self, weap=None):
    if weap == None:
        weap = self.slots["wield"][0]

    return "Weapon Focus ({})".format(self.weap_basename(weap)) in self.feat_list and self.bab[0] >= 1
    #and self.weap_prof(weap)