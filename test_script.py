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

test_monk1 = character.Character(charClass="Monk", level=1, str=12, dex=16, con=10, int=13, wis=15, cha=8, feat_list=["Combat Reflexes", "Dodge", "Improved Unarmed Strike", "Stunning Fist", "Weapon Finesse"], name="Careful Initiate", loc=[4,5], hp=9, ambi=False, side=3)

test_monk1.add_weapon(items.kama.copy())
test_monk1.add_weapon(items.crossbow_light.copy())

shuriken = items.shuriken.copy()
shuriken.set_ammo(5)

test_monk1.add_weapon(items.shuriken)

##########################################################

fighter1 = test_monk1
fighter2 = test_ftr1

print("{}:".format(test_ftr1_2h.name))
print(fighter1.print_AC_line())
print(fighter1.print_save_line())
print(fighter1.print_all_atks())
print("\n\n")
print("{}:".format(fighter2.name))
print(fighter2.print_AC_line())
print(fighter2.print_save_line())
print(fighter2.print_all_atks())
print("")

mat = battlemat.Battlemat()
fight = combat.Combat()

fight.set_mat(mat)

fight.add_fighter(fighter1)
fight.add_fighter(fighter2)

fight.set_tactic(fighter1,"Close")
fight.set_tactic(fighter2,"Close")

fight.set_init()

roundcount = 0

while not fight.check_combat_end() and roundcount < 50:
#    try:
        roundcount += 1
        fight.combat_round()
#    except:
#        print("Unexpected error: {}".format(sys.exc_info()))

print(fight.output_log())
print(fighter1.get_atk_bon(0, True, fighter2.type, fighter2.subtype))
print(fighter1.avg_weap_dmgs(fighter2))
print(fighter1.avg_weap_dmgs(fighter2,prn=True))
print(fighter1.best_dual_wield(fighter2,prn=True))
print(fighter1.best_melee_equip(fighter2,prn=True))
print(fighter1.best_melee_opt(fighter2,prn=True))
print(fighter1.weap_name(fighter1.best_melee_weap(fighter2)))
print(fighter1.weap_name(fighter1.best_ranged_weap(fighter2)))
print(fighter2.get_atk_bon(0, True, fighter1.type, fighter1.subtype))
print(fighter2.avg_weap_dmgs(fighter1))
print(fighter2.avg_weap_dmgs(fighter1,prn=True))
print(fighter2.best_melee_equip(fighter1,prn=True))
print(fighter2.best_melee_opt(fighter1,prn=True))
print(fighter2.weap_name(fighter2.best_melee_weap(fighter1)))
print(fighter2.weap_name(fighter2.best_ranged_weap(fighter1)))