# ITDcarry — Thinuka’s school pitch

## Open on another laptop

1. Download and extract `ITDcarry-presentation.zip` (or download `OPEN-PRESENTATION.html` on its own).
2. Open `OPEN-PRESENTATION.html` in a current Chrome, Edge, Firefox or Safari browser.
3. Click **Start presentation**, then **Fullscreen**. Advance using **Next**, Right Arrow or Space.
4. On slide 4, **Next** advances one demo step at a time. **Back** revisits the previous step. Click any of the four step labels to jump directly to it. Each step holds until you advance; **Reset demo** returns to step 1.
5. Read `PRESENTATION-SCRIPT.txt` while rehearsing. The simpler script follows the slide headings and each demo step. **Script / sources** shows just the words for your current slide or step. Aim for about three minutes with pointing and pauses; there are no timed demo transitions.

All presentation media is embedded in the HTML. No Python, Node, server, sign-in or internet is needed for playback. Test the browser on the presenting laptop beforehand. GitHub/Drive preview is not the presentation player: download the file and open it locally. The MP4 backup is available if local HTML is restricted.

## Files

- `OPEN-PRESENTATION.html`: click-controlled slides with Remotion-rendered animations. The demo uses four embedded frames from the original rendered demo so every step appears immediately and holds until you advance.
- `PRESENTATION-SCRIPT.txt`: simple speaking script, click cues and pinned sources.
- `ITDcarry-demo-40s.mp4`: original standalone silent demo for live narration. Its playback is still timed; use the HTML for manual step control.
- `ITDcarry-pitch-3min.mp4`: original 180-second silent video backup. Its fixed timings are independent of the revised script.
- `evidence/`: actual local output, raw TSV, reference verdicts and hash checks.
- `remotion-source/`: editable Remotion 4.0.539 source. To edit, install Node.js, run `npm ci` then `npm run dev`. `node render.mjs` exports the scene videos to a sibling `renders` folder.

## What was actually run

Reviewed source: [commit 789290a](https://github.com/thinuka-rgb/itdcarry/tree/789290a1557cae5854cd32b5e2d0b043d7db95e3).

The vendored getITD 1.5.17 caller ran locally against the repository fixture, under the compatible and changed profiles. The repository parser and exact matcher evaluated its real output. Both runs exited 0; compatible recovered the position-72, 21-base marker exactly; changed did not. Both input-file hashes matched the committed manifest. Windows checkout line-ending conversion was corrected by restoring the FASTQ bytes from the Git objects before the final recorded runs. The repository test suite passed all 23 tests (one dependency deprecation warning).

The demo is an animated replay of those local results with edited pacing, not a screen recording of the hosted application. The result labels use the repository’s `local_verdict` reference semantics. Daytona and Neo4j were not run; this does not validate those integrations. The full application is designed to get its production verdict from Neo4j.

No patient data was used. This is a non-clinical synthetic proof of concept, not a diagnosis, treatment recommendation, or validation of laboratory processes. The approval request is for an educational school demonstration.

### Evidence reproduction

The helper `evidence/run_local_demo.py` is supplied for inspection. In a working folder, place it next to a checkout named `itdcarry`, install that checkout’s dependencies, and run it using that environment’s Python. On Windows, preserve the committed FASTQ LF bytes (`git -c core.autocrlf=false clone …`). The helper writes a sibling `local-evidence` folder. It does not invoke cloud services.

### Presentation control check

Run `node presentation/test-controls.cjs` from the repository root. This uses Node's standard library to check forward/back navigation, direct demo selection, reset, keyboard controls, and the embedded script against the text file.
