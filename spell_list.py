import spell

burning_hands = spell.Spell(name="burning hands", level="m1s1w1", school="ev", desc="f", comp="VS", spl_range="15",
                            aim=["a", "CB"], effect="damage Ld4,5,R2,f")
magic_missile = spell.Spell(name="magic missile", level="m1s1w1", school="ev", desc="o", comp="VS", spl_range="medium",
                            aim=["t", "R1,9,2"], effect="damage 1d4+1,,N,o")

mage_armor = spell.Spell(name="mage armor", level="s1u1w1", school="co", subschool=["creation"], desc="o", comp="VSF",
                         spl_range="0", aim=["t", "1"], effect="buff armor,armor,4,W0h", dur="hLD")

###############################

bleed = spell.Spell(name="bleed", level="c0i0o0s0w0", school="ne", comp="VS", spl_range="close", aim=["t", "1"],
                    effect="debuff cond,Stable,end,W0")

detect_magic = spell.Spell(name="detect magic", level="b0c0d0i0m0o0s0u0w0", school="di", comp="VS", spl_range="60",
                           aim=["a", "CE"], effect="other", dur="mLCD")

resistance = spell.Spell(name="resistance", level="b0c0d0i0o0p1s0u0w0", school="ab", comp="VSMDF", spl_range="0",
                         aim=["t", "1"], effect="buff save,resistance,1,W0h", dur="m1")
