import battlemat
import character
import combat
import equip
import items
import sys

jaya = character.Character(charClass="Bard", level=10, str=11, dex=18, con=14, int=13, wis=10, cha=16, feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot", "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1,2], hp=67, AC=19)

jaya.add_weapon(items.shortbow.copy(), active=True)
jaya.add_weapon(items.guisarme.copy())

jaya.add_armor(items.studded_leather.copy(), active=True)

#jaya.add_shield(items.buckler.copy(), active=True)

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[10,10], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

guisarme = items.guisarme.copy()
guisarme.set_bon(1)

monster.add_weapon(guisarme, active=True)

monsterarm = items.full_plate.copy()
monsterarm.set_bon(1)

monster.add_armor(monsterarm, active=True)

quinn = character.Character(charClass="Ranger", level=10, str=12, dex=22, con=12, int=10, wis=14, cha=15, feat_list=["Precise Shot", "Weapon Finesse", "Deadly Aim", "Power Attack", "Combat Expertise", "Magical Tail", "Point-Blank Shot", "Rapid Shot", "Endurance", "Favored Defense (Undead)", "Manyshot", "Fox Shape", "Snap Shot", "Improved Snap Shot"], ambi=True, name="Quinn", loc=[10,10], hp=75, AC=20, side=2)

quinn.set_ranger_favored_enemy([["Undead",6], ["Humanoid",2,"human"], ["Aberration",2]])

quinn.add_weapon(items.longbow.copy(), active=True)

quinnarm = equip.Armor(name="+2 undead-defiant darkleaf leather armor", type="Light", armor_bon=4, max_dex=8, armor_check=0)

quinn.add_armor(quinnarm, active=True)

##########################################################

test_ftr1 = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=10, ambi=False, side=1)

test_ftr1.add_weapon(items.longsword.copy(), active=True)

ci_dagger = items.dagger.copy()
ci_dagger.set_mat("cold iron")
test_ftr1.add_weapon(ci_dagger)

hcb = items.crossbow_heavy.copy()
hcb.set_ammo(20)

test_ftr1.add_weapon(hcb)

test_ftr1.add_armor(items.breastplate.copy(), active=True)

test_ftr1.add_shield(items.wooden_shield_heavy.copy(), active=True)

##########################################################

test_ftr1_2h = character.Character(charClass="Fighter", level=1, str=17, dex=15, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness", "Two-Weapon Fighting"], name="Corwyn Klas (2h)", loc=[1,2], hp=10, ambi=False, side=1)

test_ftr1_2h.add_weapon(items.longsword.copy(), active=True)

ci_dagger = items.dagger.copy()
ci_dagger.set_mat("cold iron")
test_ftr1_2h.add_weapon(ci_dagger, off=True)

hcb = items.crossbow_heavy.copy()
hcb.set_ammo(20)

test_ftr1_2h.add_weapon(hcb)

test_ftr1_2h.add_armor(items.breastplate.copy(), active=True)

##########################################################

test_barb1 = character.Character(charClass="Barbarian", level=1, str=17, dex=13, con=14, int=10, wis=12, cha=8, feat_list=["Cleave", "Power Attack"], name="Arjana", loc=[5,5], hp=12, ambi=False, fc=["h"], side=2)

test_barb1.add_weapon(items.greatsword.copy())
test_barb1.add_weapon(items.flail_heavy.copy(), active=True)
test_barb1.add_weapon(items.sling.copy())

test_barb1.add_armor(items.breastplate.copy(), active=True)

test_barb1.set_rage()

##########################################################

print "{}:".format(test_ftr1_2h.name)
print test_ftr1_2h.print_AC_line()
print test_ftr1_2h.print_save_line()
print test_ftr1_2h.print_all_atks()
print "\n\n"
print "{}:".format(test_barb1.name)
print test_barb1.print_AC_line()
print test_barb1.print_save_line()
print test_barb1.print_all_atks()
print ""

mat = battlemat.Battlemat()
fight = combat.Combat()

fight.set_mat(mat)

fight.add_fighter(test_ftr1_2h)
fight.add_fighter(test_barb1)

fight.set_tactic(test_ftr1_2h,"Attack")
fight.set_tactic(test_barb1,"Close")

fight.set_init()

roundcount = 0

while not fight.check_combat_end() and roundcount < 50:
#    try:
        roundcount += 1
        fight.combat_round()
#    except:
#        print "Unexpected error: {}".format(sys.exc_info())

print fight.output_log()
print test_ftr1_2h.get_atk_bon(0, True, test_barb1.type, test_barb1.subtype)
print test_ftr1_2h.avg_weap_dmgs(test_barb1)
print test_ftr1_2h.avg_weap_dmgs(test_barb1,prn=True)
print test_ftr1_2h.weap_name(test_ftr1_2h.best_melee_weap(test_barb1))
print test_ftr1_2h.weap_name(test_ftr1_2h.best_ranged_weap(test_barb1))
print test_barb1.get_atk_bon(0, True, test_ftr1_2h.type, test_ftr1_2h.subtype)
print test_barb1.avg_weap_dmgs(test_ftr1_2h)
print test_barb1.avg_weap_dmgs(test_ftr1_2h,prn=True)
print test_barb1.weap_name(test_barb1.best_melee_weap(test_ftr1_2h))
print test_barb1.weap_name(test_barb1.best_ranged_weap(test_ftr1_2h))