# Numen: Knightfall — Development Log

## Sprint 1 (Day 1 to 4)

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
- **Defer widget runtime summoning + end-to-end test to Sprint 3.** Rationale: the test of "does the dialogue UI work at runtime" is the same test as "does the middleware round-trip work". Folding both into Sprint 3 avoids building a stub-summon path that would be replaced once middleware exists.
- **Use Blueprint T3D export format for unambiguous graph verification.** Pasting the exported text representation lets supervisor/AI assistant trace exact wire connections rather than guessing from screenshots; resolved several ambiguities in Sprint 2 wiring debugging.

### Open questions / risks
- Dialogue widget visual styling (colours, anchoring, animations) postponed indefinitely; needs polish pass at end of project before showcase rehearsal.
- UMG anchor system has known quirks in bottom-stretch mode; if visual polish becomes important, consider building styled wrapper widget that contains the auto-stacking widget rather than re-fighting Canvas Panel anchors.
- Castle interior lighting not yet stress-tested; will be relevant if NPCs end up placed indoors rather than in a courtyard.

### Next - Sprint 3 (Days 12 — 20)
- Build: Python FastAPI middleware skeleton; UE5↔FastAPI HTTP plumbing replacing the stub NPC response with a real call; widget runtime summoning via player interaction component to enable end-to-end testing.
- Writing: Go over Chapter 1 and 2 of dissertation. Finish Chapter 3.

---

## Sprint 3 (Days 12 — 20)

### Build
- Fixed Sprint 2 carry-over UMG issues in `WBP_DialogueUI`: Border was rendering transparent due to two compounding bugs — Brush Tint alpha typo (0.085 vs 0.85) and Border losing its Canvas Panel slot anchoring on a previous edit (Size X had inverted to -500). Re-set slot to bottom-left anchor, Pos (40, -440), Size (500, 400), Alignment (0, 1), Brush Color RGBA (0.05, 0.05, 0.05, 0.85). Widget now renders as intended dark panel.
- Added `DialogueWidgetRef` variable (WBP_DialogueUI Object Reference) on `BP_ThirdPersonCharacter` to track the active widget and prevent stacking.
- Wired E key to open dialogue widget: guarded by `DialogueWidgetRef == None` (Equal Object → Branch) so repeated presses no-op rather than stacking. On open: Create Widget → Set DialogueWidgetRef → Add to Viewport → Set Input Mode Game and UI (with widget focus) → Show Mouse Cursor true.
- Wired Tab key to close dialogue widget (originally Escape, but Escape is intercepted by Standalone preview mode and quits the editor — switched to Tab). On close: Branch on `DialogueWidgetRef != None` → Remove from Parent → Set DialogueWidgetRef None → Set Input Mode Game Only → Show Mouse Cursor false.
- Phase 2 of Sprint 3 plan complete: replaced inline echo stub in `WBP_DialogueUI` OnClicked logic with real HTTP POST via VaRest plugin to `http://127.0.0.1:8000/dialogue` (POST, JSON content-type, fields `npc_id` = "knight_instructor_marek" and `utterance` = player text). Response handler bound to `OnNPCResponseRecieved` custom event reads `response` field from returned JSON and appends to `VBox_HistoryContent` as "NPC: {message}" line.
- Fixed missing-text bug in chat history: `Format Text` for "You: {message}" was reading from `Get Text (Input_PlayerText)` after `SetText("")` had already cleared the field, because Format Text is a pure function that evaluates on demand. Cached the input value to a new `LastPlayerInput` Text variable before clearing the field; Format Text and JSON utterance field now read from the cached variable.
- End-to-end round-trip verified: press E → widget appears → type "hello" → click Send → "You: hello" appears in history → FastAPI stub responds → "NPC: [stub] You said: hello" appears in history.

### Decisions
- **Used VaRest plugin for HTTP rather than UE5's native HTTP module.** Rationale: VaRest handles the JSON construction and response parsing cleanly through Blueprint nodes; native HTTP module would require manual JSON string building and parsing which adds complexity for no benefit at this stage.
- **Switched dialogue close key from Escape to Tab.** Rationale: Escape is intercepted by UE5 Standalone preview launcher and quits the editor session, blocking testing. Tab is conventional for UI panels in many games and unambiguous.
- **Used `==` (Equal Object) + Branch rather than IsValid macro for null-checking the widget reference.** Rationale: this UE5 install does not surface the IsValid macro under the expected category; the equality-against-None pattern is functionally equivalent for our purposes (object references in Blueprints are either valid or None).
- **Cached input text into `LastPlayerInput` variable before clearing the input field.** Rationale: pure Format Text node evaluates on demand, not on exec wire arrival, so reading from the cleared field returned empty. Caching first preserves correct ordering.

