import copy


class SpAtk:
    """Spell data structure"""

    def __init__(self, name="", spatk_range=0, aim=None, dur=0, sr=False, effect=None, uses=1, ref_rate="rd", ref_count=1,
                 prereqs=None):
        if aim is None:
            aim = ["t", 0]

        self.name = name
        self.spatk_range = spatk_range
        self.aim = aim
        self.dur = dur
        self.sr = sr

        self.targ_num = 0

        self.uses = 0
        self.consumed = 0
        self.refresh_ctr = 0

        self.set_uses(uses, ref_rate, ref_count)

        self.counter = 0

        self.acts = []

        self.cond_list = []
        self.dmg = False

        self.effect_parse(effect)

        self.prereqs = {}
        self.prereq_parse(prereqs)

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

    # noinspection PyMethodMayBeStatic
    def targ_parse(self):
        return 0

    def prereq_parse(self, prereqs):
        prereq_list = prereqs.split(";")

        for pr in prereq_list:
            prereq = pr.split(",")

            if prereq[0] not in self.prereqs:
                self.prereqs[prereq[0]] = [prereq[1]]
            else:
                self.prereqs[prereq[0]].append(prereq[1])

    def effect_parse(self, effect):
        effect_list = effect.split(";")

        for eff in effect_list:
            spatk_type = eff.split(" ")
            if spatk_type[0] == "damage":
                damage = spatk_type[1].split(",")

                dice = damage[0].split("d")
                for c in enumerate(dice):
                    if c[1].isdigit():
                        dice[c[0]] = int(c[1])

                damage[0] = dice
                if damage[1] == "":
                    damage[1] = 0
                else:
                    damage[1] = int(damage[1])

                temp = [spatk_type[0]]
                temp += damage
                self.acts.append(temp)
                self.dmg = True
            elif spatk_type[0] == "cond":
                cond_data = [spatk_type[0]] + spatk_type[1].split(",")

                self.acts.append(cond_data)
                self.cond_list.append(cond_data[1])
            elif spatk_type[0] == "attack":
                self.acts.append(spatk_type)
                self.dmg = True
            else:
                self.acts.append(spatk_type)

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
