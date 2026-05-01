# Numen: Knightfall — Development Log

## Spring 1 (Day 1 to 4)

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

### Next - Sprint 2 (Days 5 — 12)
- Build: dialogue UI widget (UMG), interaction component on placeholder NPC, end-of-day verifying round-trip text-in/text-out inside editor.
- Writing: Complete Chapter 1, go over Chapter 2. 

---

## Sprint 2 (Days 5 - 12)

### Build
- Applied MW Landscape Auto Material (free Fab asset, MAWI United) to St. Damson's landscape. Auto-painting via slope-angle detection produced grass on flats, rock on slopes, dirt in transitions. Smoothed rough edges in the sculpt to clean up material transitions. Landscape now reads as a real outdoor environment rather than untextured prototype.
- Imported PTdesign Medieval Castle ($19.99 Fab) to project. Copied castle actors from demo map into StDamsons map; smoothed landscape sculpt around castle base for integration. Verified in Play mode: collision intact, navigable interiors (rooms, stairs, corridors), no walk-through walls or floaty geometry.
- Created `Content/Numen/{UI,NPCs,Interaction}` folder structure for project work, separating new assets from template content and Marketplace imports.
- Built WBP_DialogueUI widget structure: Vertical Box root containing NPC name Text Block (`Text_NPCName`), scrollable history pane (`Scroll_History`) with inner content container (`VBox_HistoryContent`), and input row (Horizontal Box with `Input_PlayerText` Editable Text Box and `Button_Submit` Button). All five widgets exposed as variables (Is Variable ticked) for Graph access.
- Built complete OnClicked logic for WBP_DialogueUI: reads player input, branches on empty, clears input field, dynamically constructs and appends a "You: {message}" TextBlock to history, then constructs and appends a stub "NPC: You typed: {message}" TextBlock to history. All execution flow and data wiring verified via Blueprint T3D export inspection. Saved and compiled successfully.

### Writing
- Completed Chapter 2 of report/dissertation. 

### Decisions
- **Hand-build both dialogue UIs (LLM and tree baseline) rather than purchase from Fab.** Rationale: methodological control — same UMG widget for both conditions with only the response source swapped, eliminating a threat-to-validity. Also: no Fab plugin supports free-text input + async HTTP responses, which is what the LLM condition requires.
- **Use MW Landscape Auto Material (free, owned) for terrain texturing.** Saves a day of manual painting; auto-painting based on slope angle is appropriate for outdoor training-institute setting.
- **Use PTdesign Medieval Castle ($19.99, owned) as visual backdrop for St. Damson's.** Castle anchors the scene aesthetically; playable area where NPCs live will be courtyard/training-square dressed with smaller props.
- **Use Vertical Box auto-stacking layout for dialogue UI rather than Canvas Panel + manual anchoring.** Rationale: UE5's anchor field behaviour produced unpredictable widget sizing in bottom-stretch mode (specifically Offset Right interpreted as a width override rather than an inset distance, producing 0-width panels). Vertical Box auto-stacking sidesteps anchors entirely. Visual styling deferred to polish pass — current widget is functional but unstyled.
- **Defer widget runtime summoning + end-to-end test to Days 12 - 20.** Rationale: the test of "does the dialogue UI work at runtime" is the same test as "does the middleware round-trip work". Folding both into Day 3 avoids building a stub-summon path tonight that would be replaced tomorrow.
- **Use Blueprint T3D export format for unambiguous graph verification.** Pasting the exported text representation lets supervisor/AI assistant trace exact wire connections rather than guessing from screenshots; resolved several ambiguities in Day 2 wiring debugging.

### Open questions / risks
- Dialogue widget visual styling (colours, anchoring, animations) postponed indefinitely; needs polish pass at end of project before showcase rehearsal.
- UMG anchor system has known quirks in bottom-stretch mode; if visual polish becomes important, consider building styled wrapper widget that contains the auto-stacking widget rather than re-fighting Canvas Panel anchors.
- Castle interior lighting not yet stress-tested; will be relevant if NPCs end up placed indoors rather than in a courtyard.

