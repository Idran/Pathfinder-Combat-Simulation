import battlemat
import character
import combat
import equip
import items

jaya = character.Character(charClass="Bard", level=10, str=11, dex=18, con=14, int=13, wis=10, cha=16, feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot", "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1,2], hp=67, AC=19)

jaya.add_weapon(items.shortbow, active=True)

jaya.add_armor(items.studded_leather, active=True)

#jaya.add_shield(items.buckler, active=True)

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[14,14], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

monster.add_weapon(items.guisarme, active=True)

monsterarm = equip.Armor(name="+1 full plate", type="Heavy", armor_bon=10, max_dex=1, armor_check=-6)

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

mat = battlemat.Battlemat()
mat.add_token(test_ftr1_2h)
#mat.add_token(monster)
mat.add_token(test_barb1)

test_ftr1_count = 0
test_ftr1_hp = 0
test_ftr1_round = 0
monster_count = 0
monster_hp = 0
monster_round = 0
test_barb1_count = 0
test_barb1_hp = 0
test_barb1_round = 0

num_combat = 10000

print "{}: {}".format(test_ftr1_2h.name,test_ftr1_2h.print_all_atks())
#print "{}: {}".format(monster.name,monster.print_atk_line())
print "{}: {}".format(test_barb1.name,test_barb1.print_all_atks())
print ""
print "{}: AC {} ({})".format(test_ftr1_2h.name,test_ftr1_2h.get_AC(),test_ftr1.print_AC_bons())
#print "{}: AC {} ({})".format(monster.name,monster.get_AC(),monster.print_AC_bons())
print "{}: AC {} ({})".format(test_barb1.name,test_barb1.get_AC(),test_barb1.print_AC_bons())
print ""

for i in range(num_combat):
    test_ftr1_2h.reset()
#    monster.reset()
    test_barb1.reset()

    fight = combat.Combat()
    fight.set_mat(mat)
    fight.add_fighter(test_ftr1_2h)
    fight.add_fighter(test_barb1)
    fight.set_init()

    while not fight.check_combat_end() and fight.round < 50:
       fight.combat_round()

    if test_ftr1_2h in fight.fighters:
        test_ftr1_count = test_ftr1_count + 1
        test_ftr1_hp = test_ftr1_hp + test_ftr1_2h.get_hp() - test_ftr1_2h.damage
        test_ftr1_round = test_ftr1_round + fight.round - 1

#    if monster in fight.fighters:
#        monster_count = monster_count + 1
#        monster_hp = monster_hp + monster.get_hp() - monster.damage
#        monster_round = monster_round + fight.round - 1

    if test_barb1 in fight.fighters:
        test_barb1_count = test_barb1_count + 1
        test_barb1_hp = test_barb1_hp + test_barb1.get_hp() - test_barb1.damage
        test_barb1_round = test_barb1_round + fight.round - 1

test_ftr1_hp = (test_ftr1_hp / test_ftr1_count) if test_ftr1_count > 0 else "N/A"
test_ftr1_round = (test_ftr1_round / test_ftr1_count) if test_ftr1_count > 0 else "N/A"

monster_hp = (monster_hp / monster_count) if monster_count > 0 else "N/A"
monster_round = (monster_round / monster_count) if monster_count > 0 else "N/A"

test_barb1_hp = (test_barb1_hp / test_barb1_count) if test_barb1_count > 0 else "N/A"
test_barb1_round = (test_barb1_round / test_barb1_count) if test_barb1_count > 0 else "N/A"

print "{} vs. {}, {} iterations:\n".format(test_ftr1_2h.name, test_barb1.name, num_combat)
print "{}: {:.2%}".format(test_ftr1.name,float(test_ftr1_count) / num_combat)
print "Average HP when victorious: {}".format(test_ftr1_hp)
print "Average rounds before end: {}\n".format(test_ftr1_round)
#print "{}: {:.2%}".format(monster.name,float(monster_count) / num_combat)
#print "Average HP when victorious: {}".format(monster_hp)
#print "Average rounds before end: {}\n".format(monster_round)
print "{}: {:.2%}".format(test_barb1.name,float(test_barb1_count) / num_combat)
print "Average HP when victorious: {}".format(test_barb1_hp)
print "Average rounds before end: {}\n".format(test_barb1_round)
#print "Sample combat log:\n"
#print fight.output_log()