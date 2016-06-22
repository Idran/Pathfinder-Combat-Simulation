class AI:

    import sys

    def __init__(self, char, mat):
    
        self.char = char
        self.node = "Ready"
        self.node_arg = ""
        self.mat = mat
        self.tactic = ["Attack"]
        self.target = "Closest"
        
        self.disable_list = ["Stunned","Paralyzed","Petrified","Unconscious"]
        
        self.update()
        
    def __sizeof__(self):
        return object.__sizeof__(self) + \
            sum(sys.getsizeof(v) for v in self.__dict__.values())
        
    
    def act(self):
        
        self.node = "Ready"        
        act = []
        log = []
        
        self.update()
        
        while self.node != "Decided":
            temp = self.pick_action()
            #print("{}: {}".format(self.char.name,self.node))
            act += temp[0]
            log += temp[1]
        
        return [act,log]
    
    def update(self):
    
        self.fighters = self.mat.tokens
        self.moves = 0
        self.fix_loc = self.char.loc
        self.loc = self.char.loc
    
    def pick_action(self):
    
        if self.node == "Ready":
            return self.ready()
        elif self.node == "Attacking":
            return self.attacking()
        elif self.node == "Moving":
            return self.moving()
        elif self.node == "Selecting Action":
            return self.selecting_act()
        elif self.node == "Selecting Attack":
            return self.selecting_atk()
        elif self.node == "Selecting Spell":
            return self.selecting_spl()
        elif self.node == "Special Attack":
            return self.satk()
        elif self.node == "Targeting":
            return self.targeting()
        else:
            pass

###################################################################
#
# Value-setting functions

    def set_tactic(self, tactic):
        
        self.tactic = tactic.split(',')
    
    def set_target(self, fighter1, fighter2, log):
        fighter1.target = fighter2
        log.append("{} targets {}".format(fighter1.name, fighter2.name))
        return log

