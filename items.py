import equip

dagger = equip.Weapon(name="dagger", type="Simple", group=["Blades, Light", "Thrown"], atk_damage=[1,4], atk_type="ML", crit_range=19, spb="SP")

dagger_thrown = equip.Weapon(name="dagger", type="Simple", group=["Blades, Light", "Thrown"], atk_damage=[1,4], atk_type="RT", crit_range=19, range=10, spb="SP", ammo=1)

crossbow_heavy = equip.Weapon(name="heavy crossbow", type="Simple", group=["Crossbows"], atk_damage=[1,10], atk_type="R", crit_range=19, range=120, spb="P", ammo=10)

sling = equip.Weapon(name="sling", type="Simple", group=["Thrown"], atk_damage=[1,4], atk_type="RT", crit_range=20, range=50, spb="B", ammo=10)

flail_heavy = equip.Weapon(name="heavy flail", type="Martial", group=["Flails"], atk_damage=[1,10], atk_type="M", crit_range=19, spb="B", hands=2, disarm=True, trip=True)

greatsword = equip.Weapon(name="greatsword", type="Martial", group=["Blades, Heavy"], atk_damage=[2,6], atk_type="M", crit_range=19, spb="S", hands=2)

guisarme = equip.Weapon(name="guisarme", type="Martial", group=["Polearms"], atk_damage=[2,4], atk_type="M", crit_range=20, crit_mult=3, spb="S", hands=2)

longbow = equip.Weapon(name="longbow", type="Martial", group=["Bows"], atk_damage=[1,8], atk_type="R", crit_range=20, crit_mult=3, weap_bon=1, range=110, spb="P", hands=2)

longsword = equip.Weapon(name="longsword", type="Martial", group=["Blades, Heavy"], atk_damage=[1,8], atk_type="M", crit_mult=2, crit_range=19, spb="S", ammo=20)

shortbow = equip.Weapon(name="shortbow", type="Martial", group=["Bows"], atk_damage=[1,6], atk_type="R", crit_mult=3, range=60, spb="P", ammo=20, hands=2)

##############################################################

studded_leather = equip.Armor(name="studded leather", type="Light", armor_bon=3, max_dex=5, armor_check=-1)

breastplate = equip.Armor(name="breastplate", type="Medium", armor_bon=6, max_dex=3, asf=25, armor_check=-4)

full_plate = equip.Armor(name="full plate", type="Heavy", armor_bon=9, max_dex=1, asf=35, armor_check=-6)

##############################################################

buckler = equip.Armor(name="buckler", type="Shield", shield_bon=1, armor_check=-1)

wooden_shield_heavy = equip.Armor(name="heavy wooden shield", type="Shield", shield_bon=2, armor_check=-2, hands=1)

##############################################################