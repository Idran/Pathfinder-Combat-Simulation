import equip
import character

longsword = equip.Weapon(name="longsword", group=["Blades, Heavy"], atk_damage=[1,8], atk_type="M", crit_mult=2, crit_range=19)

##############################################################

breastplate = equip.Armor(name="breastplate", type="Medium", armor_bon=6, max_dex=3, asf=25, armor_check=-4)

##############################################################

heavy_wooden_shield = equip.Armor(name="heavy wooden shield", type="Shield", shield_bon=2, armor_check=-2)

##############################################################

test_char = character.Character(charClass="Fighter", level=1, str=17, dex=14, con=12, int=8, wis=13, cha=10, feat_list=["Iron Will", "Power Attack", "Toughness"], name="Corwyn Klas", loc=[1,2], hp=14)

test_char.add_weapon(longsword, active=True)

test_char.add_armor(breastplate, active=True)

test_char.add_shield(heavy_wooden_shield, active=True)

print test_char.print_stat_block()