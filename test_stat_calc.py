import equip
import character
import items

test_ftr1 = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=10, ambi=False)

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

test_barb1 = character.Character(charClass="Barbarian", level=1, str=17, dex=13, con=14, int=10, wis=12, cha=8, feat_list=["Cleave", "Power Attack"], name="Arjana", loc=[1,2], hp=12, ambi=False, fc=["h"])

test_barb1.add_weapon(items.greatsword.copy())
test_barb1.add_weapon(items.flail_heavy.copy(), active=True)
test_barb1.add_weapon(items.sling.copy())

test_barb1.add_armor(items.breastplate.copy(), active=True)

test_barb1.set_rage()

##########################################################

test_monk1 = character.Character(charClass="Monk", level=20, str=12, dex=16, con=10, int=13, wis=15, cha=8, feat_list=["Combat Reflexes", "Dodge", "Improved Unarmed Strike", "Stunning Fist", "Weapon Finesse"], name="Careful Initiate", loc=[4,5], hp=9, ambi=False)

test_monk1.add_weapon(items.kama.copy())
test_monk1.add_weapon(items.crossbow_light.copy())

shuriken = items.shuriken.copy()
shuriken.set_ammo(5)

test_monk1.add_weapon(items.shuriken)

##########################################################

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[10,10], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

guisarme = items.guisarme.copy()
guisarme.set_bon(1)

monster.add_weapon(guisarme, active=True)

monsterarm = items.full_plate.copy()
monsterarm.set_bon(1)

monster.add_armor(monsterarm, active=True)

print(test_monk1.print_stat_block())