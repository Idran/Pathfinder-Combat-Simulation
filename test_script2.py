import battlemat
import character
import combat
import equip
import items

jaya = character.Character(charClass="Bard", level=10, str=11, dex=18, con=14, int=13, wis=10, cha=16, feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot", "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1,2], hp=67, AC=19)

jaya.add_weapon(items.shortbow, active=True)

jaya.add_armor(items.studded_leather, active=True)

jaya.add_shield(items.bucklet, active=True)

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

mat = battlemat.Battlemat()
mat.add_token(jaya)
#mat.add_token(monster)
mat.add_token(quinn)

jaya_count = 0
jaya_hp = 0
jaya_round = 0
monster_count = 0
monster_hp = 0
monster_round = 0
quinn_count = 0
quinn_hp = 0
quinn_round = 0

num_combat = 25000

print "{}: {}".format(jaya.name,jaya.print_atk_line())
#print "{}: {}".format(monster.name,monster.print_atk_line())
print "{}: {}".format(quinn.name,quinn.print_atk_line())
print ""
print "{}: AC {} ({})".format(jaya.name,jaya.get_AC(),jaya.print_AC_bons())
#print "{}: AC {} ({})".format(monster.name,monster.get_AC(),monster.print_AC_bons())
print "{}: AC {} ({})".format(quinn.name,quinn.get_AC(),quinn.print_AC_bons())
print ""

for i in range(num_combat):
    jaya.reset()
#    monster.reset()
    quinn.reset()

    fight = combat.Combat()
    fight.add_fighter(jaya)
    fight.add_fighter(quinn)
    fight.set_mat(mat)
    fight.set_init()

    while not fight.check_combat_end() and fight.round < 50:
       fight.combat_round()

    if jaya in fight.fighters:
        jaya_count = jaya_count + 1
        jaya_hp = jaya_hp + jaya.hp - jaya.damage
        jaya_round = jaya_round + fight.round

#    if monster in fight.fighters:
#        monster_count = monster_count + 1
#        monster_hp = monster_hp + monster.hp - monster.damage
#        monster_round = monster_round + fight.round

    if quinn in fight.fighters:
        quinn_count = quinn_count + 1
        quinn_hp = quinn_hp + quinn.hp - quinn.damage
        quinn_round = quinn_round + fight.round

jaya_hp = (jaya_hp / jaya_count) if jaya_count > 0 else "N/A"
jaya_round = (jaya_round / jaya_count) if jaya_count > 0 else "N/A"

monster_hp = (monster_hp / monster_count) if monster_count > 0 else "N/A"
monster_round = (monster_round / monster_count) if monster_count > 0 else "N/A"

quinn_hp = (quinn_hp / quinn_count) if quinn_count > 0 else "N/A"
quinn_round = (quinn_round / quinn_count) if quinn_count > 0 else "N/A"

print "{} vs. {}, {} iterations:\n".format(jaya.name, quinn.name, num_combat)
print "{}: {:.2%}".format(jaya.name,float(jaya_count) / num_combat)
print "Average HP when victorious: {}".format(jaya_hp)
print "Average rounds before end: {}\n".format(jaya_round)
#print "{}: {:.2%}".format(monster.name,float(monster_count) / num_combat)
#print "Average HP when victorious: {}".format(monster_hp)
#print "Average rounds before end: {}\n".format(monster_round)
print "{}: {:.2%}".format(quinn.name,float(quinn_count) / num_combat)
print "Average HP when victorious: {}".format(quinn_hp)
print "Average rounds before end: {}\n".format(quinn_round)
print "Sample combat log:\n"
print fight.output_log()