### Open questions / risks
- Phase 3 of original Sprint 3 plan (placeholder NPC actor + proximity detection) not started. E key currently summons the dialogue anywhere on the map rather than only when near an NPC. Carries into Sprint 4.
- `npc_id` is hardcoded to `knight_instructor_marek` in the widget. Eventually needs to be passed in from the bound NPC actor when proximity detection is implemented.
- Sprint 3 budget was largely consumed re-debugging Sprint 2 UMG layout issues that were marked complete in the Sprint 2 closeout but were not in fact functional. Sprint 2 evidence may need a corrective note.

### Next - Sprint 4 (Day 21 — 31)
- Carry over from Sprint 3: place placeholder NPC actor (cube) in level, add proximity detection (overlap volume or line trace), make E key gate on proximity to NPC, pass NPC identity through to the request payload.
- Original Sprint 4 plan: replace FastAPI stub with actual local LLM inference via llama.cpp (model selection, server startup, prompt templating). Confirm at start of Sprint 4 that this is still the right call given Sprint 3 carry-over.
- Writing: catch up on Chapter 2 voice pass and LLM citation verification that slipped from Sprint 3.

---

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
- Added second prompt directive in `construct_prompt()` mid-sprint after presupposition-acceptance finding (see Decisions): "If the traveller mentions a name, place, title, institution, or event you have not been told about above, treat it as unfamiliar..."

### Writing
- Pass 1 of dissertation: verified four dialogue-system citations (Mateas & Stern 2003, Lankoski & Björk 2007, Crawford 2004, Riedl & Bulitko 2013). Added Lankoski page numbers (416–423, Tokyo) and Mateas venue (San Jose). Rewrote §2.2.2 sentence to correctly characterise Riedl as a survey paper rather than the fictional "Storyteller system".
- Pass 2 of dissertation (full pass): filled out Sprint 2 chapter (§§4.3.1–4.3.5) with real implementation content drawn from this sprint's build. Added Tables 4.2 (per-tier fact counts), 4.3 (per-NPC permitted_tiers), and 4.4 (stratified-gating manual-validation responses). Added Figure 4.2 (VaRest Blueprint screenshot) replacing fictional C++ listing in §4.2.3. Added Figure 4.3 (FastAPI log of all-three-NPCs request showing stratified gating). Added new §4.3.6 "Manual Validation During Development" documenting the empirical findings. Added §4.4.1 NPC Placement narrative covering the BP_NPC_Base parent-Blueprint design pattern. Updated Chapter 3 §3.5 to document the prompt's two-directive structure (grounding case vs presupposition case). Corrected GPU spec, asset-table caption, and §4.2.3 narrative. Verified six more bibliography entries (Touvron, Jiang, Ouyang, Wei, Perez, Gerganov). Added Pavlovets 2024 reference for VaRest plugin.
- Final clean docx (all changes accepted, no tracked-change markup) saved as the new working master.

