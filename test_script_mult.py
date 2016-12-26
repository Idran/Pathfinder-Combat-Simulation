import battlemat
import character
import combat
import equip
import items
import spell_list as spells
import sys
import traceback

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

test_wiz1.add_spell_mem(spells.burning_hands.copy())
test_wiz1.add_spell_mem(spells.magic_missile.copy())
test_wiz1.add_spell_mem(spells.bleed.copy())
test_wiz1.add_spell_mem(spells.detect_magic.copy())
test_wiz1.add_spell_mem(spells.resistance.copy())

##########################################################
fighter_list = [test_ftr1,test_monk1,test_wiz1,test_barb1]

for fighter in fighter_list:
    print("{} ({} {}):".format(fighter.name,fighter.charClass,fighter.level))
    print("\t{}".format(fighter.print_AC_line()))
    print("\t{}".format(fighter.print_save_line()))
    print("\t{}".format(fighter.print_all_atks()))
    print("\n")
print("")

mat = battlemat.Battlemat()
fight = combat.Combat()

fight.set_mat(mat)

for fighter in fighter_list:
    fight.add_fighter(fighter)

fight.set_tactic(test_ftr1,"Close")
fight.set_tactic(test_monk1,"Close")
fight.set_tactic(test_barb1,"Close")
fight.set_tactic(test_wiz1,"Spell,Damage")

fight.set_init()

roundcount = 0

while not fight.check_combat_end() and roundcount < 50:
    try:
        roundcount += 1
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
        print("Battlemat token list:")
        #for entity in mat.tokens:
        #    print("\t{}: id {}".format(entity.name,entity.id))
        #print("")
        #for id in mat.token_id_index:
        #    print("\t{}: name {}".format(id,mat.token_id_index[id].name))
        sys.exit()

print(fight.output_log())
for fighter in fighter_list:
    print("=====================================================================================")
    for id in fighter.ai.mental_model:
        print("{} Model: {}".format(fighter.name,id))
        print("\t{}".format(fighter.ai.mental_model[id].name))