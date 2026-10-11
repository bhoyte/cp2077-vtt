# Night City Live — Ruleset Design Bible
### Cyberpunk RED Deep Dive vs. Our Homebrew System

> **Purpose:** This document maps every major Cyberpunk RED mechanic to its Night City Live homebrew equivalent. For each system, it explains what RED does, why we can't copy it verbatim, and how our version achieves the same dramatic purpose — often better suited to a live stream format. Use this as the design authority when building or expanding any game system.

---

## Part 1: The Core Resolution System

### Cyberpunk RED

Cyberpunk RED uses ten STATs as its attribute foundation: **INT** (Intelligence), **REF** (Reflexes), **DEX** (Dexterity), **TECH** (Technique), **COOL** (Cool), **WILL** (Willpower), **LUCK** (Luck), **BODY** (Body), **EMP** (Empathy), and **MOVE** (Movement).[cite:95] Each character also has Skills — over 60 of them — organized into categories like Awareness, Body, Control, Education, Fighting, Performance, Ranged Weapon, and Social.[cite:93] To resolve any action, a player rolls `1d10 + STAT + Skill Rank` vs. a Difficulty Value (DV). Skills start at a minimum of 2 for the "Basic Skills" that everyone knows.[cite:94]

This system is granular, but that granularity is a burden for a live audience watching a stream. A viewer can't parse the difference between "Handgun (REF)" and "Shoulder Arms (REF)" in real time, and a character sheet with 60+ skills is impossible to display meaningfully as an on-screen overlay.

### Night City Live Homebrew

Our system compresses the ten RED stats into six, each covering a broader thematic domain. The resolution core is identical in structure — `1d10 + STAT vs. Difficulty Number` — but the skill layer is absorbed into the stat itself. No separate skill ranks. No 60-item skill list. The audience can see all six stats on the HUD at once and understand them instantly.

```
Roll: 1d10 + Relevant STAT vs. Difficulty Number (DN)
Success:   Roll >= DN
Failure:   Roll < DN
Critical:  Natural 10 (success regardless of DN; triggers bonus narration)
Fumble:    Natural 1 (failure regardless of modifiers; triggers complication)
```

**The Six Stats and What They Cover:**

| Homebrew Stat | Maps to RED | Covers |
|---|---|---|
| **IRON** | REF | All ranged combat, firearms, suppressive fire |
| **BLADE** | DEX | Melee, brawling, martial arts, close quarters |
| **GHOST** | REF + DEX | Stealth, infiltration, evasion, acrobatics |
| **JACK** | INT + TECH | Hacking, electronics, netrunning, devices |
| **TALK** | COOL + EMP | Persuasion, deception, intimidation, social reads |
| **MEAT** | BODY + WILL | Endurance, HP bonus, physical feats, resistance, death saves |

