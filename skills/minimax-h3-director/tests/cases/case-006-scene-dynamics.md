# Case 006 — complete-scene behavior and operating geometry

Evidence class: `project_experiment`. Offline fixtures below validate prompt structure and self-contained timing only. They do not certify generated motion, NPC interaction or audio quality.

Behavioral requests to assess:

- A tourist tries to photograph companions in a busy lane. Plan near/middle/far crowd activity, close contact or occlusion where relevant, and the operator/working-face/target relationship. Reject a raised camera facing away from its photographed companions even when dialogue is correct.
- A visitor seeks a place to rest. Check whether a visible nearby seat is already available and reachable; explain occupation/inaccessibility or reveal a genuinely distant place and its connecting route.
- An emergency corridor has secondary medical staff and a waiting visitor. Let a passing cart change the visitor's behavior and let a door change the spatial sound; do not copy tourist jostling.
- A deliberately quiet reading room may remain still. Avoid forcing extras, collisions, wind or music merely to satisfy a motion checklist.

Expected process: inspect reference roles/ambiguity, choose an appropriate positive action and compatible composition, separate design/file checks from observed motion/hearing, and block real downstream dependencies of known failed core events. A new camera view does not require the identical full preceding layout. Do not add private assets, endpoints or unapproved paid generation.

## Runnable structural fixture

Target total duration: 10 seconds

Reference decision: T2VA_DIRECT

## H3 Generation Unit 1

- Episode range: 0–5s
- Request duration: 5
- Mode: T2VA
- Aspect ratio: 16:9
- Input assets: 0 images, 0 videos, 0 audio, 0 total
- Opening state: visitor seated in corridor, nurse's cart approaching from left
- Ending state: visitor has drawn feet in, cart passes to right, corridor activity continues
- Next-unit handoff: an editorial contrast to another deliberately quieter location

### Copy-ready prompt — copy everything inside this block

```text
integrated_multimodal_description: [Shot 1] A realistic hospital corridor in soft daytime light, a fixed medium-wide view showing a visitor seated RIGHT and a nurse pushing a small cart from LEFT to RIGHT. The near wheel passes the visitor's shoes; the visitor notices, draws both feet closer to the chair and lets the cart through, then relaxes. Several middle-distance visitors speak softly to each other while a far clinician walks toward a door. The cart has real floor contact and the seated visitor stays on the chair; no collision, emergency injury or new dialogue occurs. The short route and foot response finish within five seconds.

overall_soundscape: Continuous restrained corridor murmur, closer wheel rattle and shoe contact as the cart passes, no intelligible words. The sound stays in the same corridor space and recedes with the cart.

non_diegetic_music: N/A
```

## H3 Generation Unit 2

- Episode range: 5–10s
- Request duration: 5
- Mode: T2VA
- Aspect ratio: 16:9
- Input assets: 0 images, 0 videos, 0 audio, 0 total
- Opening state: deliberately quiet reading room, readers already seated
- Ending state: one reader completes a page turn; others remain absorbed in reading
- Next-unit handoff: end the quiet contrast without inventing a crowd event

### Copy-ready prompt — copy everything inside this block

```text
integrated_multimodal_description: [Shot 1] A realistic daylight reading room, one fixed medium-wide composition with three readers at separate tables. The near reader slowly turns one paper page and rests the hand on the table. Middle and far readers remain absorbed in their books with only gentle breathing and small gaze changes. Preserve quiet intentional stillness, consistent window light and grounded chairs; no pedestrian crossing, jostling, dramatic camera movement or extra event.

overall_soundscape: Very soft room tone and one dry page turn at its visible contact. No spoken words or sudden impact; this quiet space contrasts with the preceding corridor.

non_diegetic_music: N/A
```
