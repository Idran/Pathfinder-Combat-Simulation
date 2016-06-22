import copy

class Spell:
    """Spell data structure"""

    def __init__(self, name="", level=None, school=None, subschool=[], desc=[], cast_time="std", comp="V", range=0, aim=None, dur=0, sr=False, effect=None):
        if level == None:
            level = "s1w1"
        if school == None:
            school = "di"
        if aim == None:
            aim = ["t",0]
        
        self.name = name
        self.level = level
        self.school = school
        self.subschool = subschool
        self.cast_time = cast_time
        self.comp = comp
        self.range = range
        self.aim = aim
        self.dur = dur
        self.sr = sr
        
        self.targ_num = 0
        
        self.buff = []
        self.debuff = []
        self.dmg = []
        
        self.save = False
        
        self.effect_parse(effect)

    #############################
    #
    # Parsing functions
    
    def lvl_parse(self,level=None):
    
        if level == None:
            level = self.level
        
        lvl_int = {}
        temp_class = ""
        for c in level:
            if c.isalpha():
                temp_class = self.class_parse(c)
                continue
            lvl_int[temp_class] = int(c)
        
        return lvl_int
    
    def class_parse(self,cls):
    
        if cls == "b":
            return "Bard"
        if cls == "c":
            return "Cleric"
        if cls == "d":
            return "Druid"
        if cls == "i":
            return "Inquisitor"
        if cls == "m":
            return "Magus"
        if cls == "o":
            return "Oracle"
        if cls == "p":
            return "Paladin"
        if cls == "r":
            return "Ranger"
        if cls == "s":
            return "Sorcerer"
        if cls == "u":
            return "Summoner"
        if cls == "w":
            return "Wizard"
        
        return ""
    
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
                    else:
                        dice[c[0]] = c[1]
                        
                damage[0] = dice
                if damage[1] == "":
                    damage[1] = 0
                else:
                    damage[1] = int(damage[1])
                
                self.dmg.append(damage) #damage dice in index 0 (L=level variable), max dice in index 1, save in index 2, damage type in index 3
                
                save_data = damage[2]
                
                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True
            
            if type[0] == "buff":
                buff = type[1].split(",")
                
                self.buff.append(buff)
                
                save_data = buff[3]
                
                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True
            
            if type[0] == "debuff":
                debuff = type[1].split(",")
                
                save_data = debuff[3]
                
                if save_data != "N" and (len(save_data) == 2 or save_data[2] != "h"):
                    self.save = True

    #############################
    #
    # Spell data
    
    def is_single(self):
        if self.aim[0] == "t":
            return True
        else:
            return False
    
    def is_multi(self):
        return not self.is_single()
    
    def has_save(self):
    
        return self.save
    
    def is_valid_target(self,target):
        if self.aim[0] != "t":
            return True
        
        valid = False
        
        # Targeting restrictions
        
        # Effect-based restrictions
        
        for debuff in self.debuff:
            if debuff[1] == "cond":
                if debuff[3] == "end" and target.has(debuff[2]):
                    valid = True
                if debuff[3] != "end" and not target.has(debuff[2]):
                    valid = True
        
        return valid
    
    def get_DC(self,caster):
        level_list = self.lvl_parse()
        SL = level_list[caster.charClass]
        cast_bon = caster.stat_bonus(caster.casttot())
        
        return 10 + SL + cast_bon
    
    def avg_damage(self,caster,target):
        if not self.dmg:
            return 0
        
        CL = caster.CL()
        
        avg_dmg_tot = 0
        
        for damage in self.dmg:
            [dice,lvlmax,save,types] = damage
            
            if dice[0] == "L":
                if lvlmax == 0:
                    dice[0] = CL
                else:
                    dice[0] = min(CL,lvlmax)
            
            avg_dmg = (dice[0] + (dice[0]*dice[1])) / 2
                
            for l in types:
                pass
            
            if save != "N":
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

                if save != "N" and (len(save) == 2 or save[2] != "h"):
                    save_bon = self.get_save_bon(save,target)

                goal_score = self.get_DC(caster) - save_bon

                chance_pass = max(min((20 - goal_score + 1) / 20,0.95),0.05)

                avg_dmg = (avg_dmg_pass * chance_pass) + (avg_dmg_fail * (1-chance_pass))
            
                #print("Average damage on pass: {}".format(avg_dmg_pass))
                #print("Average damage on fail: {}".format(avg_dmg_fail))
                #print("DC: {}".format(self.get_DC(caster)))
                #print("Target save bon: {}".format(save_bon))
                #print("Goal score: {}".format(goal_score))
                #print("Chance to pass: {}".format(chance_pass))
                
            #print("Average damage: {}".format(avg_dmg))
            
            avg_dmg_tot += avg_dmg
            
        return avg_dmg_tot
            
            
    #############################
    #
    # Utility functions
    
    def get_save_bon(self,save,target):
        if save[0] == "F":
            save_bon = target.get_fort()
        if save[0] == "R":
            save_bon = target.get_ref()
        if save[0] == "W":
            save_bon = target.get_will()
        
        return save_bon
        

    def copy(self):
        return copy.copy(self)
        