### Next - Sprint 3 (Days 12 — 20)
- Build: Python FastAPI middleware skeleton; UE5↔FastAPI HTTP plumbing replacing the stub NPC response with a real call; widget runtime summoning via player interaction component to enable end-to-end testing.
- Writing: Go over Chapter 1 and 2 of dissertation. Finish Chapter 3.

## Sprint 3 (Days 12 — 20)

### Build
- Fixed Sprint 2 carry-over UMG issues in `WBP_DialogueUI`: Border was rendering transparent due to two compounding bugs — Brush Tint alpha typo (0.085 vs 0.85) and Border losing its Canvas Panel slot anchoring on a previous edit (Size X had inverted to -500). Re-set slot to bottom-left anchor, Pos (40, -440), Size (500, 400), Alignment (0, 1), Brush Color RGBA (0.05, 0.05, 0.05, 0.85). Widget now renders as intended dark panel.
- Added `DialogueWidgetRef` variable (WBP_DialogueUI Object Reference) on `BP_ThirdPersonCharacter` to track the active widget and prevent stacking.
- Wired E key to open dialogue widget: guarded by `DialogueWidgetRef == None` (Equal Object → Branch) so repeated presses no-op rather than stacking. On open: Create Widget → Set DialogueWidgetRef → Add to Viewport → Set Input Mode Game and UI (with widget focus) → Show Mouse Cursor true.
- Wired Tab key to close dialogue widget (originally Escape, but Escape is intercepted by Standalone preview mode and quits the editor — switched to Tab). On close: Branch on `DialogueWidgetRef != None` → Remove from Parent → Set DialogueWidgetRef None → Set Input Mode Game Only → Show Mouse Cursor false.
- Phase 2 of Day 3 plan complete: replaced inline echo stub in `WBP_DialogueUI` OnClicked logic with real HTTP POST via VaRest plugin to `http://127.0.0.1:8000/dialogue` (POST, JSON content-type, fields `npc_id` = "knight_instructor_marek" and `utterance` = player text). Response handler bound to `OnNPCResponseRecieved` custom event reads `response` field from returned JSON and appends to `VBox_HistoryContent` as "NPC: {message}" line.
- Fixed missing-text bug in chat history: `Format Text` for "You: {message}" was reading from `Get Text (Input_PlayerText)` after `SetText("")` had already cleared the field, because Format Text is a pure function that evaluates on demand. Cached the input value to a new `LastPlayerInput` Text variable before clearing the field; Format Text and JSON utterance field now read from the cached variable.
- End-to-end round-trip verified: press E → widget appears → type "hello" → click Send → "You: hello" appears in history → FastAPI stub responds → "NPC: [stub] You said: hello" appears in history.


### Decisions
- **Used VaRest plugin for HTTP rather than UE5's native HTTP module.** Rationale: VaRest handles the JSON construction and response parsing cleanly through Blueprint nodes; native HTTP module would require manual JSON string building and parsing which adds complexity for no benefit at this stage.
- **Switched dialogue close key from Escape to Tab.** Rationale: Escape is intercepted by UE5 Standalone preview launcher and quits the editor session, blocking testing. Tab is conventional for UI panels in many games and unambiguous.
- **Used `==` (Equal Object) + Branch rather than IsValid macro for null-checking the widget reference.** Rationale: this UE5 install does not surface the IsValid macro under the expected category; the equality-against-None pattern is functionally equivalent for our purposes (object references in Blueprints are either valid or None).
- **Cached input text into `LastPlayerInput` variable before clearing the input field.** Rationale: pure Format Text node evaluates on demand, not on exec wire arrival, so reading from the cleared field returned empty. Caching first preserves correct ordering.

### Open questions / risks
- Phase 3 of original Day 3 plan (placeholder NPC actor + proximity detection) not started. E key currently summons the dialogue anywhere on the map rather than only when near an NPC. Carries into Day 4.
- `npc_id` is hardcoded to `knight_instructor_marek` in the widget. Eventually needs to be passed in from the bound NPC actor when proximity detection is implemented.
- Day 3 originally budgeted ~1.5h for FastAPI middleware + ~2.5h for UE5 plumbing + ~1h for widget summoning + ~1h for writing. Actual time was largely consumed re-debugging Day 2 UMG layout issues that were marked complete in the Day 2 closeout but were not in fact functional. Day 2 evidence may need a corrective note.

