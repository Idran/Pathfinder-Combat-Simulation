import satk

stunning_fist = satk.SpAtk(name="stunning fist", range="M", aim=["t",1], effect="attack;if dmg;cond Stunned,F0,wis,2", uses=1, ref_rate="day", prereqs="weap,unarmed strike")