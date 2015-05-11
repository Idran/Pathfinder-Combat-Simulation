class AI:

    import sys

    def __init__(self, char, mat):
    
        self.char = char
        self.node = "Ready"
        self.mat = mat
        self.tactic = ["Attack"]
        self.target = "Closest"
        
        self.update()
        
    def __sizeof__(self):
        return object.__sizeof__(self) + \
            sum(sys.getsizeof(v) for v in self.__dict__.values())
        
    
    def act(self):
        
        act = []
        log = []
        
        self.update()
        
        while self.node != "Decided":
            temp = self.pick_action()
            act += temp[0]
            log += temp[1]
        
        self.node = "Ready"
        
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
        elif self.node == "Swapping":
            return self.swapping()
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
    
    def swapping(self):
    
        act = []
        log = []
        
        ranged = self.char.best_ranged_weap(self.char.target)
        melee = self.char.best_melee_weap(self.char.target)
        curr_weap = self.char.curr_weap()
        swap = False
        
        if self.tactic[0] in ["Close"]:
            if not ranged or self.mat.threaten(self.char, self.char.target):
                if curr_weap != melee:
                    act.append(["swap",melee])
                    swap = True
            else:
                if curr_weap != ranged:
                    act.append(["swap",ranged])
                    swap = True
        
        elif self.tactic[0] in ["Maneuver"]:        
            if self.char.weap_name() == "unarmed strike" and curr_weap != melee:
                act.append["swap",melee]
                swap = True
            
        if self.mat.can_attack(self.char, self.char.target):
            if swap and self.char.weap_swap() == "move":
                self.moves += 1
            self.node = "Attacking"
        else:
            if swap and self.char.bab[0] == 0:
                self.moves += 1
            self.node = "Moving"
        
        return [act,log]
    
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
        elif self.tactic[0] in ["Close","Maneuver"]:
            self.node = "Swapping"
        
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
        
        