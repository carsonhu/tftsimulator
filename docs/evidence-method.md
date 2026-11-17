# Collecting timing evidence from VODs

How to answer a worksheet's timing questions (Q2-Q12) from video, so measurements from different people and days
compare. Until Set 19 replays exist, VODs are the only direct evidence.

## Before measuring

1. **Know the build.** Note the VOD's date, and the patch if visible, and match it to a build in
   `builds/index.json`. PBE changes daily, so a VOD from another day may be another build. If the worksheet's
   predicted values changed between those builds (the "Changed since" section), say which build you assumed.
2. **Prefer 60 fps.** One game tick is 1/30 s = 2 frames at 60 fps, 1 frame at 30 fps. At 30 fps a single
   measurement is only good to about ±1 tick; average several.
3. **Pick clean situations.** The unit stationary (already in range), no attack speed or mana effects you can't
   account for, no stuns. Write down every item, trait and augment active on the unit; they change attack speed
   and mana.

## Events to mark

Mark the frame where each event *first* shows. The display has its own delay; measure differences between two
events of the same kind (attack start to attack start, cast start to cast start), so the delay cancels.

| Event | What to look for |
|---|---|
| Attack start | first frame of the attack animation |
| Hit (melee) / release (ranged) | damage number or HP-bar drop (melee); projectile leaves the unit (ranged) |
| Projectile hit | damage number or HP-bar drop on the target |
| Cast start | mana bar empties and the cast animation begins |
| Next attack start after a cast | first frame of the next attack animation |
| Mana gain resumes | first frame the mana bar rises again after a cast |

## What to measure for each question

| Question | Measurement |
|---|---|
| Q2 mana per attack / per second | Count attacks between two casts with no other mana sources; compare with max mana ÷ (mana per attack + mana per second × time). |
| Q3 first attack | Combat start (planning timer ends, units move) to the first hit/release, stationary units only. |
| Q4 windup at base AS | Attack start to hit/release, several attacks, itemless unit. |
| Q5 windup at other AS | The same at a known higher AS (e.g. a Rageblade unit late in combat) and, if possible, a slowed unit. |
| Q6 projectile | Release to hit, with the distance in hexes noted. |
| Q7 cast time | Cast start to the next attack start. |
| Q8 / Q10 AS scaling | Q7 / Q9 repeated at clearly different attack speeds; scaling shows as a shorter cast. |
| Q9 mana lock | Cast start to the first frame the mana bar rises again. |
| Q11 cast as attacks | An on-attack effect or attack counter visible in game (e.g. Rageblade stacks, an "every 3rd attack" passive) before and after a cast. |
| Q12 cast cancels attack | A cast that starts mid-windup: does that attack still land? |

## Recording

Add one row per measurement to the champion's evidence log:

`| date | build | VOD URL @ timestamp | fps | what | frames or values | result | Qn |`

Then update the question's status. A single clean measurement that matches the prediction to the tick is enough
to mark it **confirmed**; a mismatch marks it **refuted** and needs a second measurement plus a note on what
differs. If a measurement changes a global rule (G-ID in `docs/ASSUMPTIONS.md`), update the ledger too.
