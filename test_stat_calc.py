import equip
import character
import items

test_char = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=14, ambi=False)

test_char.add_weapon(items.longsword.copy(), active=True)

ci_dagger = items.dagger.copy()
ci_dagger.set_mat("cold iron")
test_char.add_weapon(ci_dagger)

hcb = items.crossbow_heavy.copy()
hcb.set_ammo(20)

test_char.add_weapon(hcb)

test_char.add_armor(items.breastplate.copy(), active=True)

test_char.add_shield(items.wooden_shield_heavy.copy(), active=True)

##########################################################

monster = character.Character(charClass="Fighter", level=10, str=18, dex=10, con=8, int=14, wis=10, cha=12, feat_list=["Combat Expertise", "Critical Focus", "Dodge", "Improved Critical (guisarme)", "Improved Trip", "Intimidating Prowess", "Leadership", "Persuasive", "Power Attack", "Run", "Toughness"], ambi=True, name="Warlord", loc=[10,10], hp=55, AC=23, side=2)

monster.set_fighter_weap_train(["Polearms","Close"])

guisarme = items.guisarme.copy()
guisarme.set_bon(1)

monster.add_weapon(guisarme, active=True)

monsterarm = items.full_plate.copy()
monsterarm.set_bon(1)

monster.add_armor(monsterarm, active=True)

print test_char.print_stat_block()