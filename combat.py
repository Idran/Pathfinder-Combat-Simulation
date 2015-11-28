class Combat:
    """Combat round processing"""

    import random
    import sys

    def __init__(self):
        self.fighters = []
        self.fighternames = []
        self.aoo_counts = dict()
        self.threat_tiles = dict()
        self.defeated = []
        self.combatlog = []
        self.round = 1
        self.has_acted = dict()
        
    def __sizeof__(self):
        return object.__sizeof__(self) + \
            sum(sys.getsizeof(v) for v in self.__dict__.values())
    
    def clear_out(self):
        for fighter in self.fighters:
            self.mat.remove_token(fighter)
            del fighter
         
        del self.mat

    def log(self,entry=""):
        self.combatlog.append(entry)

    def log_del(self):
        self.combatlog.pop()

    def add_fighter(self, fighter):
        if fighter.name in self.fighternames:
            raise StandardError("Fighter named {} already fighting".format(fighter.name))

        fighter.set_ai(self.mat)
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
        fighter.set_tactic(tactic)

    def set_targeting(self, fighter, targeting):
        fighter.set_targeting(targeting)

    def clear_target(self, fighter):
        self.log("{} targets no one".format(fighter.name))
        fighter.target = None

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
        self.log("{} takes an AoO against {}".format(target.name,fighter.name))
        self.aoo_counts[target.name] = self.aoo_counts[target.name] + 1
        self.attack(target, fighter, False)

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
        if fighter == None:
            return False
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
            fighter.round_pass()
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
            # Run AI routine
            
            result = fighter.ai.act()
            
            self.combatlog += result[1]
            
            survive = True
            
            for action in result[0]:
                if action[0] == "end":
                    pass
                elif action[0] == "move":
                    survive = self.move_path(fighter, action[1])
                    if not survive:
                        break
                elif action[0] == "attack":
                    self.attack(fighter, fighter.target, action[1])
                elif action[0] == "satk":
                    self.satk(fighter, fighter.target, action[1])
                elif action[0] == "stand":
                    self.log("{} stands up".format(fighter.name))
                    fighter.drop_condition("Prone")
                    self.check_for_aoo(fighter, fighter.loc)
                    if self.check_death(fighter):
                        break        
                elif action[0] == "swap":
                    fighter.set_weapon(action[1])
                    self.log("{} switches weapons to {}".format(fighter.name,fighter.weap_name()))
                elif action[0] == "cond":
                    self.set_cond(fighter, fighter.target, action[1:])
                elif action[0] == "disarm":
                    self.disarm(fighter, fighter.target)
                elif action[0] == "trip":
                    self.trip(fighter, fighter.target)
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
        path = self.mat.partial_path(fighter, target, fighter.get_move())
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

    def attack(self, fighter, target, FRA=False, fob=False):
        if fighter.has("Prone") and "R" in fighter.weap_type() and "Crossbows" not in fighter.weap_group():
            self.log("{0} cannot attack; {0} is Prone".format(fighter.name))
            return False
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attacks {}: {}".format(fighter.name, target.name,fighter.print_all_atks(dist_to_target, FRA, target.type, target.subtype)))
        dmg = fighter.attack(target.get_AC(type=fighter.type, subtype=fighter.subtype), dist_to_target, FRA, fighter.type, fighter.subtype)

        self.log("{} takes {} damage".format(target.name, dmg[0]))
        self.log("  ({})".format(fighter.print_atk_dmg(dmg[1])))
        target.take_damage(dmg[0])
        self.log("{} at {}".format(target.name, target.print_hp()))

    def satk(self, fighter, target, satk_type):
        if satk_type in ["fob"]:
            if fighter.has("Prone") and "R" in fighter.weap_type() and "Crossbows" not in fighter.weap_group():
                self.log("{0} cannot attack; {0} is Prone".format(fighter.name))
                return False
                
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        
        if satk_type == "fob":
            self.log("{} attacks {}: {}".format(fighter.name, target.name,fighter.print_atk_line(dist=dist_to_target, fob=True)))
            
            dmg = fighter.attack(target.get_AC(type=fighter.type, subtype=fighter.subtype), dist_to_target, True, fighter.type, fighter.subtype, fob=True)

            self.log("{} takes {} damage".format(target.name, dmg[0]))
            self.log("  ({})".format(fighter.print_atk_dmg(dmg[1])))
            target.take_damage(dmg[0])
            self.log("{} at {}".format(target.name, target.print_hp()))
    
    def set_cond(self, fighter, target, cond_info):
        
        cond_type,save_type,DC_type,rds = cond_info
        rds = int(rds)
    
        self.log("{} is attempting to apply {} to {}".format(fighter.name, cond_type, target.name))
        
        save_type = save_type[0]
        
        save_type_long = {"F":"fortitude","R":"reflex","W":"will"}[save_type]
        
        if DC_type == "str":
            DC_stat_bon = fighter.stat_bonus(fighter.strtot())
        elif DC_type == "dex":
            DC_stat_bon = fighter.stat_bonus(fighter.dextot())
        elif DC_type == "con":
            DC_stat_bon = fighter.stat_bonus(fighter.contot())
        elif DC_type == "int":
            DC_stat_bon = fighter.stat_bonus(fighter.inttot())
        elif DC_type == "wis":
            DC_stat_bon = fighter.stat_bonus(fighter.wistot())
        elif DC_type == "cha":
            DC_stat_bon = fighter.stat_bonus(fighter.chatot())
        
        DC = 10 + (fighter.level // 2) + DC_stat_bon
        
        self.log("{} is making a {} save against DC {}".format(target.name, save_type_long, DC))
        
        cond_check = target.check_save(save_type,DC)
        
        if not cond_check[0]:
            self.log("{} failed their save ({})".format(target.name,cond_check[1]))
            self.log("{} now has the {} condition".format(target.name, cond_type))
            target.set_condition(cond_type,rds)
        else:
            self.log("{} passed their save ({})".format(target.name,cond_check[1]))
    
    def maneuver_check(self, fighter, target, dist, man):
        CMD = target.CMD(fighter.type, fighter.subtype, target.has("Flat-Footed"), man)
        result = fighter.check_CMB(CMD, dist, target.type, target.subtype, man)
        
        return result
    
    def disarm(self, fighter, target):
        dist_to_target = self.mat.dist_ft(fighter.loc, target.loc)
        self.log("{} attempts to disarm {}".format(fighter.name, target.name))
        if self.can_attempt_aoo(target):
            self.take_aoo(fighter, target)
        if not self.check_death(fighter):
            result = self.maneuver_check(fighter, target, dist_to_target, "Disarm")
            if result[0]:
                self.log("{} succeeds".format(fighter.name))
                item = target.drop("wield,0")
                self.log("{} drops {}".format(target.name, item.fullname()))
                if result[1] >= 10:
                    item = target.drop("wield,1")
                    if item:
                        self.log("{} drops {}".format(target.name, item.fullname()))
            else:
                self.log("{} fails to disarm".format(fighter.name))
                if result[1] <= -10:
                    item = fighter.drop("wield,0")
                    if item:
                        self.log("{} drops {}".format(fighter.name, item.fullname()))
            return True    
        else:
            return False
        
    def trip(self, fighter, target):
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
            else:
                self.log("{} fails to disarm".format(fighter.name))
                if result[1] <= -10 and self.can_trip(fighter):
                    self.log("{} is tripped".format(fighter.name))
                    fighter.set_condition("Prone")                    
            return True    
        else:
            return False  

###################################################################
#
# Output functions

    def output_init(self):
        output = ""
        for fighter in self.init_order:
            output = output + "{} ({:+d}): {}\n".format(fighter[0].name,fighter[0].get_init(),fighter[1])

        return output

    def output_log(self):
        return '\n'.join(self.combatlog)