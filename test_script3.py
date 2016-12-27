import battlemat
import character
import combat
import equip
import items
import time

jaya = character.Character(char_class="Bard", level=10, stg=11, dex=18, con=14, inl=13, wis=10, cha=16,
                           feat_list=["Improved Initiative", "Point-Blank Shot", "Precise Shot", "Bullseye Shot",
                                      "Rapid Shot", "Arcane Strike"], ambi=True, name="Jaya", loc=[1, 2], hp=67,
                           armor_class=19)

jaya.add_weapon(items.shortbow, active=True)

jaya.add_armor(items.studded_leather, active=True)

# jaya.add_shield(items.buckler, active=True)

monster = character.Character(char_class="Fighter", level=10, stg=18, dex=10, con=8, inl=14, wis=10, cha=12,
                              feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)",
                                         "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive",
                                         "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[14, 14],
                              hp=55, armor_class=23, side=2)

monster.set_fighter_weap_train(["Polearms", "Close"])

monster.add_weapon(items.guisarme, active=True)

monsterarm = equip.Armor(name="+1 full plate", weap_type="Heavy", armor_bon=10, max_dex=1, armor_check=-6)

monster.add_armor(monsterarm, active=True)

quinn = character.Character(char_class="Ranger", level=10, stg=12, dex=22, con=12, inl=10, wis=14, cha=15,
                            feat_list=["Precise Shot", "Weapon Finesse", "Deadly Aim", "Power Attack",
                                       "Combat Expertise", "Magical Tail", "Point-Blank Shot", "Rapid Shot",
                                       "Endurance", "Favored Defense (Undead)", "Manyshot", "Fox Shape", "Snap Shot",
                                       "Improved Snap Shot"], ambi=True, name="Quinn", loc=[10, 10], hp=75,
                            armor_class=20, side=2)

quinn.set_ranger_favored_enemy([["Undead", 6], ["Humanoid", 2, "human"], ["Aberration", 2]])

quinn.add_weapon(items.longbow.copy(), active=True)

quinnarm = equip.Armor(name="+2 undead-defiant darkleaf leather armor", weap_type="Light", armor_bon=4, max_dex=8,
                       armor_check=0)

quinn.add_armor(quinnarm, active=True)

##########################################################

test_ftr1 = character.Character(char_class="Fighter", level=1, stg=17, dex=14, con=12, inl=8, wis=13, cha=10,
                                feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1, 2],
                                hp=10, ambi=False, side=1)

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

test_ftr1_2h = character.Character(char_class="Fighter", level=1, stg=17, dex=15, con=12, inl=8, wis=13, cha=10,
                                   feat_list=["Iron Will", "Power Attack", "Toughness", "Two-Weapon Fighting"],
                                   name="Corwyn Klas (2h)", loc=[1, 2], hp=10, ambi=False, side=1)

test_ftr1_2h.add_weapon(items.longsword.copy(), active=True)

ci_dagger = items.dagger.copy()
ci_dagger.set_mat("cold iron")
test_ftr1_2h.add_weapon(ci_dagger, off=True)

hcb = items.crossbow_heavy.copy()
hcb.set_ammo(20)

test_ftr1_2h.add_weapon(hcb)

test_ftr1_2h.add_armor(items.breastplate.copy(), active=True)

##########################################################

test_barb1 = character.Character(char_class="Barbarian", level=1, stg=17, dex=13, con=14, inl=10, wis=12, cha=8,
                                 feat_list=["Cleave", "Power Attack"], name="Arjana", loc=[5, 5], hp=12, ambi=False,
                                 fc=["h"], side=2)

test_barb1.add_weapon(items.greatsword.copy())
test_barb1.add_weapon(items.flail_heavy.copy(), active=True)
test_barb1.add_weapon(items.sling.copy())

test_barb1.add_armor(items.breastplate.copy(), active=True)

test_barb1.set_rage()

##########################################################

training_dummy = character.Character(char_class="Fighter", level=1, stg=10, dex=10, con=10, inl=10, wis=10, cha=10,
                                     feat_list=[], name="Training Dummy", loc=[1, 3], hp=100000, side=2)

##########################################################

print("{}: {}".format(test_ftr1_2h.name, test_ftr1_2h.print_all_atks()))
# print("{}: {}".format(monster.name,monster.print_atk_line()))
print("{}: {}".format(training_dummy.name, training_dummy.print_all_atks()))
print("")
print("{}: armor_class {} ({})".format(test_ftr1_2h.name, test_ftr1_2h.get_ac(), test_ftr1.print_ac_bons()))
# print("{}: armor_class {} ({})".format(monster.name,monster.get_AC(),monster.print_AC_bons()))
print("{}: armor_class {} ({})".format(training_dummy.name, training_dummy.get_ac(), training_dummy.print_ac_bons()))
print("")

temp = time.clock()
stat = "Str"
stat_track = []
for i in range(20):

    test_ftr1_2h.reset()
    #    monster.reset()
    # test_barb1.reset()
    training_dummy.reset()

    mat = battlemat.Battlemat()
    mat.add_token(test_ftr1_2h)
    # mat.add_token(monster)
    # mat.add_token(test_barb1)
    mat.add_token(training_dummy)

    fight = combat.Combat()
    fight.set_mat(mat)
    fight.add_fighter(test_ftr1_2h)
    # fight.add_fighter(test_barb1)
    fight.add_fighter(training_dummy)

    fight.set_tactic(test_ftr1_2h, "Attack")
    fight.set_tactic(test_barb1, "Close")
    fight.set_tactic(training_dummy, "Nothing")

    fight.set_init()

    while not fight.check_combat_end():
        fight.combat_round()

    test_round = fight.round - 1

    stat_track.append([test_ftr1_2h.strtot(), 100000 / test_round])

    test_ftr1_2h.stg += 1

# if i % 100 == 0:
#        print("i: {}".format(i))
#        print("ftr1_2h refs: {}".format(sys.getrefcount(test_ftr1_2h)))
#        print("barb1 refs: {}".format(sys.getrefcount(test_barb1)))
#        print("mat refs: {}".format(sys.getrefcount(mat)))
#        print("fight refs: {}".format(sys.getrefcount(fight)))
#        print("fight size: {}".format(sys.getsizeof(fight)))

#    fight.clear_out()

#    del fight
#    del mat

time_elapsed = time.clock()

print("{} vs. {}:\n".format(test_ftr1_2h.name, training_dummy.name))
print("Average damage per round as {} changes:".format(stat))
print()
for stats in stat_track:
    print("{}: {:.2f}".format(stats[0], stats[1]))
# print("Sample combat log:\n")
# print(fight.output_log())
print()
print("Time elapsed: {:.3f} seconds".format(time_elapsed))
