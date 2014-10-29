class Combat:
    """Combat round processing"""

    import random

    def __init__(self):
        self.fighters = []
        self.defeated = []
        self.combatlog = ""
        self.round = 1

    def log(self,entry):
        self.combatlog = self.combatlog + entry

    def add_fighter(self, fighter):
        fighter.target = None
        fighter.targeting = "Closest"
        fighter.action = "Attack"
        self.fighters.append(fighter)
        self.log("{0} enters combat at {1}\n{0} at {2}\n".format(fighter.name, fighter.loc, fighter.print_hp()))

    def disable_fighter(self, fighter):
        self.fighters.remove(fighter)
        self.defeated.append(fighter)
        self.log("{} leaves combat\n".format(fighter.name))

    def enable_fighter(self, fighter):
        self.defeated.remove(fighter)
        self.fighters.append(fighter)
        self.log("{0} enters combat at {1}\n{0} at {2}\n".format(fighter.name, fighter.loc, fighter.print_hp()))

    def set_mat(self, mat):
        self.mat = mat

    def set_target(self, fighter1, fighter2):
        self.log("{} targets {}\n".format(fighter1.name, fighter2.name))
        fighter1.target = fighter2

    def clear_target(self, fighter):
        self.log("{} targets no one\n".format(fighter.name))
        fighter.target = None

    def move_path(self, fighter, path):
        for tile in path:
            self.move_to_tile(fighter, tile)

    def move_to_tile(self, fighter, tile):
        self.log("{} moves from {} to {}\n".format(fighter.name, fighter.loc, tile))
        fighter.loc = tile

    def attack(self, fighter, target, FRA):
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attacks {}: {}\n".format(fighter.name, target.name,fighter.print_atk_line(dist_to_target, FRA)))
        dmg = fighter.attack(target.get_AC(type=fighter.type, subtype=fighter.subtype), dist_to_target, FRA)

        self.log("{} takes {} damage\n".format(target.name, dmg[0]))
        self.log("  ({})\n".format(', '.join(dmg[1])))
        target.take_damage(dmg[0])
        self.log("{} at {}\n".format(target.name, fighter.target.print_hp()))

    def set_init(self):
        self.init_order = []
        for fighter in self.fighters:
            init_roll = self.random.randint(1,20)
            init_roll = init_roll + fighter.init
            self.init_order.append([fighter, init_roll])

        self.init_order = sorted(self.init_order, key=lambda x:x[1], reverse=True)

        self.log(self.output_init())

    def check_death(self, fighter):
         if fighter.damage_con != "Normal":
            self.log("{} is {}\n".format(fighter.name, fighter.damage_con))
            self.disable_fighter(fighter)
            return True
         return False

    def combat_round(self):
        self.log("\nRound {}\n\n".format(self.round))
        for init_entry in self.init_order:
            fighter = init_entry[0]

            #############################
            #
            # Skip disabled/defeated combatants

            if fighter in self.defeated:
                continue

            #############################
            #
            # Perform set action

            if fighter.action == "Attack":

                #############################
                #
                # Determine target if necessary

                if fighter.target == None:
                    if fighter.targeting == "Closest":
                        self.log("{} targets closest enemy\n".format(fighter.name))
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
                            self.log("{0} has no target; {0} does nothing\n".format(fighter.name))
                            continue

                dist_to_target = self.mat.dist_ft(fighter.loc, fighter.target.loc)
                self.log("Distance from {} to {}: {} ft.\n".format(fighter.name, fighter.target.name, dist_to_target))
                if self.mat.can_attack(fighter, fighter.target):
                    FRA = True
                else:
                    FRA = False
                    path = self.mat.partial_path(fighter, fighter.target, fighter.move)
                    self.move_path(fighter, path)

                if self.mat.can_attack(fighter, fighter.target):
                    self.attack(fighter, fighter.target, FRA)
                else:
                    path = self.mat.partial_path(fighter, fighter.target, fighter.move)
                    self.move_path(fighter, path)

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

    def output_init(self):
        output = ""
        for fighter in self.init_order:
            output = output + "{} ({:+d}): {}\n".format(fighter[0].name,fighter[0].init,fighter[1])

        return output

    def output_log(self):
        return self.combatlog