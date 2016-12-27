import equip

dagger = equip.Weapon(name="dagger", weap_type="Simple", group=["Blades, Light", "Thrown"], atk_damage=[1, 4], atk_type="ML",
                      crit_range=19, spb="SP")

dagger_thrown = equip.Weapon(name="dagger", weap_type="Simple", group=["Blades, Light", "Thrown"], atk_damage=[1, 4],
                             atk_type="RT", crit_range=19, weap_range=10, spb="SP", ammo=1)

crossbow_heavy = equip.Weapon(name="heavy crossbow", weap_type="Simple", group=["Crossbows"], atk_damage=[1, 10],
                              atk_type="R", crit_range=19, weap_range=120, spb="P", ammo=10)

crossbow_light = equip.Weapon(name="light crossbow", weap_type="Simple", group=["Crossbows"], atk_damage=[1, 8],
                              atk_type="R", crit_range=19, weap_range=80, spb="P", ammo=10)

sling = equip.Weapon(name="sling", weap_type="Simple", group=["Thrown"], atk_damage=[1, 4], atk_type="RT", crit_range=20,
                     weap_range=50, spb="B", ammo=10)

quarterstaff = equip.Weapon(name="quarterstaff", weap_type="Simple", group=["Double", "Monk"], atk_damage=[1, 6],
                            atk_type="M", crit_range=20, spb="B", hands=2)

flail_heavy = equip.Weapon(name="heavy flail", weap_type="Martial", group=["Flails"], atk_damage=[1, 10], atk_type="M",
                           crit_range=19, spb="B", hands=2, disarm=True, trip=True)

greatsword = equip.Weapon(name="greatsword", weap_type="Martial", group=["Blades, Heavy"], atk_damage=[2, 6], atk_type="M",
                          crit_range=19, spb="S", hands=2)

guisarme = equip.Weapon(name="guisarme", weap_type="Martial", group=["Polearms"], atk_damage=[2, 4], atk_type="M",
                        crit_range=20, crit_mult=3, spb="S", hands=2)

longbow = equip.Weapon(name="longbow", weap_type="Martial", group=["Bows"], atk_damage=[1, 8], atk_type="R", crit_range=20,
                       crit_mult=3, weap_bon=1, weap_range=110, spb="P", ammo=20, hands=2)

longsword = equip.Weapon(name="longsword", weap_type="Martial", group=["Blades, Heavy"], atk_damage=[1, 8], atk_type="M",
                         crit_mult=2, crit_range=19, spb="S")

shortbow = equip.Weapon(name="shortbow", weap_type="Martial", group=["Bows"], atk_damage=[1, 6], atk_type="R", crit_mult=3,
                        weap_range=60, spb="P", ammo=20, hands=2)

kama = equip.Weapon(name="kama", weap_type="Exotic", group=["Monk"], atk_damage=[1, 6], atk_type="ML", crit_range=20,
                    spb="SP")

shuriken = equip.Weapon(name="shuriken", weap_type="Exotic", group=["Monk", "Thrown"], atk_damage=[1, 2], atk_type="RT",
                        crit_range=20, spb="P", ammo=1)

##############################################################

studded_leather = equip.Armor(name="studded leather", weap_type="Light", armor_bon=3, max_dex=5, armor_check=-1)

breastplate = equip.Armor(name="breastplate", weap_type="Medium", armor_bon=6, max_dex=3, asf=25, armor_check=-4)

full_plate = equip.Armor(name="full plate", weap_type="Heavy", armor_bon=9, max_dex=1, asf=35, armor_check=-6)

##############################################################

buckler = equip.Armor(name="buckler", weap_type="Shield", shield_bon=1, armor_check=-1)

wooden_shield_heavy = equip.Armor(name="heavy wooden shield", weap_type="Shield", shield_bon=2, armor_check=-2, hands=1)

##############################################################
