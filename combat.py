import random
import sys


class Combat:
    """Combat round processing"""

    def __init__(self):
        self.fighters = []
        self.fighternames = []
        self.fighter_id_index = dict()
        self.aoo_counts = dict()
        self.threat_tiles = dict()
        self.defeated = []
        self.combatlog = []
        self.round = 1
        self.has_acted = dict()
        self.mat = None
        self.init_order = []

    def __sizeof__(self):
        return object.__sizeof__(self) + \
               sum(sys.getsizeof(v) for v in self.__dict__.values())

    def clear_out(self):
        for fighter in self.fighters:
            self.mat.remove_token(fighter)
            del fighter

        del self.mat

    def log(self, entry=""):
        self.combatlog.append(entry)

    def log_del(self):
        self.combatlog.pop()

    def add_fighter(self, fighter):
        if fighter.name in self.fighternames:
            raise Exception("Fighter named {} already fighting".format(fighter.name))

        fighter.set_ai(self.mat)
        fighter.target = None
        self.set_targeting(fighter, "Closest")
        self.set_tactic(fighter, "Attack")

        self.fighters.append(fighter)
        self.fighternames.append(fighter.name)
        self.fighter_id_index[fighter.id] = fighter

        self.aoo_counts[fighter.name] = 0
        self.threat_tiles[fighter.name] = self.mat.threatened_tiles(fighter)
        self.has_acted[fighter.name] = False
        fighter.set_condition("Flat-Footed")

        self.mat.add_token(fighter)

        self.log("{0} enters combat at {1}\n{0} at {2}".format(fighter.name, fighter.loc, fighter.print_hp()))

    def disable_fighter(self, fighter):
        self.fighters.remove(fighter)
        self.defeated.append(fighter)
        self.log("{} leaves combat".format(fighter.name))

    def enable_fighter(self, fighter):
        self.defeated.remove(fighter)
        self.fighters.append(fighter)
        self.log("{0} enters combat at {1}\n{0} at {2}".format(fighter.name, fighter.loc, fighter.print_hp()))

    def set_mat(self, mat):
        self.mat = mat

    @staticmethod
    def set_tactic(fighter, tactic):
        fighter.set_tactic(tactic)

    @staticmethod
    def set_targeting(fighter, targeting):
        fighter.set_targeting(targeting)

    def clear_target(self, fighter):
        self.log("{} targets no one".format(fighter.name))
        fighter.target = None

    def aoo_possible(self, fighter, tile):
        for foe in self.fighters:
            if foe.side == fighter.side:
                continue

            if tile in self.threat_tiles[foe.name] and self.can_attempt_aoo(foe):
                return True

        return False

        # Note: current test only works for 1x1 combatants, fix in future

    def check_for_aoo(self, fighter, tile):
        for foe in self.fighters:
            if foe.side == fighter.side:
                continue

            if tile in self.threat_tiles[foe.name] and self.can_attempt_aoo(foe):
                self.take_aoo(fighter, foe)

                # Note: current test only works for 1x1 combatants, fix in future

    def can_attempt_aoo(self, target):
        return target.can_aoo() and self.aoo_counts[target.name] < target.get_aoo_count()

    def take_aoo(self, fighter, target):
        self.log("{} takes an AoO against {}".format(target.name, fighter.name))
        self.aoo_counts[target.name] += 1
        self.attack(target, fighter, None, False)

    def reset_aoo_count(self):
        for fighter in self.fighters:
            self.aoo_counts[fighter.name] = 0

    def set_init(self):
        self.init_order = []
        for fighter in self.fighters:
            init_roll = random.randint(1, 20)
            init_roll = init_roll + fighter.get_init()
            self.init_order.append([fighter, init_roll])

        self.init_order = sorted(self.init_order, key=lambda x: x[1], reverse=True)

        self.log(self.output_init())

    def check_death(self, fighter):
        if fighter not in self.fighters:
            return True
        if fighter is None:
            return False
        if fighter.damage_con not in ["Normal", "Disabled"]:
            self.log("{} is {}".format(fighter.name, fighter.damage_con))
            self.disable_fighter(fighter)
            return True
        return False

    def combat_round(self):
        self.log("\nRound {}\n".format(self.round))
        self.reset_aoo_count()
        for init_entry in self.init_order:
            fighter = init_entry[0]
            round_changes = fighter.round_pass()
            for cond in round_changes[0]:
                self.log("{} loses {}".format(fighter.name, cond))

            #############################
            #
            # Skip disabled/defeated combatants

            if fighter in self.defeated:
                continue

            #############################
            #
            # Skip combatants that cannot act temporarily

            act_status = fighter.can_act()

            if act_status[1] in ["Dying", "Dead"]:
                self.log("{} is {}".format(fighter.name, act_status[1]))
                self.disable_fighter(fighter)
                continue

            if not act_status[0]:
                self.log("{} unable to act due to {} condition".format(fighter.name, act_status[1]))
                continue

            #############################
            #
            # Remove FF from those actually acting                

            if not self.has_acted[fighter.name]:
                self.has_acted[fighter.name] = True
                fighter.drop_condition("Flat-Footed")

            #############################
            #
            # Run AI routine

            if fighter.target in self.defeated:
                self.clear_target(fighter)

            result = fighter.ai.act()

            self.combatlog += result[1]

            survive = True

            post_damage = 0

            iter_result = iter(result[0])

            print("{} action list:".format(fighter.name))

            for action in iter_result:
                print("\t{}".format(action))
                if fighter.target:
                    pre_damage = post_damage
                    post_damage = fighter.target.damage
                else:
                    pre_damage = 0
                    post_damage = 0
                if action[0] == "end":
                    break
                elif action[0] == "if":
                    if action[1] == "dmg":
                        if post_damage == pre_damage:
                            self.log("Conditional failed, no damage taken")
                            next(iter_result)
                            continue
                        else:
                            self.log("Conditional passed")
                elif action[0] == "move":
                    survive = self.move_path(fighter, action[1])
                elif action[0] == "attack":
                    self.attack(fighter, fighter.target, fighter.target_model, action[1])
                elif action[0] == "satk":
                    self.satk(fighter, fighter.target, fighter.target_model, action[1])
                elif action[0] == "cast":
                    survive = self.cast(fighter, action[2], action[1])
                elif action[0] == "stand":
                    self.log("{} stands up".format(fighter.name))
                    fighter.drop_condition("Prone")
                    self.check_for_aoo(fighter, fighter.loc)
                    if self.check_death(fighter):
                        break
                elif action[0] == "swap":
                    fighter.set_weapon(action[1])
                    if type(action[1]) is not list:
                        self.log("{} switches weapons to {}".format(fighter.name, fighter.weap_name(action[1])))
                    else:
                        log_line = "{} switches weapons to ".format(fighter.name)
                        log_array = []
                        for weap in action[1]:
                            log_array.append(fighter.weap_name(weap))
                        log_line += ", ".join(log_array)
                        self.log(log_line)
                elif action[0] == "cond":
                    self.set_cond(fighter, fighter.target, fighter.target_model, action[1:])
                elif action[0] == "disarm":
                    self.disarm(fighter, fighter.target, fighter.target_model)
                elif action[0] == "trip":
                    self.trip(fighter, fighter.target, fighter.target_model)
                else:
                    pass

                if not survive:
                    break

            if not survive:
                continue

            if self.check_death(fighter.target):
                self.clear_target(fighter)

        self.round += 1
        if self.round == 51:
            raise OverflowError("Round count exceeded 50, quitting.")

    def check_combat_end(self):
        active_side = -1
        end = True
        for fighter in self.fighters:
            if fighter.side != active_side:
                if active_side == -1:
                    active_side = fighter.side
                else:
                    end = False
                    break

        return end

    def winning_side(self):
        active_side = -1
        for fighter in self.fighters:
            if fighter.side != active_side:
                if active_side == -1:
                    active_side = fighter.side
                else:
                    active_side = -1
                    break

        return active_side

    ###################################################################
    #
    # Round actions

    #############################
    #
    # Movement functions

    def move_to_target(self, fighter, target, nolog=False):
        if not nolog:
            self.log("{} attempts to move to {}".format(fighter.name, target.name))
        tot_moved = 0
        path = self.mat.partial_path(fighter, target, fighter.get_move())
        for tile in path:
            if self.mat.can_attack(fighter, target):
                return tot_moved
            if not self.move_to_tile(fighter, tile):
                return -1
        return tot_moved

    def move_path(self, fighter, path):
        self.log("{} attempts to move to {}".format(fighter.name, path[-1]))
        survive = False
        for tile in path:
            survive = self.move_to_tile(fighter, tile)
            if not survive:
                break
        return survive

    def move_to_tile(self, fighter, tile):
        self.check_for_aoo(fighter, fighter.loc)

        if not self.check_death(fighter):
            self.log("{} moves from {} to {}".format(fighter.name, fighter.loc, tile))
            self.mat.move_token(fighter, tile)
            self.threat_tiles[fighter.name] = self.mat.threatened_tiles(fighter)
            return True
        else:
            return False

    #############################
    #
    # Attack functions

    def attack(self, fighter, target, target_model, full_attack=False, fob=False):
        if fighter.has("Prone") and "R" in fighter.weap_type() and "Crossbows" not in fighter.weap_group():
            self.log("{0} cannot attack; {0} is Prone".format(fighter.name))
            return False
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attacks {}: {}".format(fighter.name, target.name,
                                            fighter.print_all_atks(dist_to_target, full_attack, target.type_mon, target.subtype)))
        dmg = fighter.attack(target.get_ac(type_mon=fighter.type_mon, subtype=fighter.subtype), dist_to_target, full_attack,
                             fighter.type_mon, fighter.subtype)

        self.log("{} takes {} damage".format(target.name, dmg[0]))
        self.log("  ({})".format(fighter.print_atk_dmg(dmg[1])))
        target.take_damage(dmg[0])
        if target_model is not None:
            target_model.take_damage(dmg[0])
        self.log("{} at {}".format(target.name, target.print_hp()))

    def satk(self, fighter, target, target_model, satk_type):
        if satk_type in ["fob"]:
            if fighter.has("Prone") and "R" in fighter.weap_type() and "Crossbows" not in fighter.weap_group():
                self.log("{0} cannot attack; {0} is Prone".format(fighter.name))
                return False

        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)

        if satk_type == "fob":
            self.log("{} attacks {}: {}".format(fighter.name, target.name,
                                                fighter.print_atk_line(dist=dist_to_target, fob=True)))

            dmg = fighter.attack(target.get_ac(type_mon=fighter.type_mon, subtype=fighter.subtype), dist_to_target, True,
                                 fighter.type_mon, fighter.subtype, fob=True)

            self.log("{} takes {} damage".format(target.name, dmg[0]))
            self.log("  ({})".format(fighter.print_atk_dmg(dmg[1])))
            target.take_damage(dmg[0])
            target_model.take_damage(dmg[0])
            self.log("{} at {}".format(target.name, target.print_hp()))

    def set_cond(self, fighter, target, target_model, cond_info):

        cond_type, save_type, dc_type, rds = cond_info
        rds = int(rds)

        self.log("{} is attempting to apply {} to {}".format(fighter.name, cond_type, target.name))

        save_type = save_type[0]

        save_type_long = {"F": "fortitude", "R": "reflex", "W": "will"}[save_type]

        dc_stat_bon = 0

        if dc_type == "str":
            dc_stat_bon = fighter.stat_bonus(fighter.strtot())
        elif dc_type == "dex":
            dc_stat_bon = fighter.stat_bonus(fighter.dextot())
        elif dc_type == "con":
            dc_stat_bon = fighter.stat_bonus(fighter.contot())
        elif dc_type == "int":
            dc_stat_bon = fighter.stat_bonus(fighter.inttot())
        elif dc_type == "wis":
            dc_stat_bon = fighter.stat_bonus(fighter.wistot())
        elif dc_type == "cha":
            dc_stat_bon = fighter.stat_bonus(fighter.chatot())

        # dc_stat_bon = 99

        dc = 10 + (fighter.level // 2) + dc_stat_bon

        self.log("{} is making a {} save against dc {}".format(target.name, save_type_long, dc))

        cond_check = target.check_save(save_type, dc)

        if not cond_check[0]:
            self.log("{} failed their save ({})".format(target.name, cond_check[1]))
            self.log("{} now has the {} condition".format(target.name, cond_type))
            target.set_condition(cond_type, rds)
            target_model.set_condition(cond_type, rds)
            if cond_type == "Stunned":
                self.log("{} has dropped all wielded items".format(target.name))
        else:
            self.log("{} passed their save ({})".format(target.name, cond_check[1]))

    @staticmethod
    def maneuver_check(fighter, target, dist, man):
        cmd = target.CMD(fighter.type_mon, fighter.subtype, target.has("Flat-Footed"), man)
        result = fighter.check_CMB(cmd, dist, target.type_mon, target.subtype, man)

        return result

    def disarm(self, fighter, target, target_model):
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attempts to disarm {}".format(fighter.name, target.name))
        if self.can_attempt_aoo(target):
            self.take_aoo(fighter, target)
        if not self.check_death(fighter):
            result = self.maneuver_check(fighter, target, dist_to_target, "Disarm")
            if result[0]:
                self.log("{} succeeds".format(fighter.name))
                item = self.drop(target, target_model, 0)
                self.log("{} drops {}".format(target.name, item.fullname()))
                if result[1] >= 10:
                    item = self.drop(target, target_model, 1)
                    if item:
                        self.log("{} drops {}".format(target.name, item.fullname()))
            else:
                self.log("{} fails to disarm".format(fighter.name))
                if result[1] <= -10:
                    item = self.drop(fighter, None, 0)
                    if item:
                        self.log("{} drops {}".format(fighter.name, item.fullname()))
            return True
        else:
            return False

    def trip(self, fighter, target, target_model):
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attempts to trip {}".format(fighter.name, target.name))
        if self.can_attempt_aoo(target):
            self.take_aoo(fighter, target)
        if not self.check_death(fighter):
            result = self.maneuver_check(fighter, target, dist_to_target, "Trip")
            if result[0]:
                self.log("{} succeeds".format(fighter.name))
                self.log("{} is tripped".format(target.name))
                target.set_condition("Prone")
                target_model.set_condition("Prone")
            else:
                self.log("{} fails to disarm".format(fighter.name))
                if result[1] <= -10:  # and self.can_trip(fighter):
                    self.log("{} is tripped".format(fighter.name))
                    fighter.set_condition("Prone")
            return True
        else:
            return False

    @staticmethod
    def drop(target, target_model, slot):
        ret_val = target.drop("wield,{}".format(slot))
        if target_model is not None:
            temp = target_model.drop("wield,{}".format(slot))
        return ret_val

    #############################
    #
    # Magic functions

    def cast(self, fighter, target_list, spell):

        cast_defensive = False
        sl = spell.lvl_parse()[fighter.char_class]

        if self.aoo_possible(fighter, fighter.loc):
            conc_bon = fighter.concentration()
            dc = 15 + 2 * sl
            check_goal = dc - conc_bon

            if check_goal <= 10:
                self.log(
                    "{0} casts defensively; {0} is making a concentration check against dc {1}".format(fighter.name,
                                                                                                       dc))
                conc_result = fighter.check_conc(dc)
                if conc_result[0]:
                    self.log("{} passed their concentration check ({})".format(fighter.name, conc_result[1]))
                    cast_defensive = True
                else:
                    self.log("{0} failed their concentration check ({1}); {0} loses spell".format(fighter.name,
                                                                                                  conc_result[1]))
                    fighter.cast(spell)
                    return True

        if not cast_defensive:
            pre_dmg = fighter.damage
            self.check_for_aoo(fighter, fighter.loc)
            if self.check_death(fighter):
                return False
            if fighter.damage > pre_dmg:
                damage_taken = fighter.damage - pre_dmg
                dc = 10 + damage_taken + sl
                self.log("{0} took {1} damage while casting; {0} is making a concentration check against dc {2}".format(
                    fighter.name, damage_taken, dc))
                conc_result = fighter.check_conc(dc)
                if conc_result[0]:
                    self.log("{} passed their concentration check ({})".format(fighter.name, conc_result[1]))
                else:
                    self.log("{0} failed their concentration check ({1}); {0} loses spell".format(fighter.name,
                                                                                                  conc_result[1]))
                    fighter.cast(spell)
                    return True

        fighter.cast(spell)
        for target in target_list:
            if target.model:
                target_model = target
                target = self.fighter_id_index[target.id]
            else:
                target_model = fighter.ai.mental_model[target.id]
            result = spell.cast_on(target, fighter)
            self.combatlog += result[1]
            spell_dmg = result[0]
            self.log("{} takes {} damage".format(target.name, spell_dmg))
            if spell_dmg > 0:
                target.take_damage(spell_dmg)
                target_model.take_damage(spell_dmg)
                self.log("{} at {}".format(target.name, target.print_hp()))

        return True

    ###################################################################
    #
    # Output functions

    def output_init(self):
        output = ""
        for fighter in self.init_order:
            output += "{} ({:+d}): {}\n".format(fighter[0].name, fighter[0].get_init(), fighter[1])

        return output

    def output_log(self):
        return '\n'.join(self.combatlog)
