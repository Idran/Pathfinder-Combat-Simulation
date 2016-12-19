class AI:

    import sys
    import character

    def __init__(self, char, mat):
    
        self.char_perm = char
        self.char = self.char_perm.copy()
        self.node = "Ready"
        self.node_arg = ""
        self.mat = mat
        self.tactic = ["Attack"]
        self.motivation = "Neutral"
        self.target = "Closest"
        self.target_list = []
        self.mental_map = dict()
        
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
        
        if len(self.mental_map) != len(self.mat.tokens):
            self.build_map()
        
        while self.node != "Decided":
            temp = self.pick_action()
            #print("{}: {}".format(self.char.name,self.node))
            act += temp[0]
            log += temp[1]
        
        return [act,log]
    
    def build_map(self):
    
        for entity in self.mental_map:
            if entity.id not in self.mat.token_list:
                self.mental_map.remove(entity)
        
        for entity in self.mat.tokens:
            if entity.id not in self.mental_map.keys():
                model_stats = entity.presented_stats(self.char_perm.side)
                self.mental_map[entity.id] = self.character.Charmodel(**model_stats)
                
    def update(self):
        
        del self.char
        self.char = self.char_perm.copy()
    
        self.fighters = self.mat.tokens
        self.moves = 0
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
    
    def set_motivation(self, motivation):
    
        self.motivation = motivation
    
    def set_target(self, fighter1, fighter2, log=[]):
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
                    
        if self.tactic[0] in ["Spell"]:
            spell = self.node_arg
            
            if spell.dmg:
                range = spell.get_range(self.char)
                dist_to_target = self.mat.dist_ft(self.char.loc, self.char.target.loc)
                move = min(self.char.get_move(),dist_to_target - range)
                log.append("{}".format(move))
                pre_move = self.char.loc
                act = self.move_to_target(act,move)
                self.char.loc = self.loc
                
                log.append("{} will move from {} to {} before casting".format(self.char.name,pre_move,self.char.loc))
            
                if self.moves < 2:
                    self.node = "Selecting Spell"
                else:
                    self.node = "Decided"
                    act.append(["end"])
            
        self.node_arg = ""
        
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
                        if not self.range_check(satk):
                            continue
                        if not self.prereq_check(satk):
                            continue
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
        min_tr = 20000
        for tr in melee_weap_range:
            if tr[0] < min_tr:
                min_tr = tr[0]
        max_tr = -20000
        for tr in melee_weap_range:
            if tr[1] > max_tr:
                max_tr = tr[0]
        
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
            if not ranged or (dist_to_target - speed < max_tr):
                #print("{} is thinking about melee".format(self.char.name))
                if curr_weap != melee_weap:
                    act.append(["swap",melee_weap])
                    self.char.set_weapon(melee_weap)
                    swap = True
            else:
                #print("{} is thinking about ranged".format(self.char.name))
                if curr_weap != ranged:
                    act.append(["swap",ranged])
                    self.char.set_weapon(ranged)
                    swap = True
        
        elif self.tactic[0] in ["Maneuver"]:        
            if self.char.weap_name() == "unarmed strike" and curr_weap != melee:
                act.append["swap",melee_weap]
                self.char.set_weapon(melee_weap)
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
        
        # Generating spell list
        
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
            
        if len(spell_list) == 0:
            log.append("Out of usable spells; switching to Close tactic")
            self.set_tactic("Close")
            self.node = "Ready"
            return[[],log]
            
            #print("Start0")
            #for spell in spell_list:
            #    print("Spell: {}, Level: {}".format(spell.name,spell.lvl_parse()[self.char.charClass]))
            #    print("Avg dmg vs self: {}".format(spell.avg_damage(self.char,self.char)))
            #print("End0")
        
        # Checking spell target options
        
        avg_dmg_table = []
        spell_choice = []
        
        if self.tactic[1] in ["Damage"]:
            for spell in spell_list:
                avg_dmg = 0
                if spell.aim[0] == "t":
                    target_table = []
                    for i in range(0,spell.targ_parse(self.char)):
                        avg_dmg_table = self.single_target_dmg_spell_eval(spell,combatant_data["Enemy"])
                        
                        if not avg_dmg_table:
                            continue
                            
                        selection = avg_dmg_table[0]
                        target_table.append(selection[1])
                        avg_dmg += selection[2]
                        selection[1].temp_dmg_add(selection[2])
                        
                    for enemy in combatant_data["Enemy"]:
                        enemy.temp_dmg_reset()
                    log_line = "{} attempts to cast {} at target(s) {}".format(self.char.name,spell.name,list(map(lambda i:i.name,target_table)))
                    spell_choice.append([spell,avg_dmg,target_table[:],log_line])
                elif spell.aim[0] == "a" and spell.aim[1][1] not in ['S','Y']:
                    spell_area,desc = spell.get_area(self.char)
                    target_list = self.mat.get_spell_targets(spell_area,self.char)

                    avg_dmg_table = []                    
                    #print("=====")
                    corner = ["bottom-left","top-left","bottom-right","top-right"]
                    for j in range(0,4):
                        for i,area in enumerate(target_list[j]):
                            avg_dmg_tot = 0
                            #print("{}, {}: {}".format(j,i,list(map(lambda j:[j[0]+self.char.loc[0],j[1]+self.char.loc[1]], spell_area[i]))))
                            if not area:
                                #print("\tNo targets".format(j,i))
                                pass
                            else:
                                for target in area:
                                    #print("\t{}: {}".format(target.name,target.loc))
                                    avg_dmg = spell.avg_damage(self.char,target)
                                    #print("\t\tAvg dmg: {}".format(avg_dmg))
                                    if target.side == self.char.side:
                                        avg_dmg_tot -= 2 * avg_dmg
                                    else:
                                        avg_dmg_tot += avg_dmg
                            #print("\tTotal expected damage: {}".format(avg_dmg_tot))
                            avg_dmg_table.append([avg_dmg_tot, j, i])
                            #print("=====")
                    avg_dmg_table.sort(key=lambda i:i[0], reverse=True)
                    avg_dmg,j,i = avg_dmg_table[0]
                    log_line = "{} attempts to cast {} towards {} from {} corner, striking target(s) {}".format(self.char.name,spell.name,desc[i],corner[j],list(map(lambda i:i.name,target_list[j][i])))
                    spell_choice.append([spell,avg_dmg,target_list[j][i][:],log_line])
                   
            spell_choice.sort(key=lambda i:i[1], reverse=True)
            if spell_choice[0][2] and (spell_choice[0][1] > 0 or spell_choice[0][0].debuff):
                spell_info = [spell_choice[0][0],spell_choice[0][2],spell_choice[0][3]]
                spell_pick = True
            else:
                spell_info = [spell_choice[0][0],spell_choice[0][2],spell_choice[0][3]]
                spell_pick = False
        
        #for entry in spell_choice:
        #    print("[{},{},{},{}]".format(entry[0].name,entry[1],list(map(lambda i:i.name,entry[2])),entry[3]))
        
        if spell_pick:
            self.node = "Decided"
            act.append(["cast",spell_info[0],spell_info[1]])
            act.append(["end"])
            log.append(spell_info[2])
        elif spell_info[1]:
            log.append("Out of usable spells; switching to Close tactic")
            self.set_tactic("Close")
            self.node = "Ready"
            return[[],log]
        else:
            log.append("{} cannot cast a spell".format(self.char.name))
            if self.moves < 2:
                log.append("{} moving in range".format(self.char.name))
                self.node = "Targeting"
                self.node_arg = spell_info[0]
            else:
                log.append("{} cannot act".format(self.char.name))
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
                active_check = other.is_active()
                if not active_check[0]:
                    continue
                if other.side != self.char.side:
                    other_dist = self.mat.dist_tile(self.char.loc, other.loc)
                    if other_dist < target_dist:
                        target_dist = other_dist
                        pot_target = other

            if pot_target != None:
                log = self.set_target(self.char,pot_target,log)
                temp = self.set_target(self.char_perm,pot_target)
            else:
                log.append("{0} has no target; {0} does nothing".format(self.char.name))
                self.node = "Decided"
                act.append(["end"])
                return [act,log]

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
        elif self.tactic[0] in ["Spell"]:
            self.node = "Moving"
        return [act,log]

