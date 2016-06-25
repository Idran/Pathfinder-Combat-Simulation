import battlemat
import character
import combat
import equip
import items
import spell_list as spells
import sys
import traceback
import time

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

test_ftr1 = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=10, side=1)

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

test_ftr1_2h = character.Character(charClass="Fighter", level=1, str=17, dex=15, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness", "Two-Weapon Fighting"], name="Corwyn Klas (2h)", loc=[1,2], hp=10, side=1)

test_ftr1_2h.add_weapon(items.longsword.copy(), active=True)

ci_dagger = items.dagger.copy()
ci_dagger.set_mat("cold iron")
test_ftr1_2h.add_weapon(ci_dagger, off=True)

hcb = items.crossbow_heavy.copy()
hcb.set_ammo(20)

test_ftr1_2h.add_weapon(hcb)

test_ftr1_2h.add_armor(items.breastplate.copy(), active=True)

##########################################################

test_barb1 = character.Character(charClass="Barbarian", level=1, str=17, dex=13, con=14, int=10, wis=12, cha=8, feat_list=["Cleave", "Power Attack"], name="Arjana", loc=[5,5], hp=12, fc=["h"], side=2)

test_barb1.add_weapon(items.greatsword.copy())
test_barb1.add_weapon(items.flail_heavy.copy(), active=True)
test_barb1.add_weapon(items.sling.copy())

test_barb1.add_armor(items.breastplate.copy(), active=True)

test_barb1.set_rage()

##########################################################

test_monk1 = character.Character(charClass="Monk", level=1, str=12, dex=16, con=10, int=13, wis=15, cha=8, feat_list=["Combat Reflexes", "Dodge", "Improved Unarmed Strike", "Stunning Fist", "Weapon Finesse"], name="Careful Initiate", loc=[4,5], hp=9, side=3)

test_monk1.add_weapon(items.kama.copy())
test_monk1.add_weapon(items.crossbow_light.copy())

shuriken = items.shuriken.copy()
shuriken.set_ammo(5)

test_monk1.add_weapon(items.shuriken)

##########################################################

test_wiz1 = character.Character(charClass="Wizard", level=1, str=10, dex=13, con=14, int=17, wis=12, cha=8, feat_list=["Alertness","Combat Casting","Improved Initiative","Scribe Scroll"], name="Holdreda Danton", loc=[7,9], hp=6, side=4)

test_wiz1.add_weapon(items.quarterstaff.copy(), active=True)

test_wiz1.add_spell_mem(spells.magic_missile.copy())
test_wiz1.add_spell_mem(spells.magic_missile.copy())
test_wiz1.add_spell_mem(spells.bleed.copy())
test_wiz1.add_spell_mem(spells.detect_magic.copy())
test_wiz1.add_spell_mem(spells.resistance.copy())

##########################################################

fighter1 = test_ftr1
fighter2 = test_wiz1

fighter1_count = 0
fighter1_hp = 0
fighter1_maxhp = fighter1.get_hp()
fighter1_round = 0
monster_count = 0
monster_hp = 0
monster_round = 0
fighter2_count = 0
fighter2_hp = 0
fighter2_maxhp = fighter2.get_hp()
fighter2_round = 0

num_combat = 10000

print("{}: {} {}".format(fighter1.name,fighter1.charClass,fighter1.level))
print("\t{}".format(fighter1.print_all_atks()))
print("\tAC {} ({})".format(fighter1.get_AC(),fighter1.print_AC_bons()))
print("")
print("{}: {} {}".format(fighter2.name,fighter2.charClass,fighter2.level))
print("\t{}".format(fighter2.print_all_atks()))
print("\tAC {} ({})".format(fighter2.get_AC(),fighter2.print_AC_bons()))

temp = time.clock()

for i in range(num_combat):
    fighter1.reset()
#    monster.reset()
    fighter2.reset()
    
    mat = battlemat.Battlemat()
    mat.add_token(fighter1)
    #mat.add_token(monster)
    mat.add_token(fighter2)

    fight = combat.Combat()
    fight.set_mat(mat)
    fight.add_fighter(fighter1)
    fight.add_fighter(fighter2)

    fight.set_tactic(fighter1,"Close")
    fight.set_tactic(fighter2,"Close")
    
    fight.set_init()

    while not fight.check_combat_end() and fight.round < 50:
        try:
            fight.combat_round()
        except:
            print("Unexpected error, dumping log")
            print("=====================================================================================")
            print(fight.output_log())
            print("=====================================================================================")
            print("Log dump complete")
            print("-----------------")
            print("Error details:")
            traceback.print_exc()
            sys.exit()

    if fighter1 in fight.fighters:
        fighter1_count = fighter1_count + 1
        fighter1_hp = fighter1_hp + fighter1.get_hp() - fighter1.damage
        fighter1_round = fighter1_round + fight.round - 1

#    if monster in fight.fighters:
#        monster_count = monster_count + 1
#        monster_hp = monster_hp + monster.get_hp() - monster.damage
#        monster_round = monster_round + fight.round - 1

    if fighter2 in fight.fighters:
        fighter2_count = fighter2_count + 1
        fighter2_hp = fighter2_hp + fighter2.get_hp() - fighter2.damage
        fighter2_round = fighter2_round + fight.round - 1
        
#    if i % 100 == 0:
#        print("i: {}".format(i))
#        print("ftr1_2h refs: {}".format(sys.getrefcount(fighter1)))
#        print("barb1 refs: {}".format(sys.getrefcount(fighter2)))
#        print("mat refs: {}".format(sys.getrefcount(mat)))
#        print("fight refs: {}".format(sys.getrefcount(fight)))
#        print("fight size: {}".format(sys.getsizeof(fight)))
    
#    fight.clear_out()
    
#    del fight
#    del mat

time_elapsed = time.clock()

fighter1_hp = (fighter1_hp / fighter1_count) if fighter1_count > 0 else "N/A"
fighter1_round = (fighter1_round / fighter1_count) if fighter1_count > 0 else "N/A"

monster_hp = (monster_hp / monster_count) if monster_count > 0 else "N/A"
monster_round = (monster_round / monster_count) if monster_count > 0 else "N/A"

fighter2_hp = (fighter2_hp / fighter2_count) if fighter2_count > 0 else "N/A"
fighter2_round = (fighter2_round / fighter2_count) if fighter2_count > 0 else "N/A"

print("{} vs. {}, {} iterations:\n".format(fighter1.name, fighter2.name, num_combat))
print("{}: {:.2%}".format(fighter1.name,float(fighter1_count) / num_combat))
print("Average HP when victorious: {}/{}".format(int(fighter1_hp),fighter1_maxhp))
print("Average rounds before end: {}\n".format(int(fighter1_round)))
#print("{}: {:.2%}".format(monster.name,float(monster_count) / num_combat))
#print("Average HP when victorious: {}".format(monster_hp))
#print("Average rounds before end: {}\n".format(monster_round))
print("{}: {:.2%}".format(fighter2.name,float(fighter2_count) / num_combat))
print("Average HP when victorious: {}/{}".format(int(fighter2_hp),fighter2_maxhp))
print("Average rounds before end: {}\n".format(int(fighter2_round)))
#print("Sample combat log:\n")
#print(fight.output_log())
print
print("Time elapsed: {:.3f} seconds".format(time_elapsed))
print("Est. time per iteration: {:.3f} seconds".format(time_elapsed / num_combat))