### Next - Sprint 4 (Day 21 — 31)
- Carry over from Day 3: place placeholder NPC actor (cube) in level, add proximity detection (overlap volume or line trace), make E key gate on proximity to NPC, pass NPC identity through to the request payload.
- Original Day 4 plan: replace FastAPI stub with actual local LLM inference via llama.cpp (model selection, server startup, prompt templating). Confirm at start of Day 4 that this is still the right call given Day 3 carry-over.
- Writing: catch up on Chapter 2 voice pass and LLM citation verification that slipped from Day 3.

## Sprint 4 (Day 32 - 40)

### Build
- Created `BP_NPC_Base` (Character subclass) at `/Game/Numen/NPCs/`. Components: SkeletalMesh, InteractionSphere (radius 200, OverlapAllDynamic), NameTag TextRender. Variables: `IsPlayerOverlapping` (bool), `NPCId` (String, instance-editable, expose-on-spawn).
- Implemented proximity-gated interaction: `OnComponentBeginOverlap` → cast to BP_ThirdPersonCharacter → set `OverlappingNPC` to self; `OnComponentEndOverlap` clears it to None. Player E-key gated on `OverlappingNPC != None`. Caught and fixed Boolean→String type bug and the End-overlap unwired-cast bug during integration.
- Added `OverlappingNPC` variable to BP_ThirdPersonCharacter; added `NPCId` (String, Instance Editable, Expose on Spawn) to WBP_DialogueUI. NPCId now flows actor → player → widget → JSON request body.
- Marek placed in StDamsons near castle courtyard with custom knight-armour SkeletalMesh from Fab marketplace. Joren and Ren placed as `BP_NPC_Base` instances using default Mannequin appearance. NPCIds: `initiate_joren`, `squire_ren`, `knight_instructor_marek`. Fixed typo `knight_intructor_marek` → `knight_instructor_marek`.
- Downloaded llama.cpp build b8994 (CUDA 13.1) plus cudart runtime DLLs to `source/inference/`. Downloaded Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf (~4.92 GB) from bartowski's HF repo. Added `source/inference/` to `.gitignore`.
- Launched `llama-server.exe --model ...Q4_K_M.gguf --port 8080 --n-gpu-layers 99 --ctx-size 4096`. Result: 33/33 layers on GPU, CUDA0 buffer 4,403.49 MiB, KV cache 512 MiB, listening on 127.0.0.1:8080. Verification curl test: 411 ms total (313 ms prompt + 98 ms generation) on a small completion. Strong early signal for H4.
- Replaced FastAPI middleware stub with real llama.cpp integration. Added `httpx` to venv. New async `_call_llama_server(prompt)` function POSTs OpenAI-compatible payload (temp 0.7, max_tokens 200) to `http://127.0.0.1:8000/v1/chat/completions`. Errors mapped to 503 (unreachable) / 502 (malformed). Stub retained for offline testing. First successful real Llama response: Marek to "Tell me about yourself" → in-character.
- Added `Set Auto Wrap Text` node to WBP_DialogueUI on both NPC-response and player-side text chains. Long Llama responses now wrap correctly inside the panel.
- Added second prompt directive in `construct_prompt()` mid-day after presupposition-acceptance finding (see Decisions): "If the traveller mentions a name, place, title, institution, or event you have not been told about above, treat it as unfamiliar..."

### Writing
- Pass 1 of dissertation: verified four dialogue-system citations (Mateas & Stern 2003, Lankoski & Björk 2007, Crawford 2004, Riedl & Bulitko 2013). Added Lankoski page numbers (416–423, Tokyo) and Mateas venue (San Jose). Rewrote §2.2.2 sentence to correctly characterise Riedl as a survey paper rather than the fictional "Storyteller system".
- Pass 2 of dissertation (full pass): filled out Sprint 2 chapter (§§4.3.1–4.3.5) with real implementation content drawn from today's build. Added Tables 4.2 (per-tier fact counts), 4.3 (per-NPC permitted_tiers), and 4.4 (stratified-gating manual-validation responses). Added Figure 4.2 (VaRest Blueprint screenshot) replacing fictional C++ listing in §4.2.3. Added Figure 4.3 (FastAPI log of all-three-NPCs request showing stratified gating). Added new §4.3.6 "Manual Validation During Development" documenting today's empirical findings. Added §4.4.1 NPC Placement narrative covering the BP_NPC_Base parent-Blueprint design pattern. Updated Chapter 3 §3.5 to document the prompt's two-directive structure (grounding case vs presupposition case). Corrected GPU spec, asset-table caption, and §4.2.3 narrative. Verified six more bibliography entries (Touvron, Jiang, Ouyang, Wei, Perez, Gerganov). Added Pavlovets 2024 reference for VaRest plugin.
- Final clean docx (all changes accepted, no tracked-change markup) saved as the new working master.

