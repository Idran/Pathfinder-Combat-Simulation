class Combat:
    """Combat round processing"""

    import random

    def __init__(self):
        self.fighters = []
        self.fighternames = []
        self.aoo_counts = dict()
        self.threat_tiles = dict()
        self.defeated = []
        self.combatlog = []
        self.round = 1
        self.has_acted = dict()

    def log(self,entry):
        self.combatlog.append(entry)

    def log_del(self):
        self.combatlog.pop()

    def add_fighter(self, fighter):
        if fighter.name in self.fighternames:
            raise StandardError("Fighter named {} already fighting".format(fighter.name))

        fighter.target = None
        self.set_targeting(fighter, "Closest")
        self.set_tactic(fighter, "Attack")
        self.fighters.append(fighter)
        self.fighternames.append(fighter.name)

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

    def set_tactic(self, fighter, tactic):
        fighter.tactic = tactic

    def set_targeting(self, fighter, targeting):
        fighter.targeting = targeting

    def set_target(self, fighter1, fighter2):
        self.log("{} targets {}".format(fighter1.name, fighter2.name))
        fighter1.target = fighter2

    def clear_target(self, fighter):
        self.log("{} targets no one".format(fighter.name))
        fighter.target = None

    def check_for_aoo(self, fighter, tile):
        for foe in self.fighters:
            if foe.side == fighter.side:
                continue

            if tile in self.threat_tiles[foe.name] and foe.can_aoo() and self.aoo_counts[foe.name] < foe.get_aoo_count():
                self.log("{} takes an AoO against {}".format(foe.name,fighter.name))
                self.aoo_counts[foe.name] = self.aoo_counts[foe.name] + 1
                self.attack(foe, fighter, False)

        # Note: current test only works for 1x1 combatants, fix in future

    def reset_aoo_count(self):
        for fighter in self.fighters:
            self.aoo_counts[fighter.name] = 0

    def set_init(self):
        self.init_order = []
        for fighter in self.fighters:
            init_roll = self.random.randint(1,20)
            init_roll = init_roll + fighter.get_init()
            self.init_order.append([fighter, init_roll])

        self.init_order = sorted(self.init_order, key=lambda x:x[1], reverse=True)

        self.log(self.output_init())

    def check_death(self, fighter):
         if fighter.damage_con != "Normal":
            self.log("{} is {}".format(fighter.name, fighter.damage_con))
            self.disable_fighter(fighter)
            return True
         return False

    def combat_round(self):
        self.log("\nRound {}\n".format(self.round))
        self.reset_aoo_count()
        for init_entry in self.init_order:
            fighter = init_entry[0]
            if not self.has_acted[fighter.name]:
                self.has_acted[fighter.name] = True
                fighter.drop_condition("Flat-Footed")

            #############################
            #
            # Skip disabled/defeated combatants

            if fighter in self.defeated:
                continue

            #############################
            #
            # Determine target if necessary

            if fighter.target in self.defeated:
                self.clear_target(fighter)

            if fighter.target == None:
                if fighter.targeting == "Closest":
                    self.log("{} targets closest enemy".format(fighter.name))
                    target_dist = 20000
                    pot_target = None

                    for other in self.fighters:
                        if other.side != fighter.side:
                            other_dist = self.mat.dist_tile(fighter.loc, other.loc)
                            if other_dist < target_dist:
                                target_dist = other_dist
                                pot_target = other

                    if pot_target != None:
                        self.set_target(fighter,pot_target)
                    else:
                        self.log("{0} has no target; {0} does nothing".format(fighter.name))
                        continue

            dist_to_target = self.mat.dist_ft(fighter.loc, fighter.target.loc)
            self.log("Distance from {} to {}: {} ft.".format(fighter.name, fighter.target.name, dist_to_target))

            survive = True

            #############################
            #
            # Perform set action

            ###########################################

            if fighter.tactic == "Attack":

                survive = self.move_attack(fighter, fighter.target)

            ###########################################

            elif fighter.tactic == "Close":

                survive = self.close_attack(fighter, fighter.target)

            else:

                pass

            if not survive:
                continue

            if self.check_death(fighter.target):
                self.clear_target(fighter)

        self.round = self.round + 1


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

###################################################################
#
# Round actions

    #############################
    #
    # Movement functions

    def move_to_target(self, fighter, target, nolog=False):
        if not nolog:
            self.log("{} attempts to move to {}".format(fighter.name,target.name))
        tot_moved = 0
        path = self.mat.partial_path(fighter, target, fighter.move)
        for tile in path:
            if self.mat.can_attack(fighter, target):
                return tot_moved
            if not self.move_to_tile(fighter, tile):
                return -1
        return tot_moved

    def move_path(self, fighter, path):
        self.log("{} attempts to move to {}".format(fighter.name,path[-1]))
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

    def attack(self, fighter, target, FRA=False):
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attacks {}: {}".format(fighter.name, target.name,fighter.print_atk_line(dist_to_target, FRA)))
        dmg = fighter.attack(target.get_AC(type=fighter.type, subtype=fighter.subtype), dist_to_target, FRA, fighter.type, fighter.subtype)

        self.log("{} takes {} damage".format(target.name, dmg[0]))
        self.log("  ({})".format(', '.join(dmg[1])))
        target.take_damage(dmg[0])
        self.log("{} at {}".format(target.name, fighter.target.print_hp()))

    #############################
    #
    # move_attack (Attack): Move towards target if necessary. If fighter can attack, do so, otherwise move again.

    def move_attack(self, fighter, target, move=1, FRA=True):
        survive = True

        for moves in range(move):
            tot_moved = self.move_to_target(fighter, target)
            if tot_moved == 0:
                self.log_del()
            elif tot_moved < 0:
                return False
            else:
                FRA = False

        if self.mat.can_attack(fighter, target):
            self.attack(fighter, target, FRA)
        else:
            tot_moved = self.move_to_target(fighter, target, nolog=True)

        return tot_moved >= 0

    #############################
    #
    # close_attack (Close): Switch to best ranged weapon (if any) and run move_attack. Once within melee range, switch to best melee weapon and run move_attack.

    def close_attack(self, fighter, target):

        ranged = fighter.best_ranged_weap(fighter.target)
        melee = fighter.best_melee_weap(fighter.target)
        curr_weap = fighter.weap
        move = 1
        FRA = True

        fighter.set_weapon(melee)

        if ranged < 0 or self.mat.can_attack(fighter, fighter.target):
            if curr_weap != melee:
                self.log("{} switches weapons to {}".format(fighter.name,fighter.weap_name()))
                if fighter.weap_swap() == "move":
                    if fighter.bab[0] == 0:
                        move = 0
                    else:
                        FRA = False
            return self.move_attack(fighter, target, move, FRA)
        else:
            fighter.set_weapon(ranged)
            if curr_weap != ranged:
                self.log("{} switches weapons to {}".format(fighter.name,fighter.weap_name()))
                if fighter.weap_swap() == "move":
                    if fighter.bab[0] == 0:
                        move = 0
                    else:
                        FRA = False
            return self.move_attack(fighter, target, move, FRA)

###################################################################
#
# Output functions

    def output_init(self):
        output = ""
        for fighter in self.init_order:
            output = output + "{} ({:+d}): {}\n".format(fighter[0].name,fighter[0].init,fighter[1])

        return output

    def output_log(self):
        return '\n'.join(self.combatlog)