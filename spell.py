import copy

class Spell:
    """Spell data structure"""

    def __init__(self, name="", level=None, school=None, subschool=[], desc=[], cast_time="std", comp="V", range=0, aim=None, dur=0, sr=False, effect=None):
        if level == None:
            level = "s1w1"
        if school == None:
            school = "D"
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
        
        self.save = []
        
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
                
                self.dmg.append(damage)
                
                if damage[2] == "N":
                    self.save.append(None)
                else:
                    self.save.append(damage[2])
    
    def has_save(self):
        for i in self.save:
            if i != None:
                return True
        
        return False

    def copy(self):
        return copy.copy(self)
        