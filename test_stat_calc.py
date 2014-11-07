import equip
import character
import items

test_char = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=14)

test_char.add_weapon(items.longsword, active=True)

test_char.add_armor(items.breastplate, active=True)

test_char.add_shield(items.wooden_shield_heavy, active=True)

print test_char.print_stat_block()