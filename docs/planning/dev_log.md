# Numen: Knightfall — Development Log

## Day 1 — 28 Decemeber 2025

### Build
- Cloned existing GitHub repo locally to `C:\GameDev\Numen-Knightfall`.
- Restructured repo from flat artefact dump into `docs/`, `source/`, `study/` layout.
- Added project-root `.gitignore` covering UE5, Python, llama.cpp, and OS junk.
- Authored `README.md` with project title, vision, hypotheses, architecture, repository structure.
- Created UE 5.7 Third Person Blueprint project at `source/unreal/Numen` with Open World level.
- Imported 4033×4033 Gaea heightmap as Landscape (Section Size 63×63, Components 64×64, clean 1:1 mapping).
- Resculpted and rescaled landscape to St. Damson's footprint — descoped from full 4km² wilderness to focused training-institute scale.
- Configured PlayerStart and `BP_ThirdPersonGameMode` as default. Default Mannequin walks/runs across terrain via WASD + space.
- Added project-local `.gitignore` inside `source/unreal/Numen/`.
- Verified no files >50 MB before commit. 372 MB total project, 224 MB ignored (cache), 148 MB committed (Content + Mannequin assets retained for NPC use).
- Committed and pushed to GitHub.

### Writing
- Drafted Chapters 1–5 of dissertation.
- Established structure: 8 numbered chapters + appendices, with Methodology after Implementation, separated Results/Discussion, LSEP integrated rather than dedicated chapter.
- Citation list compiled.

### Decisions
- **Descoped landscape from 4km² to St. Damson's footprint.** Rationale: vertical-slice demo doesn't need wilderness; smaller area is easier to dress, render, and demo live.
- **Build LLM pipeline first, polish environment after.** Rationale: integration risk concentrates in middleware/inference layer; landscape work is solved territory.
- **Cut speech fingerprinting and event propagation from May 5th scope.** Rationale: time budget; both deferred to dissertation Future Work chapter.
- **Participant testing approach: existing ethics approval covers Likert + blind transcript study (H1, H3); H2 and H4 fully automated.**

### Open questions / risks
- llama.cpp on Windows alongside UE5 in editor — concurrent memory pressure unknown until Day 4.
- Dissertation citations need Google Scholar verification before submission.
- AI Use Declaration appendix needs filling continuously, not reconstructed at end.

### Tomorrow (Day 2 — 29 Dec)
- Build: dialogue UI widget (UMG), interaction component on placeholder NPC, end-of-day verifying round-trip text-in/text-out inside editor.
- Writing: voice-pass on Chapter 1 of dissertation. 

---

## Day 2 — 29 Dec 2025

### Build
- Applied MW Landscape Auto Material (free Fab asset, MAWI United) to St. Damson's landscape. Auto-painting via slope-angle detection produced grass on flats, rock on slopes, dirt in transitions. Smoothed rough edges in the sculpt to clean up material transitions. Landscape now reads as a real outdoor environment rather than untextured prototype.
- Imported PTdesign Medieval Castle ($19.99 Fab) to project. Copied castle actors from demo map into StDamsons map; smoothed landscape sculpt around castle base for integration. Verified in Play mode: collision intact, navigable interiors (rooms, stairs, corridors), no walk-through walls or floaty geometry.
- Created `Content/Numen/{UI,NPCs,Interaction}` folder structure for project work, separating new assets from template content and Marketplace imports.
- Built WBP_DialogueUI widget structure: Vertical Box root containing NPC name Text Block (`Text_NPCName`), scrollable history pane (`Scroll_History`) with inner content container (`VBox_HistoryContent`), and input row (Horizontal Box with `Input_PlayerText` Editable Text Box and `Button_Submit` Button). All five widgets exposed as variables (Is Variable ticked) for Graph access.
- Built complete OnClicked logic for WBP_DialogueUI: reads player input, branches on empty, clears input field, dynamically constructs and appends a "You: {message}" TextBlock to history, then constructs and appends a stub "NPC: You typed: {message}" TextBlock to history. All execution flow and data wiring verified via Blueprint T3D export inspection. Saved and compiled successfully.

### Writing
- (deferred to evening session: voice pass on Chapter 1, citation verification)

### Decisions
- **Hand-build both dialogue UIs (LLM and tree baseline) rather than purchase from Fab.** Rationale: methodological control — same UMG widget for both conditions with only the response source swapped, eliminating a threat-to-validity. Also: no Fab plugin supports free-text input + async HTTP responses, which is what the LLM condition requires.
- **Use MW Landscape Auto Material (free, owned) for terrain texturing.** Saves a day of manual painting; auto-painting based on slope angle is appropriate for outdoor training-institute setting.
- **Use PTdesign Medieval Castle ($19.99, owned) as visual backdrop for St. Damson's.** Castle anchors the scene aesthetically; playable area where NPCs live will be courtyard/training-square dressed with smaller props.
- **Use Vertical Box auto-stacking layout for dialogue UI rather than Canvas Panel + manual anchoring.** Rationale: UE5's anchor field behaviour produced unpredictable widget sizing in bottom-stretch mode (specifically Offset Right interpreted as a width override rather than an inset distance, producing 0-width panels). Vertical Box auto-stacking sidesteps anchors entirely. Visual styling deferred to polish pass — current widget is functional but unstyled.
- **Defer widget runtime summoning + end-to-end test to Day 3.** Rationale: the test of "does the dialogue UI work at runtime" is the same test as "does the middleware round-trip work". Folding both into Day 3 avoids building a stub-summon path tonight that would be replaced tomorrow.
- **Use Blueprint T3D export format for unambiguous graph verification.** Pasting the exported text representation lets supervisor/AI assistant trace exact wire connections rather than guessing from screenshots; resolved several ambiguities in Day 2 wiring debugging.

### Open questions / risks
- Dialogue widget visual styling (colours, anchoring, animations) postponed indefinitely; needs polish pass at end of project before showcase rehearsal.
- UMG anchor system has known quirks in bottom-stretch mode; if visual polish becomes important, consider building styled wrapper widget that contains the auto-stacking widget rather than re-fighting Canvas Panel anchors.
- Castle interior lighting not yet stress-tested; will be relevant if NPCs end up placed indoors rather than in a courtyard.

### Tomorrow (Day 3 — 30 Dec)
- Build: Python FastAPI middleware skeleton (Day 3 morning); UE5↔FastAPI HTTP plumbing replacing the stub NPC response with a real call (Day 3 afternoon); widget runtime summoning via player interaction component to enable end-to-end testing.
- Writing: Go over Chapter 1 of dissertation. 