import battlemat
import character
import combat
import equip
import items

jaya = character.Character(charClass="Bard", level=10, str=11, dex=18, con=14, int=13, wis=10, cha=16, feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot", "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1,2], hp=67, AC=19)

jaya.add_weapon(items.shortbow.copy(), active=True)
jaya.add_weapon(items.guisarme.copy())

jaya.add_armor(items.studded_leather.copy(), active=True)

jaya.add_shield(items.buckler.copy(), active=True)

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[10,10], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

guisarme = items.guisarme.copy()
guisarme.set_bon(1)

monster.add_weapon(guisarme, active=True)

monsterarm = items.full_plate.copy()
monsterarm.set_bon(1)

monster.add_armor(monsterarm, active=True)

print "{}:".format(jaya.name)
print jaya.print_AC_line()
print jaya.print_save_line()
print jaya.print_atk_line()
print "\n\n"
print "{}:".format(monster.name)
print monster.print_AC_line()
print monster.print_save_line()
print monster.print_atk_line()
print ""

mat = battlemat.Battlemat()
fight = combat.Combat()

fight.set_mat(mat)

fight.add_fighter(jaya)
fight.add_fighter(monster)

fight.set_tactic(jaya,"Close")

fight.set_init()

while not fight.check_combat_end() and fight.round < 50:
    fight.combat_round()

print fight.output_log()