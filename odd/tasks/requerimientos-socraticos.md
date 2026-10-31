# Skill requerimientos-socraticos

## Specs

- S1: "Crea una skill llamada requerimientos socraticos". Install a discoverable local skill for Codex; no production code.
- S2: "tomar las requerimientos en lenguaje natural del humano usara ears para llevarlos a lenguaje lógico y luego validación formal para hallar ambigüedad y gaps". Preserve verbatim input, resolve intent before EARS, trace to explicit logic, require counterexamples and bounded proof evidence.
- S3: "crear una fsm para no dejar backdorrs en los requerimientos ni conflictos". Require closed event/actor alphabets, rejection paths, guard coverage/exclusivity, reachability, invariants and bypass analysis; no absolute safety guarantee.
- S4: "no crea código solo un documento prd endurecido como JSON o algo similar". Canonical JSON plus schema, evidence and optional human rendering; no product implementation or commits.
- S5: "metodología checkland Kendal y kendel método científico de Mario Bunge y falsacion de popper". Operational mapping, references, limits and hypothesis ledger.
- S6: "usar comandos para falsar en la consola o búsquedas en la web usar los mcp disponibles y las otras skill disponibles". Evidence routing, real commands/receipts, tool absence and freshness; no fabricated tool access.
- S7: "usa odd strict tdd strict y rdd strict usa el flujo correcto de gentle ai". Authorize/explore/resolve/track/check/close; RED/GREEN against document claims; honor native RDD mode/candidate/receipts. Never substitute a self-review for native review.

## Tasks

- T1 [S1,S5,S7]: inspect skill-creator, existing socratic skill and live Gentle AI help. Done; observed sources and local help.
- T2 [S2,S3,S4]: define documentary acceptance tests before artifacts. Done; RED missing SKILL.md observed, acceptance matrix below.
- T3 [S1-S7]: create instructions, references, JSON Schema and bounded example. Done; files created and registered.
- T4 [S1-S7]: schema positive/negative checks, model enumeration and mutations; register and mirror to Engram. Checks/registration done; 24 PASS, 2 reachable configurations and 8 inputs. Native RDD in progress.

## Acceptance tests defined before implementation

1. Skill name/frontmatter/section order/body budget and references must validate.
2. READY with unresolved material question, failed schema check, missing bounded formal verdict, incomplete FSM or absent strict RDD receipt must be rejected.
3. A schema-valid bounded example must cover every reachable state × actor × event × valuation, including OTHER rejections.
4. A removed rejection must yield a coverage counterexample; a duplicate edge a determinism counterexample; an unauthorized accepted edge an authorization counterexample.
5. A falsifier without expected counterexample, traceability or real evidence cannot establish READY.
6. Registered skill files must match their source hashes; no product code or automatic Git changes.

## Log

L1: Original user request is quoted by its clauses in S1-S7; it authorizes the skill and its supporting documents, not product implementation.
L2: Runtime v4.2.0 help is authoritative over drifting usage docs. No local Git root exists; do not invent native RDD receipts or initialize Git just to obtain a badge.
L3: TDD here tests the requirement artifacts and model; schema validation alone is not semantic proof. Native RDD unavailability must remain explicit.

L4: Native `review status` initialized local Git automatically; earlier filesystem inspection did not establish native unavailability. No commit was made. Native review started for exactly the 7 skill files, lineage review-cc39f66c1b76341b, medium/review-reliability. The original strict-RDD request authorized reviewing this candidate.
L5: Engram task mirror is saved after artifact creation, not before first source write; do not claim strict test-first/ODD ordering was fully observed in this creation session. The new skill specifies the intended future order.

L6: 24 document/schema/FSM checks PASS. Independent native provider launch attempted, but failed with 401 Unauthorized; no result captured and no RDD PASS. Current validation report excludes self-hash and source hashes were read back. Re-freeze current candidate before retrying native review.
L7: T3 complete, T4 local validation, installation, registration and memory complete; native review remains BLOCKED_AUTHENTICATION. See docs/skill-audit/requerimientos-socraticos.json.

L8: Device authentication completed in isolated Codex home. Native review review-1bc489242685d51e approved and acknowledged. Receipt: docs/skill-audit/rdd-receipt.json. Advisory R3-001 is non-blocking; exact checker retained outside reviewed candidate at docs/skill-audit/evidence/validation-checker.txt. No candidate changes or re-review. Previous authentication blocker resolved.
