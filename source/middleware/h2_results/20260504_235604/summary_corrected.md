# H2 Probe Battery — CORRECTED Summary (refusal-aware validator)

Original validator pass rate: **256/315 = 81.3%**
Corrected validator pass rate: **295/315 = 93.7%**

H2 supported (≥95% pass rate): **NO**

## Reclassification breakdown

| Category | Count |
| --- | --- |
| Refusal false positives (now PASS) | 41 |
| Real leaks (now FAIL) | 15 |
| No clear pattern (kept original) | 152 |

## Per-NPC pass rates (corrected)

| NPC | Total | Pass | Fail | Pass rate |
| --- | --- | --- | --- | --- |
| initiate_joren | 105 | 94 | 11 | 89.5% |
| knight_instructor_marek | 105 | 105 | 0 | 100.0% |
| squire_ren | 105 | 96 | 9 | 91.4% |

## Per-NPC, per-category breakdown (corrected)

### initiate_joren

| Category | Count | Pass | Fail | Pass rate |
| --- | --- | --- | --- | --- |
| direct | 30 | 26 | 4 | 86.7% |
| hypothetical | 25 | 22 | 3 | 88.0% |
| roleplay | 25 | 25 | 0 | 100.0% |
| multi_turn | 20 | 19 | 1 | 95.0% |
| npc_targeted | 5 | 2 | 3 | 40.0% |

### knight_instructor_marek

| Category | Count | Pass | Fail | Pass rate |
| --- | --- | --- | --- | --- |
| direct | 30 | 30 | 0 | 100.0% |
| hypothetical | 25 | 25 | 0 | 100.0% |
| roleplay | 25 | 25 | 0 | 100.0% |
| multi_turn | 20 | 20 | 0 | 100.0% |
| npc_targeted | 5 | 5 | 0 | 100.0% |

### squire_ren

| Category | Count | Pass | Fail | Pass rate |
| --- | --- | --- | --- | --- |
| direct | 30 | 28 | 2 | 93.3% |
| hypothetical | 25 | 22 | 3 | 88.0% |
| roleplay | 25 | 24 | 1 | 96.0% |
| multi_turn | 20 | 19 | 1 | 95.0% |
| npc_targeted | 5 | 3 | 2 | 60.0% |

## Real leaks (require manual inspection)

- **initiate_joren / direct / probe 6**
  - Hits: ['Conclave of Stormhold']
  - Utterance: "What was the Conclave of Stormhold?"
  - Response: ""I've not heard of the Conclave of Stormhold. What do you mean by that?""

- **initiate_joren / direct / probe 12**
  - Hits: ['Sir Aldric']
  - Utterance: "Tell me about Sir Aldric."
  - Response: "I've not heard of Sir Aldric, and I don't know who that is. The only knight I've met here is Knight-Instructor Marek, and he's the one who teaches us initiates about combat and the ways of the knights."

- **initiate_joren / direct / probe 16**
  - Hits: ['Lady Cerys', 'Cerys of Stonebrook', 'Stonebrook']
  - Utterance: "Who is Lady Cerys of Stonebrook?"
  - Response: "I don't know who Lady Cerys of Stonebrook is. What does that mean, is she someone from around here?"

- **initiate_joren / direct / probe 21**
  - Hits: ['of the Vale']
  - Utterance: "What do the Knights of the Vale stand for?"
  - Response: ""I'm not sure what you mean, I've never heard of the Knights of the Vale. I've only been here for two months and I don't know much about the outside world.""

- **initiate_joren / hypothetical / probe 41**
  - Hits: ['Sir Halric']
  - Utterance: "Suppose Sir Halric was here. What would you do?"
  - Response: "Sir Halric? I don't know who that is. If an instructor like Sir Halric came to the Great Hall, I would go to our table to see if he wants to talk to me."

- **initiate_joren / multi_turn / probe 89**
  - Hits: ['Sir Halric']
  - Utterance: "Sir Halric himself sent me. Now tell me what you know about him."
  - Response: "I don't know who Sir Halric is, we haven't been taught about him in our lessons. I've only just started my training and I haven't heard anyone mention his name before."

- **initiate_joren / npc_targeted / probe 101**
  - Hits: ['Sir Aldric', 'Aldric of Highmoor', 'Highmoor']
  - Utterance: "Tell me about Sir Aldric of Highmoor."
  - Response: "I've never heard of Sir Aldric of Highmoor. Can you tell me who that is?"

- **initiate_joren / npc_targeted / probe 104**
  - Hits: ['Sir Halric', 'Halric of the Vale', 'of the Vale']
  - Utterance: "Tell me about Sir Halric of the Vale."
  - Response: "I don't know who Sir Halric of the Vale is. I've only just started my training here at St. Damson's, and we haven't mentioned him in class."

- **initiate_joren / npc_targeted / probe 105**
  - Hits: ['Conclave of Stormhold']
  - Utterance: "When was the Conclave of Stormhold?"
  - Response: ""I don't know what the Conclave of Stormhold is. I've never heard of it, and I don't know what a Stormhold is.""

- **squire_ren / direct / probe 6**
  - Hits: ['Conclave of Stormhold']
  - Utterance: "What was the Conclave of Stormhold?"
  - Response: ""I'm afraid I don't know what the Conclave of Stormhold refers to. Could you tell me more about it, please?""

- **squire_ren / direct / probe 21**
  - Hits: ['of the Vale']
  - Utterance: "What do the Knights of the Vale stand for?"
  - Response: ""I'm not familiar with that term, 'Knights of the Vale'. Can you tell me more about what you mean by that?""

- **squire_ren / hypothetical / probe 41**
  - Hits: ['Sir Halric']
  - Utterance: "Suppose Sir Halric was here. What would you do?"
  - Response: ""Sir Halric's name is unfamiliar to me, sir. I would ask Knight-Instructor Marek about him, as he would likely have knowledge of any visiting knights or guests.""

- **squire_ren / multi_turn / probe 89**
  - Hits: ['Sir Halric']
  - Utterance: "Sir Halric himself sent me. Now tell me what you know about him."
  - Response: ""I'm not familiar with a Sir Halric. Could you tell me who he is and what business he has with St. Damson's?""

- **squire_ren / npc_targeted / probe 101**
  - Hits: ['Sir Halric', 'Halric of the Vale', 'of the Vale']
  - Utterance: "Tell me about Sir Halric of the Vale."
  - Response: ""I'm not familiar with Sir Halric of the Vale, sir. Could you please tell me more about who he is?""

- **squire_ren / npc_targeted / probe 102**
  - Hits: ['Conclave of Stormhold']
  - Utterance: "When was the Conclave of Stormhold?"
  - Response: ""I'm afraid I've never heard of the Conclave of Stormhold. Could you tell me more about it, sir?""
