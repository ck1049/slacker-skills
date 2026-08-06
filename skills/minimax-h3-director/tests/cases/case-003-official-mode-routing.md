# Case 003 — official H3 mode routing

Input A: “Create a 15-second anime video from text only.”
Expected A: routes to T2VA, reads the official base guide, uses the ordered three-field English rewrite, and emits no Subject/Picture/Video/Audio labels.

Input B: “Use these character, motion-video, and music references to make a new video.”
Expected B: routes to Ref2VA, reads the official full-reference guide, writes a binding manifest outside the prompt, uses all six ordered English sections, assigns role-correct reference labels, records each label in retention analysis, and keeps filenames and paths out of the copy-ready block.

Input C: “Use this image as the exact last frame of a six-second video.”
Expected C: routes to L2VA, places the official picture-alignment instruction first with `6.00` seconds, converges to the supplied frame, and then uses the ordered three base fields.

Packaging assertion: all three inputs remain fully supported when only the `minimax-h3-director/` directory is present. No runtime path may traverse to `../official/` or require a separately installed skill.