###################################################################
#
# Action functions

    #############################
    #
    # Movement functions
    
    def move_to_target(self, act, move=-1):
        
        if self.is_down() and self.safe_to_stand():
            act.append(["stand"])
            self.moves += 1
        else:
            if move == -1:
                move = self.char.get_move()
            path = self.mat.partial_path(self.char, self.char.target, move)
            act.append(["move",path])
            self.moves += 1
            self.loc = path[-1:][0]
        
        return act

    #############################
    #
    # Attack functions
    
    def can_trip(self, target):
        return target.type not in ["Ooze"] and target.legs > 0 and not target.has("Prone")

    def is_down(self):
        return self.char.has("Prone")
    
    def safe_to_stand(self):
        return (not self.mat.check_threat(self.char, self.loc) or ("R" in self.char.weap_type() and "Crossbows" not in self.char.weap_group()))

    #############################
    #
    # Magic functions
    
    def single_target_dmg_spell_eval(self,spell,enemy_list):
        avg_dmg_table = []
        
        range = spell.get_range(self.char)

        for enemy in enemy_list:
            #print("Checking target validity for {}".format(enemy.name))
            if not spell.is_valid_target(enemy):
                #print("\t{} not valid target".format(enemy.name))
                continue
            dist_to_target = self.mat.dist_ft(self.char.loc, enemy.loc)
            if dist_to_target > range:
                #print("\t{} out of range".format(enemy.name))
                continue
                
            #print("\t{} valid target".format(enemy.name))

            avg_dmg_table.append([spell,enemy,spell.avg_damage(self.char,enemy)])

        avg_dmg_table.sort(key=lambda i:i[1].get_hp_temp_perc())
        avg_dmg_table.sort(key=lambda i:i[2])
        
        return avg_dmg_table

    #############################
    #
    # Special Attack functions
    
    def prereq_check(self,satk):
        
        prereqs = satk.prereqs
        
        if not prereqs:
            return True
        
        for weap_name in prereqs["weap"]:
            if self.char.weap_name != weap_name:
                weap_data = self.char.owns_weapon(weap_name)
                if not weap_data[0]:
                    return False
        
        return True
                
    
    def range_check(self,satk):
        if satk.range == "M":
            return self.mat.threaten(self.char,self.char.target)
        
    def trigger(self, satk):
        act = []
        log = []
        
        used = satk.use()
        if not used:
            return [[],[]]
        
        log.append("{} is trying to use {} on {}".format(self.char.name,satk.name,self.char.target.name))
                
        prereqs = satk.prereqs
        weap_data = None
        
        if "weap" in prereqs:
            weap_name = prereqs["weap"][0]
            if self.char.weap_name() != weap_name:
                weap_data = self.char.owns_weapon(weap_name)[1]
                log.append("Swapping to {} to enable {}".format(weap_name,satk.name))
                act.append(["swap",weap_data])
                if self.char.weap_swap() == "move" or self.char.bab[0] == 0:
                    self.moves += 1
        
        if self.moves == 2:
            return[act,log]
        
        for action in satk.acts:
            if action[0] in ["cond","damage","if"]:
                act.append(action)
            elif action[0] == "attack":
                if self.moves == 0:
                    act.append(["attack",True])
                else:
                    act.append(["attack",False])        
        
        return [act,log]