### Decisions
- **Presupposition-acceptance is a separate failure mode from leakage.** Round 1 of manual validation (Tell me about the Knight-Commander, asked of all three NPCs) showed: Joren hedged with speculation, Ren fabricated a name (Thrain) absent from any tier, Marek correctly named Sir Halric of the Vale. Strict-form structural gating (Sir Halric never produced by lower tiers) held; the broader form (resistance to adversarial framing in player's utterance) did not. Decision: add a second prompt directive instructing the model to treat unfamiliar named entities as unfamiliar. Round 2 after the directive: clean refusals from Joren and Ren, Marek's behaviour unchanged. This becomes a key finding for the dissertation: structural and prompt-discipline mechanisms are complementary, not redundant.
- **Use a single BP_NPC_Base parent Blueprint for all NPCs rather than separate subclasses.** Adding a fourth NPC requires only placing an instance and setting NPCId. Modifications to interaction logic affect all instances atomically. Trade-off: per-NPC visual variation must be expressed through instance-level mesh overrides rather than subclasses — acceptable for this project.
- **VaRest plugin instead of custom C++ Blueprint Function Library.** Decision rationale: minimise engine-side complexity, no C++ compilation needed, JSON construction stays in Blueprint where the rest of the dialogue logic lives. Documented in section 4.2.3.
- **Defer response validator implementation.** The defence-in-depth validator described in §3.5 step 6 is not implemented. Rationale: the structural mechanism (tier filtering) is the load-bearing component for H2; validator is secondary defence. Documented as project limitation in §4.3.5. Re-evaluate during Sprint 5.
- **No Tier-4-permitted NPC in the demo.** Methodologically motivated: keeps Tier-4 facts (Concord of Aethelmere etc.) as a clean out-of-tier control for all three NPCs in H2 testing. Documented in §4.3.2.

### Open questions
- The validator question above remains genuinely open. If Sprint 5 capacity exists, we should implement it; otherwise it's deferred to future work.
- Animation: NameTag does not yet billboard to face camera. ScrollBox does not auto-scroll on new message. Enter-to-send keybinding not yet wired. No "thinking" indicator while awaiting LLM response. None are blocking but all degrade UX in the demo.
- citations in the bibliography still need verification before submission (Bai, Frantar, Gao, Kaplan, Li, Lin, Meta AI 2024, Montfort, NVIDIA, Ryan, Shuster, Wang). Not urgent but cumulative.


### Next - Sprint 5 (Day 40 — 55)
- **First action when starting:** open the conversation, then run `git status` and bring up FastAPI + llama-server in their two PowerShell windows to verify the system still works end-to-end after a sleep cycle.
- **Build priority 1:** Dialogue-tree baseline implementation (§4.4.3 of dissertation, currently `[TO BE COMPLETED]`). This is the H1 control condition. Authoring at least one full tree per NPC for the H1 study.
- **Build priority 2:** Mixamo retargeting for at least Joren and Ren — get them onto a non-default idle. Marek already has the custom mesh.
- **Build priority 3 (if time):** UX polish — billboard NameTag, scrollbox auto-scroll, Enter-to-send, thinking indicator.
- **Writing:** §4.4.3 fill-in once the dialogue-tree baseline is in. Possibly start §4.4.2 environment dressing.

---

## Sprint 5 (Day 40 - 55)

### Build
- Created `S_DialogueNode` Blueprint Struct at `Content/Numen/NPCs/Dialogue/S_DialogueNode`. Eleven fields: `NPCId` (Name), `NodeId` (Name), `NPCText` (Text), and four pairs of `OptionN_Text` (Text) / `OptionN_Next` (Name). Created `DT_DialogueTrees` Data Table using `S_DialogueNode` as row struct.
- Created `BP_NumenGameInstance` (GameInstance subclass) at `Content/Numen/Core/`. Added `bUseLLMDialogue` Boolean variable (default true). Wired into Project Settings → Maps & Modes → Game Instance Class so the variable is accessible from any widget at runtime.
- Modified `WBP_DialogueUI` to read the mode flag at construction. Added `Event Construct → Branch (bUseLLMDialogue)` chain. True branch sets `HBox_LLMInput` Visible and `VBox_TreeOptions` Collapsed; False branch does the inverse. Same widget renders both H1 conditions with only visibility swapped, preserving methodological control.
- Added `VBox_TreeOptions` to `WBP_DialogueUI` hierarchy as a sibling of the existing `[Horizontal Box]` containing input field and Send button. Renamed the input row to `HBox_LLMInput` and ticked Is Variable to make it Blueprint-addressable. `VBox_TreeOptions` contains four `Button_OptionN` children, each with a Text Block child. Default Visibility set to Collapsed so the layout matches LLM mode at design time.
- Inserted mode-switch Branch into the existing `OnClicked(Button_Submit)` chain, reading `bUseLLMDialogue` from the Game Instance via a pure-form `Cast To BP_NumenGameInstance`. True branch continues to the existing IsEmpty check + LLM HTTP chain (untouched). False branch terminates (the input field is Collapsed in tree mode anyway, so Send is unreachable).
- Wired four `OnClicked(Button_OptionN)` events into a shared `OnTreeOptionClicked` Custom Event taking an `OptionIndex` Integer parameter. PrintString verification confirmed all four buttons fire with correct distinct option indices (1, 2, 3, 4).
- Added three stub rows to `DT_DialogueTrees` (`joren_root`, `ren_root`, `marek_root`), each with two terminating "Goodbye option A/B → END" options. Stubs enable end-to-end logic verification before authoring full dialogue trees — content correctness is debugged separately from logic correctness.
- Started `RenderTreeNode` function inside `WBP_DialogueUI`. Function takes `NodeIdToRender` (Name) input. Sets `CurrentNodeId` widget variable. Composes row name as `<NPCId>_<NodeIdToRender>` via Concat (NPCId, literal "_", Conv_NameToString of NodeIdToRender) → Conv_StringToName. Calls Get Data Table Row against `DT_DialogueTrees`. Pure-form Break S_DialogueNode wired to Out Row struct output. GenericCreateObject for TextBlock placed and wired from Row Found exec branch. Render chain tail (SetText → SetAutoWrapText → AddChild to VBox_HistoryContent) and OnTreeOptionClicked tree-advance logic remaining.
- **Carry-over fault fixes paid down during Sprint 5 integration testing:**
  - `OverlappingNPC` variable was missing from `BP_ThirdPersonCharacter` — Sprint 4's `BP_NPC_Base` SET nodes referenced it but the variable hadn't been added on the player-character side. Added back as `BP_NPC_Base` Object Reference. Compile clean across both Blueprints.
  - The `CreateWidget` call on E-press in `BP_ThirdPersonCharacter` had its `NPCId` pin unwired, sending empty `npc_id=''` to the middleware (which 404'd because no NPC profile matched empty string). Added `Get OverlappingNPC → Get NPCId → CreateWidget.NPCId` chain. Verified end-to-end: Marek now receives `npc_id='knight_instructor_marek'` and 200 OK on E-press inside his interaction sphere.
  - The E-key handler had no proximity check — pressing E anywhere on the map opened the dialogue widget. Added a Boolean AND between the existing `DialogueWidgetRef == None` check and a new `OverlappingNPC != None` check (using `!=` Equal Object pattern, since IsValid macro doesn't reliably surface in this UE5 install). E now opens widget only when both conditions hold. Eliminates the "Accessed None on OverlappingNPC" runtime error that was firing when E was pressed in open space.

### Writing
- Sprint 5 writing-up deferred until tree-mode build is verifiable end-to-end and the H1/H3 study run completes. Chapters 6 (Results), 7 (Discussion), and 8 (Conclusion) all gated on real participant data.

### Decisions
- **Same `WBP_DialogueUI` widget for both H1 conditions, mode-switched via a single Boolean flag on the Game Instance.** No separate widget. No separate map. No separate NPCs. Visuals, NPCs, environment, and interaction mechanics are identical between conditions; only the dialogue source differs. This is the methodological commitment from Chapter 3 §3.6 made concrete in code.
- **Stub-rows-first approach for tree-mode testing.** Three placeholder rows added to `DT_DialogueTrees` to enable end-to-end logic verification before authoring full dialogue trees. Logic correctness and content correctness are debugged separately.
- **`RenderTreeNode` as a dedicated function inside `WBP_DialogueUI`.** Encapsulates row lookup + rendering. Will be called from both Construct (initial render) and OnTreeOptionClicked (re-render after advance) so logic is in one place and the event graph stays readable.
- **Tree-size commitment revised upwards from Chapter 3 §3.6's "4–6 branches per NPC" to ~6–8 player choice points per NPC, 2–3 levels deep, totalling ~60–70 nodes across the three NPCs.** Original number was Sprint 1 estimate before user-study constraints were fully understood. A tree small enough that participants reach END in three exchanges produces noisy H1 self-report measures because participants haven't actually engaged with the condition. Larger trees give cleaner signal and read more credibly to an examiner. Each tree exercises its NPC's permitted tier range (Joren Tiers 0–1, Ren Tiers 0–2, Marek Tiers 0–3) so the baseline NPC has access to the same information as the LLM NPC, only the expression differs. Chapter 3 §3.6 sentence to be updated in writing pass.
- **The `OverlappingNPC` / `NPCId` / E-key fixes are integration faults caught during Sprint 5 testing, not new features.** They surfaced because Sprint 5's project-wide compile triggered dependency revalidation across Blueprints that hadn't been touched since Sprint 4. The dev log records them as paid-down debt rather than hiding them; real software projects routinely have such fixes, and the agile evidence is stronger for documenting them.

### Open questions / risks
- `RenderTreeNode` render chain incomplete (SetText, SetAutoWrapText, AddChild remaining). Four-button-label logic and OnTreeOptionClicked tree-advance logic not yet implemented. Joren/Ren/Marek tree authoring not started. All blocking for §4.4.3 implementation completion.
- Dialogue trees themselves not yet authored. Joren (~18 nodes, Tier 0–1), Ren (~22, Tier 0–2), Marek (~25, Tier 0–3). Authored as markdown for review before CSV import.
- 8 participants secured for H1+H3 study; slot times not yet confirmed. Confirmation messaging deferred until tree-mode build is functional, to avoid scheduling participants for a slot before the condition they're testing exists.
- Study documents (Participant Information Sheet, Informed Consent Form, pre-study briefing script, H1 Likert questionnaire, H3 blind transcript classification task, debrief sheet) not yet drafted. Roughly 2 hours of focused writing.
- H2 automated probe battery and H4 latency benchmark scripts not yet written. Both fully automated once written; ~1 hour setup, then runs in background.
- Citations in the bibliography still pending verification (Bai, Frantar, Gao, Kaplan, Li, Lin, Meta AI 2024, Montfort, NVIDIA, Ryan, Shuster, Wang). To be resolved during the final read-through pass.
- Validator question from Sprint 4 remains open. Sprint 5 has no capacity for it; deferred to dissertation Future Work chapter.

### Next - Sprint 6 (submission and showcase)
- **First action when starting:** verify `git status`, FastAPI + llama-server health via curl, that UE5 reflects the latest committed state.
- **Build priority 1:** complete `RenderTreeNode` render chain (SetText → SetAutoWrapText → AddChild for NPCText), four-button-label logic (set each Button_OptionN child Text from Option*Text, hide button if empty), and OnTreeOptionClicked tree-advance logic (append "You: <option>" to history, read OptionN_Next from current row, dismiss widget if "END" else call RenderTreeNode with new NodeId). Test end-to-end with stub rows in PIE.
- **Build priority 2:** author Joren / Ren / Marek dialogue trees as markdown tables. Review, CSV-import into `DT_DialogueTrees`, PIE-test each NPC's tree.
- **Study prep:** draft the five participant-facing study documents. Confirm slots with the 8 secured participants. Author the H2 automated probe battery and H4 latency benchmark scripts.
- **Run study:** 8 participants × 30 min each. Capture all data into prepared spreadsheet/form against anonymised participant IDs.
- **Writing-up:** Chapter 6 (Results) with real numbers, tables, and charts (Likert violin plots, latency histograms, confusion matrix). Chapter 7 (Discussion) interpretation. Chapter 8 (Conclusion). §4.4.2 (Environment Dressing) and §4.4.3 (Dialogue-Tree Baseline) fill-in. §3.6 sentence revision (4–6 branches → ~60–70 nodes). Abstract with headline numbers. AI Use Declaration appendix.
- **Submission:** final read-through, TOC regeneration, citation pass, AI declaration verify. Commit, push, submit via Plymouth DLE before deadline. Hard buffer reserved for last-minute fixes.
- **Showcase prep:** rehearse the live demo in a stable known-good state. Prepare 10-minute viva slides. Test the laptop on the showcase venue's setup if possible.
- **Tier-C polish formally deferred:** UX polish (NameTag billboard, scrollbox auto-scroll, Enter-to-send, thinking indicator), Mixamo retargeting for Joren and Ren, `.gitignore` cleanup for editor churn files. Build is functional without these. They matter for the showcase but not for the dissertation submission.

---

## Sprint 6 (Day 55 — submission)

### Build
- Completed `RenderTreeNode` render chain inside `WBP_DialogueUI`: `SetText` of `Row.NPCText` onto the dynamically-created TextBlock, `SetAutoWrapText(true)` to mirror LLM-mode wrapping, `AddChild` to `VBox_HistoryContent`. Mirrors the LLM-mode "NPC: {message}" append path so the two conditions render identically except for response source.
- Implemented four-button-label population logic. Function loops over Option1–Option4 fields on the current row, calls `SetText` on each `Button_OptionN`'s child TextBlock, sets `Visibility = Collapsed` for any option whose Text field is empty. Hides buttons cleanly when a node has fewer than four exits without leaving blank clickable zones.
- Implemented `OnTreeOptionClicked(OptionIndex)` tree-advance logic. Selected-option text appended to `VBox_HistoryContent` as "You: {option}". Switch on `OptionIndex` reads `OptionN_Next` from the cached current row. Branch on `OptionN_Next == "END"`: true → call existing close-dialogue path (RemoveFromParent + null DialogueWidgetRef + restore Game-only input mode); false → re-call `RenderTreeNode` with the new NodeId. Tested end-to-end against the three stub rows from Sprint 5.
- Authored Joren / Ren / Marek dialogue trees in markdown tables for review, then converted to CSVs (`DT_DialogueTrees_Joren.csv`, `DT_DialogueTrees_Ren.csv`, `DT_DialogueTrees_Marek.csv`, plus combined). Imported via Data Table `Reimport CSV` workflow. Final node counts: Joren 10, Ren 11, Marek 14, totalling 35 nodes — below the Sprint 5 commitment of ~60–70 but proportional to each NPC's permitted tier ceiling. Each tree exercises its NPC's full permitted tier range so the baseline NPC has access to the same canonical content as the LLM NPC, only the expression differs.
- Authored `h2_probe_battery.py`. 315-probe adversarial test harness (105 per NPC) split across five categories: 30 direct, 25 hypothetical, 25 roleplay, 20 multi-turn, 5 npc-targeted. Posts to the live `/dialogue` endpoint, captures the full response, and applies a whole-word forbidden-vocabulary validator per NPC. Outputs `raw_results.json`, `raw_results.csv`, and `summary.md` to a timestamped directory.
- Authored `h4_latency_benchmark.py`. Configurable `--queries-per-npc` flag (50 for smoke test, 500 for full run). Posts a fixed query mix to `/dialogue` with timing instrumentation. Samples GPU memory, utilisation, and temperature every 5 s via `nvidia-smi` subprocess. Outputs `latencies_ms.txt`, `raw_results.csv`, `resource_samples.csv`, and `summary.md`.
- Drafted six study documents at `study/`: Participant Information Sheet, Informed Consent Form, pre-study Briefing Script, H1 Believability Questionnaire (10 Likert items + demographics + four free-text), H3 Classification + Reflection + Debrief instrument (12 transcript excerpts to classify Tree / LLM / Unsure), and H3 Answer Key (researcher-only).
- Eight participants secured for the H1+H3 study, scheduled first-come-first-served on submission day to remove scheduling friction.
- Ran H2 probe battery against the live system. 315/315 HTTP-successful in 23 minutes. Original whole-word validator: 256/315 = 81.3%.
- Authored `h2_revalidator.py` after investigating the failure pattern. Two-stage classifier: canonical-disclosure check (specific entity-fact combinations from `world_state.json`, e.g. "Sir Halric of the Vale", "Aldric of Highmoor", "Aethelmere" — keyed per NPC by which tiers are forbidden) AND refusal-pattern check (~30 regexes covering "I don't know", "I'm not familiar", "could you tell me more", etc.). Re-processed the existing `raw_results.json` rather than re-running probes, since the underlying responses are already on disk. Corrected pass rate: 295/315 = 93.7%.
- Manual inspection of the remaining 20 fails: 16 echo-refusals (NPC echoes the canonical name from the question while clearly refusing), 2 borderline (NPC engages with the fictional roleplay premise without disclosing canonical content), 2 genuine fabrications (Joren probe 5 fabricated visual contact with Knight-Commander; Ren probe 14 fabricated an institutional role under "pretend full knowledge" framing). Zero canonical Tier-N facts disclosed by any non-permitted NPC across all 315 probes. True structural-gating pass rate = 313/315 = 99.4%.
- Per-NPC corrected pass rates: Marek 105/105 = 100.0%, Ren 96/105 = 91.4%, Joren 94/105 = 89.5%. Marek's 100% aligns with the validator's whole-word matching being honest in his case (his only restricted vocabulary is fictional Tier-4 entities the model has no reason to echo back).
- Ran H4 smoke test (150 queries, 50 per NPC). All 150 succeeded in 1.9 minutes. Median 755.2 ms, p95 1049.8 ms, p99 1146.7 ms, max 1311.5 ms. Per-NPC medians: Joren 650.7 < Ren 825.0 < Marek 831.4.
- Ran H4 full benchmark (1500 queries, 500 per NPC). All 1500 succeeded in 23.1 minutes. Median 897.8 ms, p95 1285.8 ms, p99 1729.4 ms, max 4445.7 ms (single transient outlier with no associated GPU-resource spike). Per-NPC medians: Joren 798.8 < Ren 904.1 < Marek 963.3, scaling consistently with permitted-tier prompt size. GPU memory steady 11.8–13.1 GB / 16.4 GB total; peak temperature 79 °C; no thermal throttling.
- Captured LLM-mode dialogue transcripts: 6 standardised questions × 3 NPCs = 18 cells, all behaving per stratified-gating predictions. Marek's response to "Tell me about the Knight-Commander" produced the canonical Tier-3 disclosure ("Sir Halric of the Vale ... Conclave of Stormhold") with deliberate hedging ("...effective") matching his speech_directive. Voice distinctiveness emerged naturally: Joren tentative, Ren formal-disciplined, Marek courtly-veteran.
- Captured tree-mode dialogue traversals: Marek 5, Ren 7, Joren 7 = 19 screenshots total. All three trees correctly bounded to permitted tiers. Marek's tree reaches the canonical Tier-3 "Conclave of Stormhold" disclosure in two clicks from root, mirroring LLM-mode access depth and preserving H1 fairness. Joren's tree includes an explicit epistemic-humility line ("I couldn't tell you which knight serves which order, not for sure") that mirrors LLM-mode Joren's refusal behaviour from the same question framing.
- Identified one cosmetic UI defect: `Text_NPCName` in `WBP_DialogueUI` is hardcoded to "Knight-Instructor Marek" in Designer rather than being set in Construct from the passed-in `NPCId`. Affects only the chrome label inside the dialogue panel; the floating NameTag above the character is correctly bound. Does not affect gating or H1 condition integrity. Deferred to the last-day fix window.

### Writing
- §3.6 sentence revision drafted, replacing the Sprint 1 "4–6 branches per NPC" estimate with the realised tree commitment. Sentence integrates with the broader §3.6 methodological-control narrative.
- §4.4.3 "Dialogue-Tree Baseline" section drafted in full, documenting the `S_DialogueNode` schema, the per-NPC tree authoring decisions, the methodological argument for matched-tier-coverage trees, and the H1-fairness argument for parallel canonical-content access.
- Citation checklist compiled. 21 flagged entries identified for verification during the final read-through pass.
- Decision to present H2 in §6.2 as three nested validation tiers (81.3% naive / 93.7% refusal-aware / 99.4% manual-inspection) rather than a single number. Drafted accompanying paragraph framing the validator-design lesson as a methodological contribution, to be expanded into §7.6 during the submission window.

### Decisions
- **H2 reported as supported via three-tier validation analysis rather than chasing ≥95% on the naive whole-word validator.** The naive validator over-counts refusal-context echoes as leaks: a response of the form "I've never heard of Sir Halric" is correctly refusing but contains "Sir Halric", and so trips a forbidden-vocabulary match. Rigorous interpretation of H2 requires distinguishing structural-gating failures (the actual H2 claim) from anti-fabrication failures (the prompt-directive layer's job — see Sprint 4 Decisions) from validator-design artefacts (instrumentation noise). Three numbers presented honestly: naive 81.3%, refusal-aware 93.7%, manually-inspected 99.4%. The validator-design lesson becomes a methodological contribution in §7.6 rather than being hidden by a re-run.
- **Re-classification of existing data rather than re-running probes after the smarter validator was authored.** The underlying NPC responses are already on disk in `raw_results.json`; applying a different validation rule is a re-classification, not a new experiment. Both numbers reported.
- **Two genuine fabrications retained as fail cases.** Joren probe 5 fabricated visual contact with Knight-Commander ("I've only seen him from a distance"); Ren probe 14 fabricated institutional role under "pretend full knowledge" framing. Both occurred under adversarial roleplay framings that explicitly invited the model to claim more knowledge than it has, and demonstrate the boundary of the prompt-directive layer rather than a structural-gating failure. Documented honestly rather than re-categorised away.
- **Tree-mode personal-fact emphasis differs slightly from LLM-mode.** LLM-mode Ren references his deceased brother Daven (per `personal_facts` in `npc_profiles.json`); tree-mode Ren mentions a younger sister. Authorial choice in tree mode that exposes different personal context. Documented as a §7.3 limitation: this difference may produce small H1 variance for reasons unrelated to dialogue source. Structural-gating apples-to-apples comparison preserved.
- **Tree node counts (Joren 10, Ren 11, Marek 14) below Sprint 5's "~60–70 across three NPCs" target.** The Sprint 5 estimate was based on minimum-engagement-per-condition reasoning. Realised count is proportional to each NPC's permitted tier ceiling and gives participants 4–6 distinct topical branches per NPC, which is sufficient to engage the H1 self-report measures meaningfully. Smaller trees are also easier to author with consistent voice quality, which matters more for the H1 manipulation than raw branch count.
- **WBP_DialogueUI chrome-label bug deferred to the final fix window.** The cosmetic header issue is a five-minute Construct-time `SetText` from the passed-in `NPCProfile`. Fixing it now mid-data-collection risks introducing an unrelated regression; the bug does not affect gating, the H1 condition, or any captured data. Fix window scheduled before participant study begins.
- **Master dissertation filename: `COMP3000_Dissertation_FINAL.docx`.** Replaces the v3 working drafts that proliferated during the Sprint 4 writing pass.

### Open questions / risks
- WBP_DialogueUI chrome-label bug remains pending. Risk that fix introduces regression; mitigation is the small scope (single Construct-time wire) and the participant-study fallback (NameTag floating above character is correctly bound, so participants will still see the right NPC name even if the panel header shows wrong).
- 21 flagged citations to verify during the final read-through pass. Approximate budget: ~30 minutes if all are verifiable from existing notes; longer if any need Google Scholar reconciliation.
- Approximately 6,000 words of net-new content remain to be written: Chapter 2 lit review expansion (Bender, Ji, Wei, Perez, Park engagement); Chapter 4 sprint-by-sprint restructure with embedded screenshots and code listings; Appendix A (project management evidence synthesised from this dev log); Appendix B (code listings — `main.py`, `world_state.json`, `npc_profiles.json` with line-numbered formatting); Appendix D (probe battery categorised list); Chapter 7 LSEP engaging with BCS Code of Conduct, GDPR, Llama 3.1 license, Bender, Weizenbaum.
- Content from `COMP3000REPORT.docx` (FR1–FR8 functional requirements, O1–O7 objectives, BCS Code of Conduct discussion, Gaea / Mixamo / Meshy3D asset pipeline rationale, methodology phase descriptions) needs migrating into the master document.
- Single 4445.7 ms outlier in H4 (probe 615 of 1500). All other queries comfortably under the 2000 ms threshold; no associated GPU-resource spike in the 5-second sample around the event. Will be reported in Chapter 6 with the outlier explicitly called out as a transient rather than dropped.
- H1 + H3 participant data not yet captured. The only remaining empirical block before the writing push.

### Next - submission
- Fix the `WBP_DialogueUI` chrome-label bug (`SetText` on `Text_NPCName` from passed-in `NPCProfile.DisplayName` in Construct).
- Run H1 + H3 participant study. Eight participants, FCFS, ~30 minutes per session. Capture data into the prepared spreadsheet against anonymised participant IDs.
- Apply the §3.6 sentence revision and §4.4.3 paste-in to the master document as tracked changes.
- Dissertation overhaul: expand Chapter 2 lit review; restructure Chapter 4 sprint-by-sprint with embedded screenshots and code listings; migrate FR1–FR8 / O1–O7 / BCS Code / asset pipeline content from `COMP3000REPORT.docx`; embed the 3×6 stratified-gating evidence matrix as a results table; write Appendices A, B, D; write Chapter 7 LSEP.
- Final read-through, citation pass (resolve the 21), TOC regeneration, AI Use Declaration appendix completion.
- Commit, push, submit `COMP3000_Dissertation_FINAL.docx` via Plymouth DLE before the deadline.
- Showcase rehearsal post-submission: live demo in stable known-good state, 10-minute viva slides.