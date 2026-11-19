# TAC animated posts

Owner direction (Nov 18, 2026): more posts like draft 3. Troy called draft03_story_narration "great" and asked to aim toward more like it.

## The format that worked (draft 3)
- 1080x1920, 30 fps, about 30 seconds. Navy and cream brand style, Zilla Slab headings, Source Serif body, anchor emblem, "Illustrative example" label.
- Story in four beats on a phone screen: type the hurtful text, delete it, ask TAC, send the better message and get a good reply. End card: "Pause. Ask. Say it better." with beta sign-up and theanchoredcompass.com.
- Narration tells the feeling, not what is typed: frustration, regret, the real feeling underneath, relief. My Cloned Voice 2 (3I71Zn2e3uB3r46oQcdv), eleven_v4, one take per line, with emotion tags.
- Say "Tack", not T-A-C: write it as "Tack" in narration text.
- Music: Calm Mind (Pixabay license, see week1-music/MUSIC_LICENSES.md), low under the voice; mix leveled to -16 LUFS.

## Folders
- draft01_say_it_better: silent version with music, plus the scene source (scene.html, fonts, render scripts).
- draft02_narrated: headers-only narration (superseded by draft 3).
- draft03_story_narration: the approved style, with NARRATION.md and the five voice lines.

## Series (Nov 18, 2026): five story videos in the draft 3 style
- series/<boss|partner|coparent|coworker|mom>/TAC_anim_<name>.mp4, each with NARRATION.md and its voice lines s1-s5.mp3 (line 5 reuses the draft 3 take).
- Texts and narration live in series/scenarios.json; series/build.py renders any of them (`python3 build.py <name|all>`), timing set from text length so narration never overlaps. Scene source and music in series/_src.
- Loudness evened to about -16 LUFS, peaks under -1 dBFS.
