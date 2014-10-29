import battlemat
import character
import combat
import equip

jaya = character.Character(charClass="Bard", level=10, str=11, dex=18, con=14, int=13, wis=10, cha=16, feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot", "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1,2], hp=67, AC=19)

jayawep = equip.Weapon(name="shortbow", group=["Bows"], atk_damage=[1,6], atk_type="R", crit_mult=3, range=60)

jaya.add_weapon(jayawep, active=True)

jayaarm = equip.Armor(name="studded leather", type="Light", armor_bon=3, max_dex=5, armor_check=-1)

jaya.add_armor(jayaarm, active=True)

jayashld = equip.Armor(name="buckler", type="Shield", shield_bon=1, armor_check=-1)

jaya.add_shield(jayashld, active=True)

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[14,14], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

monsterwep = equip.Weapon(name="guisarme", group=["Polearms"], atk_damage=[2,4], atk_type="2", crit_range=20, crit_mult=3, weap_bon=1, range=5)

monster.add_weapon(monsterwep, active=True)

monsterarm = equip.Armor(name="+1 full plate", type="Heavy", armor_bon=10, max_dex=1, armor_check=-6)

monster.add_armor(monsterarm, active=True)

print "{}: {}".format(jaya.name,jaya.print_atk_line())
print "{}: {}".format(monster.name,monster.print_atk_line())
print ""
print "{}: AC {} ({})".format(jaya.name,jaya.get_AC(),jaya.print_AC_bons())
print "{}: AC {} ({})".format(monster.name,monster.get_AC(),monster.print_AC_bons())
print ""

mat = battlemat.Battlemat()
mat.add_token(jaya)
mat.add_token(monster)

fight = combat.Combat()
fight.add_fighter(jaya)
fight.add_fighter(monster)
fight.set_mat(mat)
fight.set_init()

while not fight.check_combat_end() and fight.round < 50:
    fight.combat_round()

print fight.output_log()