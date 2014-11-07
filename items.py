import equip

guisarme = equip.Weapon(name="guisarme", group=["Polearms"], atk_damage=[2,4], atk_type="2", crit_range=20, crit_mult=3, weap_bon=1)

longbow = equip.Weapon(name="longbow", group=["Bows"], atk_damage=[1,8], atk_type="R", crit_range=20, crit_mult=3, weap_bon=1, range=110)

longsword = equip.Weapon(name="longsword", group=["Blades, Heavy"], atk_damage=[1,8], atk_type="M", crit_mult=2, crit_range=19)

shortbow = equip.Weapon(name="shortbow", group=["Bows"], atk_damage=[1,6], atk_type="R", crit_mult=3, range=60)

##############################################################

studded_leather = equip.Armor(name="studded leather", type="Light", armor_bon=3, max_dex=5, armor_check=-1)

breastplate = equip.Armor(name="breastplate", type="Medium", armor_bon=6, max_dex=3, asf=25, armor_check=-4)

##############################################################

buckler = equip.Armor(name="buckler", type="Shield", shield_bon=1, armor_check=-1)

wooden_shield_heavy = equip.Armor(name="heavy wooden shield", type="Shield", shield_bon=2, armor_check=-2)

##############################################################