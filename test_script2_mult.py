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

test_monk1 = character.Character(charClass="Monk", level=1, str=12, dex=16, con=10, int=13, wis=15, cha=8, feat_list=["Combat Reflexes", "Dodge", "Improved Unarmed Strike", "Stunning Fist", "Weapon Finesse"], name="Careful Initiate", loc=[4,5], hp=9, side=1)

test_monk1.add_weapon(items.kama.copy())
test_monk1.add_weapon(items.crossbow_light.copy())

shuriken = items.shuriken.copy()
shuriken.set_ammo(5)

test_monk1.add_weapon(items.shuriken)

##########################################################

test_wiz1 = character.Character(charClass="Wizard", level=1, str=10, dex=13, con=14, int=17, wis=12, cha=8, feat_list=["Alertness","Combat Casting","Improved Initiative","Scribe Scroll"], name="Holdreda Danton", loc=[7,9], hp=6, side=2)

test_wiz1.add_weapon(items.quarterstaff.copy(), active=True)

test_wiz1.add_spell_mem(spells.magic_missile.copy())
test_wiz1.add_spell_mem(spells.magic_missile.copy())
test_wiz1.add_spell_mem(spells.bleed.copy())
test_wiz1.add_spell_mem(spells.detect_magic.copy())
test_wiz1.add_spell_mem(spells.resistance.copy())

##########################################################

fighter_list = [test_ftr1,test_monk1,test_wiz1,test_barb1]
fighter_data = dict()
fighter_side_data = dict()
fight_log_collection = dict()
shortest = [99,-1]
longest = [0,-1]

for fighter in fighter_list:
    fighter.save_state()
    #print("Freeze test: {}".format(fighter.start_spell_list_mem))
    fighter_data[fighter.id] = [0,0,fighter.get_hp(),0]
    if fighter.side not in fighter_side_data.keys():
        fighter_side_data[fighter.side] = [0,0]
    print("{} ({} {}):".format(fighter.name,fighter.charClass,fighter.level))
    print("\tSide {}".format(fighter.side))
    print("\t{}".format(fighter.print_AC_line()))
    print("\t{}".format(fighter.print_save_line()))
    print("\t{}".format(fighter.print_all_atks()))
    if fighter.CL() > 0:
        print("\tSpells:")
        for line in fighter.print_spell_line():
            print("\t\t{}".format(line))
    print("\n")
print("")

num_combat = 2500

temp = time.clock()

print("Running {} iterations:".format(num_combat))

for i in range(num_combat):
    for fighter in fighter_list:
        fighter.reset()
        #if i < 20:
        #    print("Freeze test 2, {}: ".format(fighter.name))
        #    print("\tCur: {}".format(fighter.spell_list_mem))
        #    print("\tSaved: {}".format(fighter.start_spell_list_mem))

    mat = battlemat.Battlemat()
    fight = combat.Combat()

    fight.set_mat(mat)
    
    mat = battlemat.Battlemat()
    for fighter in fighter_list:
        mat.add_token(fighter)

    fight = combat.Combat()
    fight.set_mat(mat)

    for fighter in fighter_list:
        try:
            fight.add_fighter(fighter)
        except:
            print("Unexpected initialization error in fighter {}".format(fighter.name))
            print("Dumping character log")
            print("=====================================================================================")
            print(fighter.print_stat_block())
            print("=====================================================================================")
            print("Dumping previous fight log")
            print("=====================================================================================")
            print(fight_log_collection[i-1])
            print("=====================================================================================")
            print("-----------------")
            print("Error details:")
            traceback.print_exc()
            sys.exit()

    fight.set_tactic(test_ftr1,"Close")
    fight.set_tactic(test_monk1,"Close")
    fight.set_tactic(test_barb1,"Close")
    fight.set_tactic(test_wiz1,"Spell,Damage")
    
    fight.set_init()

    while not fight.check_combat_end():
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
    
    winning_side = fight.winning_side()
    fighter_side_data[winning_side][0] += 1
    
    round_count = fight.round - 1
            
    for fighter in fighter_list:
        if fighter in fight.fighters:
            fighter_data[fighter.id][0] += 1
            fighter_data[fighter.id][1] += fighter.get_hp() - fighter.damage
            fighter_data[fighter.id][3] += round_count
            fighter_side_data[fighter.side][1] += 1
    
    if round_count < shortest[0]:
        shortest[0] = round_count
        shortest[1] = i
    if round_count > longest[0]:
        longest[0] = round_count
        longest[1] = i
    
    fight_log_collection[i] = fight.output_log()
        
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

print("Multi-side fight, {} iterations:\n".format(num_combat))

for side in fighter_side_data:
    [side_win_count,side_size] = fighter_side_data[side]
    
    print("Side {} victory: {:.2%}".format(side,float(side_win_count) / num_combat))

    for fighter in fighter_list:
        if fighter.side == side:
            [fighter_count,fighter_hp,fighter_maxhp,fighter_round] = fighter_data[fighter.id]
            
            fighter_hp = (fighter_hp / fighter_count) if fighter_count > 0 else "N/A"
            fighter_round = (fighter_round / fighter_count) if fighter_count > 0 else "N/A"
            
            print("\t{} survival: {:.2%}".format(fighter.name,float(fighter_count) / num_combat))
            if fighter_hp != "N/A":
                hp_output = "{}/{}".format(int(fighter_hp),fighter_maxhp)
            else:
                hp_output = "N/A"
            print("\tAverage HP when victorious: {}".format(hp_output))
            if fighter_round != "N/A":
                fighter_round = int(fighter_round)
            print("\tAverage rounds before end: {}\n".format(fighter_round))
    if side_win_count == 0:
        avg_surv_output = "N/A"
    else:
        avg_surv_output = "{:.1f}".format(float(side_size) / side_win_count)
    print("Average survivors on victory: {}\n".format(avg_surv_output))
    
print("Shortest combat log (Log {}, {} rounds):\n".format(shortest[1],shortest[0]))
print(fight_log_collection[shortest[1]])
print
print("Longest combat log (Log {}, {} rounds):\n".format(longest[1],longest[0]))
print(fight_log_collection[longest[1]])
print
print("Time elapsed: {:.3f} seconds".format(time_elapsed))
print("Est. time per iteration: {:.3f} seconds".format(time_elapsed / num_combat))