###################################################################
#
# State functions
    
    def ready(self):
        
        if self.tactic[0] in ["Attack","Close","Maneuver"]:
            self.node = "Targeting"
            return [[],[]]
        if self.tactic[0] in ["Spell"]:
            self.node = "Selecting Spell"
            return [[],[]]
        if self.tactic[0] in ["Nothing"]:
            self.node = "Decided"
            return[["end"],[]]
    
    def attacking(self):
        
        act = []
        log = []
        
        if self.tactic[0] in ["Attack","Close","Maneuver"]:
            
            if self.moves == 0:
                act.append(["attack",True])
            else:
                act.append(["attack",False])
            
            self.node = "Decided"
            act.append(["end"])
        
        return [act,log]
    
    def maneuvering(self):
    
        act = []
        log = []
        
        if self.tactic[0] in ["Maneuver"]:

            if self.mat.can_attack(self.char, self.char.target):
                man_list = list(self.tactic[1])
                maneuver = False
                for man in man_list:
                    if man == "d" and self.char.target.has_weapon() and self.char.weap_disarm():
                        act.append(["disarm"])
                    elif man == "t" and self.can_trip(self.char.target) and self.char.weap_trip():
                        act.append(["trip"])
                
                if maneuver:
                    self.node = "Decided"
                    act.append(["end"])
                else:
                    self.node = "Attacking"
        
        return [act,log]
    
    def moving(self):
    
        act = []
        log = []
        
        if self.tactic[0] in ["Attack","Close","Maneuver"]:
            
            act = self.move_to_target(act)
            
            self.char.loc = self.loc
            if self.mat.can_attack(self.char, self.char.target):
                if self.tactic[0] in ["Attack","Close"]:
                    self.node = "Attacking"
                elif self.tactic[0] in ["Maneuver"]:
                    self.node = "Maneuvering"
            else:
                if self.moves < 2:
                    self.node = "Moving"
                else:
                    self.node = "Decided"
                    act.append(["end"])
            self.char.loc = self.fix_loc        
        
        return [act,log]
    
    def satk(self):
        
        act = []
        log = []
        
        if self.node_arg == "fob":
            if self.moves == 0:
                act.append(["satk","fob"])
            
            self.node = "Decided"
            act.append(["end"])
        
        self.node_arg = ""
            
        return [act,log]
    
    def selecting_act(self):
    
        act = []
        log = []
        
        if self.tactic[0] in ["Close"]:
            if self.char.get_hp_perc() <= 0.5:
                for satk in self.char.sa_list:
                    if set.intersection(set(satk.cond_list),set(self.disable_list)): #Checking for disabling special attacks
                        temp = self.trigger(satk)
                        if temp[0] or temp[1]:
                            act += temp[0]
                            log += temp[1]
                            self.node = "Decided"
                            act.append(["end"])
                            break
                else:
                    self.node = "Selecting Attack"
            else:
                self.node = "Selecting Attack"
        elif self.tactic[0] in ["Spell"]:
            self.node = "Selecting Spell"
        
        return[act,log]
    
    def selecting_atk(self):
    
        act = []
        log = []
        
        target = self.char.target
        dist_to_target = self.mat.dist_ft(self.char.loc, target.loc)
        speed = self.char.get_move()
        
        FRA = (self.moves == 0)
        
        ranged = self.char.best_ranged_weap(target, dist_to_target, FRA)
        
        melee_opts = self.char.best_melee_opt(target, dist_to_target, FRA)
        melee_type = melee_opts[0]
        melee_weap = melee_opts[1]
        melee_weap_range = self.char.threat_range(melee_weap)
        
        curr_weap = self.char.weap_list(no_array=True)
        if len(curr_weap) == 1:
            curr_weap = curr_weap[0]
            
        swap = False
        
        #print("{} current weapon: {}".format(self.char.name, curr_weap))
        #print("{} best melee: {}".format(self.char.name, melee_opts))
        #print("{} best ranged: {}".format(self.char.name, ranged))
        #print("{} tactic: {}".format(self.char.name, self.tactic))
        #print("{} threatens {}: {}".format(self.char.name,self.char.target.name,self.mat.threaten(self.char, self.char.target)))
        
        if self.tactic[0] in ["Close"]:
            #print ("{} is considering Close options".format(self.char.name))
            if not ranged or (dist_to_target - speed < melee_weap_range[1]):
                #print("{} is thinking about melee".format(self.char.name))
                if curr_weap != melee_weap:
                    act.append(["swap",melee_weap])
                    swap = True
            else:
                #print("{} is thinking about ranged".format(self.char.name))
                if curr_weap != ranged:
                    act.append(["swap",ranged])
                    swap = True
        
        elif self.tactic[0] in ["Maneuver"]:        
            if self.char.weap_name() == "unarmed strike" and curr_weap != melee:
                act.append["swap",melee_weap]
                swap = True
            
        if self.mat.can_attack(self.char, self.char.target):
            if swap and self.char.weap_swap() == "move":
                self.moves += 1
            if melee_type == "weap":
                self.node = "Attacking"
            elif melee_type == "fob":
                self.node = "Special Attack"
                self.node_arg = "fob"
            else:
                log.append("{0} does nothing".format(self.char.name))
                self.node = "Decided"
                act.append(["end"])
                
        else:
            if swap and self.char.bab[0] == 0:
                self.moves += 1
            self.node = "Moving"
        
        return [act,log]
    
    def selecting_spl(self):
    
        act = []
        log = []
        
        log.append("{} is selecting a spell".format(self.char.name))
        
        max_level = self.char.max_spell_lvl
        spell_data_list = []
        combatant_data = {"Ally":[],"Enemy":[]}
        
        for other in self.fighters:
            if other.side == self.char.side:
                side = "Ally"
            else:
                side = "Enemy"
            
            combatant_data[side].append(other)
        
        if self.tactic[1] in ["Damage"]:
            if len(combatant_data["Enemy"]) > 1:
                spell_list1 = self.char.spell_list("Damage","Multi")
                spell_list2 = self.char.spell_list("Damage","Single",-1,"Max")
                spell_list3 = self.char.spell_list("Debuff","Multi")
                spell_list4 = self.char.spell_list("Debuff","Single",-1,"Max")
                
                spell_list = spell_list1 + spell_list2 + spell_list3 + spell_list4
                
                spell_list = list(set(spell_list))
                
                spell_list.sort(key=lambda i: i.lvl_parse()[self.char.charClass], reverse=True)
                
            if len(combatant_data["Enemy"]) == 1 or len(spell_list) == 0:
                spell_list1 = self.char.spell_list("Damage")
                spell_list2 = self.char.spell_list("Debuff")
                
                spell_list = spell_list1 + spell_list2
                
                spell_list = list(set(spell_list))
                
                spell_list.sort(key=lambda i: i.lvl_parse()[self.char.charClass], reverse=True)
                
            
            print("Start0")
            for spell in spell_list:
                print("Spell: {}, Level: {}".format(spell.name,spell.lvl_parse()[self.char.charClass]))
                print("Avg dmg vs self: {}".format(spell.avg_damage(self.char,self.char)))
            print("End0")
            
        if len(spell_list) == 0:
            self.set_tactic("Retreat")
            log.append("Out of usable spells; retreating")
            self.node = "Ready"
            return[[],log]
            
        self.node = "Decided"
        act.append(["end"])
    
        return[act,log]
    
    def targeting(self):
    
        act = []
        log = []

        #############################
        #
        # Select target by targeting setting
    
        if self.target in ["Closest"]:
            log.append("{} targets closest enemy".format(self.char.name))
            target_dist = 20000
            pot_target = None

            for other in self.fighters:
                if other.side != self.char.side:
                    other_dist = self.mat.dist_tile(self.char.loc, other.loc)
                    if other_dist < target_dist:
                        target_dist = other_dist
                        pot_target = other

            if pot_target != None:
                log = self.set_target(self.char,pot_target,log)
            else:
                log.append("{0} has no target; {0} does nothing".format(self.char.name))
                self.node = "Decided"
                act.append(["end"])

        dist_to_target = self.mat.dist_ft(self.char.loc, self.char.target.loc)
        log.append("Distance from {} to {}: {} ft.".format(self.char.name, self.char.target.name, dist_to_target))

        #############################
        #
        # Select next node by tactic setting
            
        if self.tactic[0] in ["Attack"]:
            if self.mat.can_attack(self.char, self.char.target):
                self.node = "Attacking"
            else:
                self.node = "Moving"
        elif self.tactic[0] in ["Maneuver"]:
            self.node = "Selecting Attack"
        elif self.tactic[0] in ["Close"]:
            self.node = "Selecting Action"
        
        return [act,log]

###################################################################
#
# Action functions
    
    def can_trip(self, target):
        return target.type not in ["Ooze"] and target.legs > 0 and not target.has("Prone")
    
    def move_to_target(self, act):
        
        if self.is_down() and self.safe_to_stand():
            act.append(["stand"])
            self.moves += 1
        else:
            path = self.mat.partial_path(self.char, self.char.target, self.char.get_move())
            act.append(["move",path])
            self.moves += 1
            self.loc = path[-1:][0]
        
        return act

    def is_down(self):
        return self.char.has("Prone")
    
    def safe_to_stand(self):
        return (not self.mat.check_threat(self.char, self.loc) or ("R" in self.char.weap_type() and "Crossbows" not in self.char.weap_group()))
        
    def trigger(self, satk):
        act = []
        log = []
        
        used = satk.use()
        if not used:
            return [[],[]]
        
        log.append("{} is trying to use {} on {}".format(self.char.name,satk.name,self.char.target.name))
        
        for action in satk.acts:
            if action[0] in ["cond","damage"]:
                act.append(action)
            elif action[0] == "attack":
                if self.moves == 0:
                    act.append(["attack",True])
                else:
                    act.append(["attack",False])        
        
        return [act,log]