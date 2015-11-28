import copy

class SpAtk:
    """Spell data structure"""

    def __init__(self, name="", range=0, aim=None, dur=0, sr=False, effect=None, uses=1, ref_rate="rd", ref_count=1):
        if aim == None:
            aim = ["t",0]
        
        self.name = name
        self.range = range
        self.aim = aim
        self.dur = dur
        self.sr = sr
        
        self.targ_num = 0
        
        self.set_uses(uses, ref_rate, ref_count)
        
        self.counter = 0        
        
        self.acts = []
        
        self.cond_list = []        
        self.dmg = False
        
        self.effect_parse(effect)
    
    def set_uses(self, uses=1, ref_rate="rd", ref_count=1):
        
        self.uses = uses
        self.consumed = 0
        if ref_rate == "rd":
            ref_rate = 1
        elif ref_rate == "min":
            ref_rate = 10
        elif ref_rate == "hr":
            ref_rate = 600
        elif ref_rate == "day":
            ref_rate = 14400
        
        self.refresh_ctr = ref_rate * ref_count

    #############################
    #
    # Parsing functions
        
    
    def targ_parse(self):
        return 0
    
    def effect_parse(self, effect):
        effect_list = effect.split(";")
        
        for eff in effect_list:
            type = eff.split(" ")
            if type[0] == "damage":
                damage = type[1].split(",")
                
                dice = damage[0].split("d")
                for c in enumerate(dice):
                    if c[1].isdigit():
                        dice[c[0]] = int(c[1])
                        
                damage[0] = dice
                if damage[1] == "":
                    damage[1] = 0
                else:
                    damage[1] = int(damage[1])
                
                temp = [type[0]]
                temp += damage
                self.acts.append(temp)
                self.dmg = True
            elif type[0] == "cond":
                cond_data = [type[0]] + type[1].split(",")
                
                self.acts.append(cond_data)
                self.cond_list.append(cond_data[1])
            elif type[0] == "attack":
                self.acts.append(type)
                self.dmg = True
            else:
                self.acts.append(type)
    
    def use(self):
        if self.consumed < self.uses:
            self.consumed += 1
            return True
        else:
            return False
    
    def round(self):
        self.counter += 1
        if self.counter >= self.refresh_ctr:
            self.counter = 0
            self.consumed = 0

    def copy(self):
        return copy.copy(self)
        