**Difficulty Numbers (simplified from RED's DV table):**[cite:95]

| Task Tier | DN | Example |
|---|---|---|
| Easy | 8 | Shoot a stationary target at close range |
| Standard | 12 | Fast-talk a suspicious guard |
| Hard | 15 | Hack a corporate ICE mid-combat |
| Legendary | 18 | Outshoot a MaxTac solo |
| Impossible | 20 | Reserved for acts of genuine heroism — rarely called |

**Stat ranges:** 2–8 at character creation. Max 10 during a campaign. Points are distributed by the audience in Episode 0.

---

## Part 2: Hit Points, Wound States & Death

### Cyberpunk RED

RED tracks HP as a pool derived from BODY. Characters have three wound states:[cite:110][cite:113]

- **Healthy / Lightly Wounded** (HP > half max): No penalty
- **Seriously Wounded** (HP ≤ half max): -2 to all actions
- **Mortally Wounded** (HP ≤ 0): Must make a Death Save each turn. Roll `1d10 ≤ BODY` or die. The DC worsens by +1 each round untreated.[cite:110]

A single failed Death Save means instant death — no second chances.[cite:110] Critical Injuries (triggered when two or more damage dice show 6) add specific injuries from a table: broken ribs, collapsed lung, dismembered arm, internal bleeding, etc., each with mechanical effects like -2 to all actions or a mandatory Death Save.[cite:113][cite:119]

### Night City Live Homebrew

We keep the three-tier wound state structure because it's dramatically excellent and mechanically clean — but we adapt the math and add a fourth "Bleeding Out" state specifically for the stream's most dramatic moments.

**HP Formula:** `20 + (MEAT × 5)` 
*Example: MEAT 5 = 45 HP max. This gives a meaningful but not overwhelming HP pool.*

**Wound States:**

| State | Threshold | Effect |
|---|---|---|
| **Intact** | HP > 75% max | No penalty |
| **Banged Up** | HP 26–75% max | -1 to all rolls |
| **Seriously Wounded** | HP 1–25% max | -2 to all rolls; GM describes injury |
| **Bleeding Out** | HP = 0 | No actions; Death Counter starts |

**The Death Counter (adapted from RED's escalating Death Save):**

When Chat-V hits 0 HP, a visible countdown begins on the overlay — 3 rounds. Each round the AI narrates the situation worsening. If no Revival mechanic is triggered within 3 rounds, Chat-V dies. If a Revival fires, HP resets to 1 and the character is Seriously Wounded.

This is superior to RED's single Death Save roll for a stream because it gives the audience time to react — to hit the Trauma Team donation tier, to choose a last-ditch action. The tension is extended, not resolved in one dice roll. The audience experiences the countdown. That's television.

**Critical Injuries (homebrew adaptation of RED's system):**[cite:113][cite:119]

Triggered when the natural die roll is exactly 1 (a Fumble) on an attack, OR when an enemy rolls a natural 10 against Chat-V. Roll 1d6 on the Critical Injury table. Effects persist until treated in-city.

| d6 | Injury | Mechanical Effect | Narrative Hook |
|---|---|---|---|
| 1 | **Grazed Eye** | -2 to IRON rolls | "Your vision splits into red static" |
| 2 | **Cracked Ribs** | -1 to all physical rolls | "Every breath is a knife" |
| 3 | **Burned Hand** | BLADE and IRON at disadvantage (roll twice, take lower) | "Your grip betrays you" |
| 4 | **Concussion** | -2 to JACK and TALK | "The world keeps stuttering" |
| 5 | **Shrapnel Leg** | GHOST rolls at disadvantage | "You're leaving a blood trail" |
| 6 | **Gut Shot** | Lose 3 HP per episode round until treated | "Tick tock, preem. That's your blood on the floor" |

---

## Part 3: The Humanity / Cyberware System — The Full Redesign

This is the section omitted from the initial spec — and the most thematically important mechanic in the entire cyberpunk genre. Stripping it out entirely would have made the system "neutered," as noted. Here is the full design.

### Cyberpunk RED: How Humanity Works

In RED, **Empathy (EMP)** is one of the ten core stats. It starts at a value between 1–8 and directly drives **Humanity**, which is `EMP × 10`.[cite:96] Installing cyberware costs Humanity — each piece has a fixed HL (Humanity Loss) that is rolled randomly after character creation (e.g., a cyberlimb might cost `3d6` Humanity).[cite:122][cite:127]

As Humanity drops, EMP is recalculated as the tens digit of the remaining Humanity score.[cite:135] A character who started with EMP 6 (60 Humanity) and loses 21 Humanity now has 39 Humanity — and therefore an EMP of 3. Because EMP drives social skills, installing chrome actively damages social capability. This is the core trade-off: power vs. personhood.[cite:96]

Each piece of cyberware also permanently lowers **maximum Humanity** by 2 (or 4 for heavy Borgware), meaning therapy can only restore you to a progressively lower ceiling as you augment more.[cite:130][cite:135] When Humanity hits 0, the character enters **Cyberpsychosis** — full loss of empathy, erratic violent behavior — and is handed to the GM.[cite:96] Recovery requires weeks of in-patient therapy and potentially removing the cyberware.[cite:136]

The only way to restore Humanity during a campaign is through paid therapy sessions — deliberately inaccessible to broke edgerunners, reinforcing Night City's class divide.[cite:120]

**Why we cannot directly copy this system:**
- The stat is literally named "Empathy" and the mechanic is called "Humanity Loss" — both are named terms from the R. Talsorian rulebook.[cite:93]
- The `EMP × 10 = Humanity` formula is a protectable specific design expression
- The borgware/fashionware/cyberware HL tables with specific dice values are verbatim reproduced game content[cite:122]

**What is absolutely free to use:** The *idea* that augmentation erodes psychological wholeness is not protectable. It's a genre theme found in Philip K. Dick, Ghost in the Shell, Neuromancer, and dozens of other works predating Cyberpunk 2020. The mechanic must be original; the thematic premise is public domain.

---

### Night City Live: The SYNC System

**SYNC** (short for "Signal/Noise — Your Cognitive Coherence") is our full analog to Humanity. It is an original mechanic that achieves every dramatic purpose of the RED system — and adds features specifically designed for the stream format.

#### The Core Concept

SYNC measures Chat-V's coherence as a person: the ratio of organic self to augmented chrome. It's not "empathy" — it's the **signal-to-noise ratio of the human mind**. Too much chrome introduces noise. Too much trauma introduces noise. SYNC dropping doesn't mean you're becoming evil; it means the clean signal of your identity is getting harder to hear under the static of the machine.

This framing is original, thematically richer, and maps to the same mechanical purpose.

#### SYNC Stats

**Base SYNC:** `50` (fixed starting value for all characters, regardless of stats)

**Maximum SYNC:** Starts at 50. Reduced permanently by **Hardwire** (cyberware) installation. Cannot be restored above the current maximum.

**Current SYNC:** Fluctuates between 0 and maximum. Can be restored through **Signal Work** (downtime recovery mechanics, see below).

#### SYNC Loss: Two Sources

**1. Hardwire (cyberware installation)**

Each piece of cyberware installed reduces **maximum SYNC** by a flat amount based on category. No dice roll — flat cost, visible and predictable. This is a design improvement over RED's random HL roll, which can feel arbitrary.

| Cyberware Category | Max SYNC Reduction | Examples |
|---|---|---|
| **Cosmetic Chrome** | 0 | Skinweave patterns, subdermal LED, tattoo implants |
| **Sensory Upgrades** | -2 | Enhanced optics, audio suite, radar sense |
| **Neural Mods** | -5 | Reflex booster, memory chip, neural co-processor |
| **Combat Chrome** | -8 | Mantis Blades, Gorilla Arms, Monowire |
| **Heavy Augmentation** | -15 | Full cyberlimb replacement, subdermal armor plating |
| **Full Conversion** | -30 | Total body conversion (Borg-tier) — starts at 20 max SYNC |

*Cosmetic Chrome has zero SYNC cost because it represents self-expression, not self-erasure. This is an intentional design choice that rewards creative character builds and gives audiences fun appearance decisions with no mechanical downside.*

**2. Trauma (event-based SYNC loss)**

Beyond chrome, psychological trauma drains SYNC. This is completely absent from RED's Humanity system and is an original addition. It means SYNC is not just a cyberware tax — it's a psychological health meter.

| Trauma Event | Current SYNC Loss |
|---|---|
| Watching a teammate die | -3 |
| Failing a mission with major consequences | -2 |
| Killing a named NPC the chat had a relationship with | -4 |
| Being betrayed by a trusted contact | -3 |
| Going full permadeath on a brutal final stand | -5 (applied before the Eulogy stream) |
| Winning against impossible odds | +2 (triumph restores signal) |
| A moment of genuine human connection (audience vote) | +3 |

The positive SYNC events — triumph and connection — are critically important. They give the audience agency over restoration. A vote to have Chat-V reach out to an NPC ally isn't just flavor; it's mechanically healing the character. This creates a feedback loop between narrative choices and system health that RED's Humanity system doesn't offer.

#### The SYNC Threshold Effects

As SYNC drops, the AI GM introduces behavioral changes to Chat-V's narration — subtle at first, escalating dramatically. These are mood and narration directives, not stat penalties. The stat penalties are reserved for lower thresholds to avoid over-penalizing the character early.

| SYNC Range | State | What It Means | GM Narration Directive | Mechanical Effect |
|---|---|---|---|---|
| 41–50 | **Integrated** | Fully coherent | Normal voice, grounded, present | None |
| 31–40 | **Fraying** | Chrome starting to talk back | Occasional dissociative asides. "The optic overlay counts bodies automatically. You didn't ask it to." | None |
| 21–30 | **Glitching** | Signal competing with noise | The AI GM narrates Chat-V noticing intrusive chrome behavior. Hands moving without instruction. Voices in the neural link. | -1 to TALK rolls |
| 11–20 | **Fragmenting** | Identity under serious strain | The AI splits narration voice — normal Chat-V and a colder, mechanical perspective narrating simultaneously | -2 to TALK and JACK; +1 to IRON and BLADE (the machine is taking over) |
| 1–10 | **Static** | On the edge of Signal Loss | The GM narrates in third person: "Chat-V raises the weapon. You're not sure you told them to." | -3 to TALK; +2 to IRON and BLADE; audience choices are overridden once per episode by the "chrome instinct" |
| 0 | **Signal Lost** | Full chromatic break | **See Breakdown Protocol below** | Character enters Breakdown |

The thresholds give the audience visible milestones. When SYNC hits 20, the stream has a "uh oh" moment — not a death, but a warning. The audience can watch the number tick down over weeks and feel dread. When Chat-V gains +3 SYNC from a genuine human moment, it's a relief the entire chat feels together.

#### The Breakdown Protocol (Signal Loss = 0)

When SYNC reaches 0, Chat-V does not immediately die and the campaign does not end. This is a deliberate design choice: **Breakdown is a dramatic climax, not a game over screen.** It is the episode's most intense narrative event.

When Signal Loss triggers:
1. The AI GM announces: *"The signal is gone. Chat-V is Static."*
2. For the remainder of that episode, Chat-V's actions are not chosen by the audience. The AI GM narrates Chat-V acting on pure machine instinct — violent, efficient, emotionless.
3. At the end of the episode, a special **Recovery Vote** is called. The audience votes whether to:
   - **Seek a Psychshrink** (spend 1,000 Eddies, restore SYNC to 15, permanent -5 max SYNC from the damage)
   - **Go Under** (check into a clinic for 2 episodes; restore SYNC to 25, permanent -2 max SYNC)
   - **Push Through** (no treatment; SYNC restored to 5; no max SYNC cost — but it can happen again)
4. If no vote majority forms (unlikely but possible with a deadlocked chat), the AI GM chooses.

This is better than RED's Cyberpsychosis because the audience doesn't lose their character permanently to the GM. They lose *control* temporarily, experience the horror of watching their character act without them, and then have to make a difficult recovery decision together. The Breakdown becomes a campaign-defining episode. It is not a punishment; it is a story arc.

#### Signal Work: Restoring SYNC

SYNC recovery requires narrative downtime — active choices, not just time passing. Between episodes (during the Briefing), the audience can vote to spend a recovery action:

| Signal Work Activity | SYNC Restored | Cost |
|---|---|---|
| **Psychshrink session** | +10 | 500 Eddies |
| **Off the grid** (safe house, no jobs) | +5 | One episode of downtime — no mission |
| **Vice** (Chat-V's chosen vice, established at character creation) | +3 | No Eddies, but requires a MEAT roll DN 12 or lose 1 HP (vice is never clean) |
| **Connection** (meaningful interaction with an NPC ally) | +3 | Requires that NPC to be alive and relationship to be positive |
| **Triumph** (completing a mission without anyone dying) | +2 | Automatic if conditions met |

The Vice mechanic deserves particular attention. At character creation, the audience votes on Chat-V's vice — alcohol, stims, braindance, gambling. Pursuing it restores SYNC (the relief of the familiar) but risks HP (the cost of the habit). This is mechanically clean, thematically rich, and gives the audience another meaningful periodic decision.

---

## Part 4: Roles and Class Identity

### Cyberpunk RED

RED has nine Roles: Solo, Netrunner, Tech, Medtech, Media, Exec, Lawman, Fixer, and Nomad.[cite:109] Each Role has a unique **Role Ability** — a special power only available to that class.[cite:108] Solo gets **Combat Awareness** (initiative and defense bonuses). Netrunner gets **Interface** (net actions and hacking). Fixer gets **Operator** (black market access and information brokering). These Role Abilities are what make each character archetype feel truly distinct — not just a different stat spread.[cite:108]

**IP status:** The nine role names are trademarked terms within the Cyberpunk brand. The *concept* of class-specific special abilities is not protectable, but "Solo," "Netrunner," "Fixer" etc. are R. Talsorian brand terms.

### Night City Live Homebrew: The Edge System

Chat-V does not choose a "role" — roles are too complex to explain to a new viewer in 30 seconds. Instead, at character creation, the audience votes on Chat-V's **Edge**: a single defining specialty that gives them one unique ability no one else has.

**The Edges:**

| Edge Name | Equivalent to RED Role | Special Ability | What It Looks Like On Stream |
|---|---|---|---|
| **Trigger** | Solo | Once per episode, call "Combat Instinct" — automatically succeed on one IRON or BLADE roll without rolling | "Chat-V moves faster than thought. No roll needed." |
| **Ghost** | (same as stat but as an Edge) | Once per episode, call "Vanish" — automatically break line of sight from all enemies | Cinematic disappear-into-shadows sequence |
| **Splice** | Netrunner | Once per episode, "Jack In" to any nearby electronic system and either get information from it OR crash it | Hacking minigame overlay triggers; unique visual event |
| **Fixer** | Fixer | Once per episode, "Call in a Favor" — an NPC contact provides assistance (info, gear, distraction) | Named contact NPC spawns and interacts with Chat-V |
| **Wrench** | Tech | Once per episode, "Jury-Rig" — improvise a device or repair something critical from available parts | Creates a narrative tool that lasts the rest of the episode |
| **Street Doc** | Medtech | Once per episode, "Patch" — restore 15 HP to Chat-V or stabilize a Bleeding Out state for free | Medical animation plays; significant survival value |

Edges are one-use per episode. They refresh at the Briefing. This caps power level and makes each use feel meaningful — the audience knows using the Edge now means it's gone for the rest of the episode.

---

## Part 5: Netrunning

### Cyberpunk RED

Netrunning in RED is a full sub-game. It requires specific cyberware (Neural Link, Interface Plugs, Cyberdeck, Virtuality Goggles) and uses the **Interface** Role Ability to determine how many **Net Actions** per turn the Netrunner gets.[cite:114] The Netrunner enters **NET Architecture** — a dungeon-style multi-floor environment with ICE (security programs) as enemies, **Black ICE** as lethal threats, and file nodes to loot.[cite:111] It runs in parallel with meat-space combat, creating a split narrative where the Netrunner fights digitally while allies fight physically.[cite:117]

This is genuinely brilliant and dramatically rich. It's also complex to present live on stream — two simultaneous combat tracks with different rules is a hard thing to show on a single camera angle.

### Night City Live Homebrew: The Jack-In Sequence

When Chat-V uses the **Splice Edge** (or attempts to hack anything), the Jack-In Sequence triggers. It is streamlined to work as a visual event with meaningful choices.

**The Jack-In Sequence:**

1. **CypherBus delivers a NET Snapshot** to the LLM:
   - Access Point location (physical)
   - Security Tier: 1 (street), 2 (corporate), 3 (military)
   - Active ICE count (1–3 "floors")
   - Target data/system (what's being hacked)

2. **The AI generates a "Cyberspace" description** — visual commands switch CP2077 to a neon-grid aesthetic (time of day: night, weather: clear, camera pushed close and dramatic). The narration describes the NET architecture as Chat-V experiences it.

3. **Each "floor" requires one JACK roll** vs. the Security Tier DN (Tier 1 = DN 12, Tier 2 = DN 15, Tier 3 = DN 18).
   - Success: Floor cleared, move deeper.
   - Failure: ICE response — take 1d10 "Biofeedback" damage that bypasses armor directly.
   - Critical success: Find a bonus data cache (extra Eddies or intel).

4. **On the final floor:** Choose the objective — steal data, crash the system, open a door, or plant a backdoor.

5. **Jack Out:** The whole sequence takes one "combat round" of in-world time, meaning Chat-V is physically vulnerable during it (allies or the situation can be deteriorating while the hack runs).

This gives the Splice Edge its own visual identity and risk/reward loop without building a fully parallel combat system. The Biofeedback damage makes hacking dangerous and interesting. The Security Tier system scales difficulty properly.

---

## Part 6: Reputation & Faction Standing

### Cyberpunk RED

RED tracks **Reputation** as a numeric value (0–10) for each character. When meeting new NPCs, the GM rolls 1d10 and if the result is ≤ the character's Reputation score, the NPC recognizes them.[cite:134] High Reputation is "COOL + Reputation" for contested social rolls. Reputation can be good (heroic) or bad (cowardly/villainous) — some GMs track two separate scores.[cite:134] Street Cred in Cyberpunk 2077 (the video game) is a simplified version of this that unlocks vendors and gear tiers.[cite:131]

### Night City Live Homebrew: Faction Heat & Street Legend

Rather than a single reputation number, Chat-V has two parallel tracks that the audience can see on the overlay at all times:

**HEAT** — How much trouble is coming for you
**LEGEND** — How much respect you've earned

These are independent. High LEGEND and high HEAT is the most interesting state (a famous target). Low LEGEND and low HEAT is a nobody. They move in opposite directions by default: doing big jobs raises both, laying low reduces HEAT but also LEGEND slowly fades.

**Faction Standing** — Chat-V has a relationship with each of Night City's major factions, tracked as a simple three-tier: **Hostile / Neutral / Friendly**. The AI GM maintains these in the character state JSON and uses them to determine how faction NPCs respond.

| Action | LEGEND change | HEAT change | Faction Effect |
|---|---|---|---|
| Complete a high-profile job | +2 | +1 | +1 with hiring faction |
| Betray a contact | -1 | +3 | -1 (Hostile) with betrayed contact's faction |
| Spare an enemy (non-lethal finish) | +1 | +1 | Variable — some factions respect it, some don't |
| Run from a fight (audience votes to flee) | -1 | -1 | None |
| Kill a named/major NPC | +3 | +4 | Hostile with that NPC's faction |
| Complete a job without being seen | +1 | 0 | None (ghost work — nobody knows it was you) |

**HEAT mechanical effects:**
- HEAT 0–3: Standard encounters. Minor gang members may ignore Chat-V.
- HEAT 4–6: Higher-tier enemies. Gangs will attack on sight. Police may show up.
- HEAT 7–9: Bounty hunters and corporate assassins start appearing as random complications.
- HEAT 10: MaxTac-level response. Every episode risks an ambush encounter.

**LEGEND mechanical effects:**
- LEGEND 0–3: Nobody. +0 to TALK with strangers.
- LEGEND 4–6: Known operator. +1 to TALK with faction contacts; fixers offer better gig rates.
- LEGEND 7–9: Street Legend. +2 to all TALK in the city; some enemies will hesitate.
- LEGEND 10: Afterlife status. NPCs whisper about Chat-V. The AI GM names a legendary reputation ("The Phantom of Kabuki," "The Blade of Heywood").

---

## Part 7: Combat Flow

### Cyberpunk RED

RED combat uses a **turn-based initiative system** where each participant rolls `1d10 + REF` to determine order.[cite:95] Each turn, a character gets one Move Action and one Action (attack, reload, use an item, etc.). Armor has **Stopping Power (SP)** that absorbs damage — damage is rolled, SP is subtracted, and the remainder is applied to HP. Armor SP is ablated (reduced) by 1 each time it stops damage, simulating wear.[cite:97][cite:140] Autofire weapons can hit multiple targets but add risk. There are also Aimed Shots (called shots to specific body parts).[cite:97]

### Night City Live Homebrew: Cinematic Combat

For a stream, initiative order and action economy are invisible to the audience — they just want to vote on the outcome. Combat is therefore abstracted to the **Scene Level**, not the **Turn Level**.

**Combat works as follows:**

1. A combat situation is presented (how many enemies, their tier, the environment)
2. The AI presents three tactical options to the audience (one per stat archetype)
3. The audience votes
4. Python rolls `1d10 + relevant STAT` vs. enemy tier DN
5. Result is Success / Failure / Critical / Fumble
6. CP2077 animates the outcome; the AI narrates it

**Enemy Tiers (adapted from RED's NPC classification):**

| Tier | DN to Hit | HP | Armor | Equivalent |
|---|---|---|---|---|
| **Mook** | DN 10 | 10 | 0 | Street grunt, unaugmented gang member |
| **Soldier** | DN 12 | 20 | 2 (reduces damage by 2) | Professional merc, augmented gang enforcer |
| **Elite** | DN 15 | 35 | 5 | Corporate security, seasoned Solo |
| **Boss** | DN 18 | 60 | 8 | Named NPC, cyberpsycho, faction leader |
| **Legend** | DN 20 | 100 | 12 | MaxTac, Arasaka Black Ops |

**Multiple Enemies:** Each additional enemy in the same scene imposes -1 to Chat-V's combat rolls, down to a minimum of -3. This is the "outnumbered" penalty and the main reason the audience should sometimes vote for tactical options over going guns-blazing.

---

## Part 8: Healing & Recovery

### Cyberpunk RED

RED healing is deliberately slow and expensive.[cite:141] A character resting heals BODY stat in HP per day. Speedheal cyberware adds WILL to daily healing. A Medtech's Paramedic skill can stabilize a Mortally Wounded character in the field. Full surgery for critical injuries requires a Medtech facility. There is no equivalent of "potions" — the game wants injury to matter.[cite:141]

### Night City Live Homebrew

Healing pacing is adapted for the episodic format. Between episodes, Chat-V auto-heals partially — injuries don't carry over indefinitely or the show becomes too punishing for a new viewer who just joined.

**Between-Episode Healing:** Chat-V heals `MEAT × 2` HP between each episode. Critical Injuries do NOT heal automatically — they require in-city treatment.

**During an Episode:**
- **Speed Heal (consumable):** Restore `MEAT + 5` HP. One use per episode. Can be purchased with Eddies during the Briefing.
- **Street Doc (Eddies spent during downtime vote):** Full HP restore + remove one Critical Injury. Cost: 200–800 Eddies depending on severity.
- **Trauma Team Protocol (donation tier):** Full HP restore, clears all Critical Injuries. Only available during the Bleeding Out state.

---

## Part 9: Economy & Gear

### Cyberpunk RED

The RED economy uses **Eurodollars (Eddies)** as currency, with items categorized by price tier: Cheap (10eb), Everyday (20eb), Costly (50eb), Premium (100eb), Expensive (500eb), Very Expensive (1,000eb), Luxury (5,000eb), and Super Luxury (10,000eb+).[cite:143] Weapons deal damage in dice pools — a Light Pistol does `2d6`, a Heavy Pistol `3d6`, a Shotgun `5d6`, an Assault Rifle `5d6`.[cite:143] Armor has SP values — Light Armorjack is SP 11, Kevlar is SP 7, Leathers SP 4.[cite:143]

### Night City Live Homebrew

The economy is simplified to audience-legible values. The Eddies currency is kept — it's canonical to the setting and CDPR's IP (from the game, not the TTRPG specifically), so it's safe to use.

**Weapon Damage (homebrew):**

| Weapon Class | Damage | Armor Bypass |
|---|---|---|
| Light Pistol / Knife | 1d6 | 0 |
| Heavy Pistol / Katana | 2d6 | 0 |
| Shotgun / Rifle | 3d6 | 0 |
| Smart Weapon / Military | 2d6 | Half armor |
| Tech Weapon / Railgun | 3d6 | Full armor bypass |

**Armor (homebrew — simplified SP):**

| Armor | Damage Reduction |
|---|---|
| Streetwear | 0 |
| Leathers | -2 damage |
| Light Armorjack | -4 damage |
| Heavy Armorjack | -6 damage |
| Military Plate | -8 damage |

These numbers are original — not reproduced from RED's tables — but achieve the same tiered power progression. A mook with a light pistol shooting at Heavy Armorjack barely scratches through; a military railgun ignores it entirely.

---

## Part 10: Full System Comparison

| System Element | Cyberpunk RED | Night City Live Homebrew | Design Rationale |
|---|---|---|---|
| **Core Stats** | 10 stats (INT, REF, DEX, TECH, COOL, WILL, LUCK, BODY, EMP, MOVE)[cite:95] | 6 stats (IRON, BLADE, GHOST, JACK, TALK, MEAT) | Viewer legibility; entire HUD visible in a banner |
| **Skills** | 60+ named skills, each ranked 1–10[cite:93][cite:94] | Absorbed into stats; no separate skill layer | Reduces character sheet to a 6-number overlay |
| **Resolution** | `1d10 + STAT + Skill vs. DV`[cite:95] | `1d10 + STAT vs. DN` | Functionally identical; stream-friendly |
| **Criticals** | Triggered when 2+ damage dice show 6[cite:116] | Triggered on natural 10 (attack) or natural 1 (defense) | More predictable for LLM output; equally dramatic |
| **Wound States** | 3 tiers (Healthy / Seriously Wounded / Mortally Wounded)[cite:110] | 4 tiers with extended Bleeding Out countdown | Extra tier creates stream-friendly tension window |
| **Death Save** | Immediate: roll ≤ BODY or die[cite:110] | 3-round countdown; audience can intervene | Converts instant death into a dramatic event |
| **Cyberware/Augmentation Track** | Humanity (EMP × 10); random HL dice per item[cite:96][cite:127] | SYNC (flat costs by category); also loses from Trauma | Original name; adds trauma dimension; deterministic costs |
| **Augmentation Ceiling** | Max Humanity reduced -2/-4 per piece[cite:130] | Max SYNC reduced by category flat rate | Same mechanic, original implementation |
| **Psychological Break** | Cyberpsychosis: handed to GM, character lost[cite:96] | Breakdown Protocol: GM takes control for 1 episode, then audience Recovery Vote | Preserves drama; audience retains ultimate ownership |
| **Recovery** | Paid therapy sessions; expensive[cite:120][cite:135] | Signal Work (Psychshrink, Vice, Connection, Triumph) | Adds narrative flavor; Vice mechanic is new and stream-friendly |
| **Roles / Classes** | 9 named Roles with unique abilities[cite:109][cite:108] | 6 Edges with one-use-per-episode special abilities | No trademarked role names; scales to single-character format |
| **Netrunning** | Full sub-game with NET Architecture floors[cite:111][cite:114] | Jack-In Sequence: 1-3 JACK rolls with Biofeedback damage risk | Single-character stream-safe; still risky and visually distinct |
| **Reputation** | Single Reputation score (0–10)[cite:134] | Dual track: HEAT + LEGEND | More dramatic range of states; HEAT creates escalating danger |
| **Faction Relations** | Implicit, GM-managed | Explicit 3-tier JSON: Hostile/Neutral/Friendly | Machine-readable; LLM references it directly |
| **Initiative** | `1d10 + REF` per combatant[cite:95] | Abstracted — audience votes on tactical approach | Turn order invisible to stream audience; not needed |
| **Armor** | SP absorption + SP ablation[cite:97][cite:143] | Flat damage reduction by tier | Simpler math; same power hierarchy |
| **Economy** | Tiered Eurodollar price categories[cite:143] | Same Eddies currency; simplified tier system | Eddies term is from CP2077 game (CDPR IP), not TTRPG specifically |
| **Healing** | Slow, expensive; no potions[cite:141] | Auto-heal between episodes + consumables | Episodic pacing requirement |

---

## Appendix: What Red Has That We Chose Not to Port

Some RED systems were deliberately left out of Night City Live, not because of IP risk, but because they don't serve the stream format.

| RED System | Why We Skipped It |
|---|---|
| **LUCK stat and LUCK pool** | Luck-as-resource requires careful bookkeeping; the audience can't track a second expendable pool alongside HP, SYNC, and Eddies |
| **MOVE stat and tactical movement** | Turn-by-turn positioning is invisible on stream; camera angles handle spatial storytelling |
| **Full 9-role system** | A single protagonist doesn't need 9 role options; Edges give identity without complexity |
| **Vehicle combat rules** | Out of scope for Season 1; add in Season 2 if the show grows |
| **Suppressive fire / Autofire tracking** | Abstracted into the IRON stat; the LLM narrates autofire cinematically without action-economy tracking |
| **Reputation between player characters** | Single protagonist show; not applicable |

---

*Version 1.0 — Night City Live Ruleset Design Bible*
*Cross-referenced against Cyberpunk RED core rules FAQ (R. Talsorian Games, 2021), Roll20 Cyberpunk RED compendium, and REDModding community documentation.*