### Decisions
- **Presupposition-acceptance is a separate failure mode from leakage.** Round 1 of manual validation (Tell me about the Knight-Commander, asked of all three NPCs) showed: Joren hedged with speculation, Ren fabricated a name (Thrain) absent from any tier, Marek correctly named Sir Halric of the Vale. Strict-form structural gating (Sir Halric never produced by lower tiers) held; the broader form (resistance to adversarial framing in player's utterance) did not. Decision: add a second prompt directive instructing the model to treat unfamiliar named entities as unfamiliar. Round 2 after the directive: clean refusals from Joren and Ren, Marek's behaviour unchanged. This becomes a key finding for the dissertation: structural and prompt-discipline mechanisms are complementary, not redundant.
- **Use a single BP_NPC_Base parent Blueprint for all NPCs rather than separate subclasses.** Adding a fourth NPC requires only placing an instance and setting NPCId. Modifications to interaction logic affect all instances atomically. Trade-off: per-NPC visual variation must be expressed through instance-level mesh overrides rather than subclasses — acceptable for this project.
- **VaRest plugin instead of custom C++ Blueprint Function Library.** Decision rationale: minimise engine-side complexity, no C++ compilation needed, JSON construction stays in Blueprint where the rest of the dialogue logic lives. Documented in section 4.2.3.
- **Defer response validator implementation.** The defence-in-depth validator described in §3.5 step 6 is not implemented. Rationale: the structural mechanism (tier filtering) is the load-bearing component for H2; validator is secondary defence. Documented as project limitation in §4.3.5. Re-evaluate during Sprint 3.
- **No Tier-4-permitted NPC in the demo.** Methodologically motivated: keeps Tier-4 facts (Concord of Aethelmere etc.) as a clean out-of-tier control for all three NPCs in H2 testing. Documented in §4.3.2.

### Open questions
- The validator question above remains genuinely open. If Sprint 3 capacity exists, we should implement it; otherwise it's deferred to future work.
- Animation: NameTag does not yet billboard to face camera. ScrollBox does not auto-scroll on new message. Enter-to-send keybinding not yet wired. No "thinking" indicator while awaiting LLM response. None are blocking but all degrade UX in the demo.
- About 12 ⚠ citations in the bibliography still need verification before submission (Bai, Frantar, Gao, Kaplan, Li, Lin, Meta AI 2024, Montfort, NVIDIA, Ryan, Shuster, Wang). Not urgent but cumulative.
- In-text citation markers (e.g., "Touvron et al., 2023 ⚠") still show ⚠ in the body even though the bibliography entries are now ✓. Decide before submission whether to flip in-text markers globally or strip the convention from the final draft entirely.

### Next - Sprint 5 (Day 40 - 55)
- **First action when starting:** open the conversation, then run `git status` and bring up FastAPI + llama-server in their two PowerShell windows to verify the system still works end-to-end after a sleep cycle.
- **Build priority 1:** Dialogue-tree baseline implementation (§4.4.3 of dissertation, currently `[TO BE COMPLETED]`). This is the H1 control condition. Authoring at least one full tree per NPC for the H1 study.
- **Build priority 2:** Mixamo retargeting for at least Joren and Ren — get them onto a non-default idle. Marek already has the custom mesh.
- **Build priority 3 (if time):** UX polish — billboard NameTag, scrollbox auto-scroll, Enter-to-send, thinking indicator.
- **Writing:** §4.4.3 fill-in once the dialogue-tree baseline is in. Possibly start §4.4.2 environment dressing.
