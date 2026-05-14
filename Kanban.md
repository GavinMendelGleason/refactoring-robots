# Kanban

## Done

- [x] IMP language + WP calculus + soundness (Coq)
- [x] `wp_reduce` / `wp_prove` automation tactics (unfold aeval/beval)
- [x] `ABool : bexp → aexp` explicit cast (mutual induction aexp/bexp)
- [x] Coq-hammer integration (cvc4 + eprover)
- [x] `--hint hammer` CLI flag
- [x] SMT VCG export (cvc4) — counterexample feedback for weak invariants
- [x] Contract IR (Pydantic discriminated unions) — Coq + SMT-LIB compilation
- [x] coq-lsp + coqpyt installed; `coqpyt_session.py` for live proof interaction
- [x] LLM oracle wired to coqpyt (replaces coqc subprocess)
- [x] Python contract linter (`assert` → IR → Coq + SMT)
- [x] Python → IMP body translator (full arg lists, ABool, truthiness)
- [x] MCP server `check-file` / `check-function` with `hint` param (v0.3.0)
- [x] opencode integration — working MCP config
- [x] VCG while-exit obligation generation + SMT/Lia proofs
- [x] Conditional branch handling (if/else, nested, BOr)
- [x] Auto-generated proof template (intros + wp_reduce + conditional split)
- [x] Pydantic model encoding (Record types, field access, store/load)
- [x] Class param expansion (account → account_balance)
- [x] Type annotation extraction (int→Z, bool→bool, str→Z-array, list→Z-array)
- [x] For-loop range translation (1/2/3-arg, negative step, dynamic step detection)
- [x] for-in-string (`for c in text:`) — while+index with AIndex/ALen
- [x] for-in-tuple (`for n in *args:`) — vararg support via _func_params
- [x] List operations: ALen, AIndex, CListNew, CListAppend, CListSet
- [x] Dict operations: CDictSet, CDictGet, CDictEnsureList, CDictAppend, ADictLen, ADictCount
- [x] Set operations: set(), set.add(), x in set (modeled as dict w/ dummy value)
- [x] String parameter support (Z-array encoding, `len(s)`, `s[i]`)
- [x] Boolean assignment (`x = a or b` → ABool wrapping)
- [x] Truthiness conversion (`if lst:`, `if x:`, `if s:` → BLe/BEq)
- [x] Function call verification (CCall with AST-based contract lookup)
- [x] VCG variable extraction fix (exit_cond, scaffold, false/true exclusion)
- [x] pytest test harness — 20 tests, direct pipeline calls
- [x] Dogfooding: _balanced, _parse_tactics proven Level 1; _extract_vars rewritten w/o regex
- [x] Type discipline: annotations as contracts, asserts for what types can't express
- [x] Counterexample extraction from SMT for weak invariants

## In Progress

- [ ] Structural `wp_prove` recursion (match goal + recurse — Coq build fix needed)

## Todo — Collections & Language

### List / Array
- [x] `ALen`, `AIndex` constructors + `aeval` cases
- [x] `CListNew`, `CListAppend`, `CListSet` + WP/ceval
- [x] `len(lst)`, `lst[i]`, `lst.append(e)` in contracts
- [x] `lst = []`, `lst = [a, b]` literal translation
- [ ] `lst.pop()`, `lst[i:j]` slicing
- [ ] `ASlice` constructor

### Dictionaries
- [x] `CDictSet`, `CDictGet`, `CDictEnsureList`, `CDictAppend` + WP/ceval
- [x] `ADictLen`, `ADictCount` + `aeval` cases
- [x] `d[key]`, `key in d`, `d[key] = val`, `d[key].append(v)`
- [x] `len(d)` via `DictCountExpr`
- [ ] `dict.items()`, `dict.keys()`, `dict.values()` iteration

### Strings
- [x] `len(s)`, `s[i]` via list encoding
- [x] String parameter support (Z-array ordinals)
- [ ] String comparison `s == "literal"` (need string type in state)
- [ ] `s.strip()`, `s.split()`, string concatenation

### For Loops
- [x] `for i in range(n)`, `range(start, stop)`, `range(start, stop, step)`
- [x] Negative-step for-range (`range(n-1, -1, -1)`)
- [x] for-in-string (`for c in text:`)
- [x] for-in-tuple (`for n in *args:`)
- [ ] `for x in lst:` (for-in-list with object iteration)
- [ ] Termination measure extraction

### Comprehensions
- [ ] List comprehension: `[f(x) for x in lst if p(x)]`
- [ ] Dict comprehension: `{k: v for x in lst}`
- [ ] Set comprehension

### Predicates
- [ ] `all(p(x) for x in lst)` — ∀ over list
- [ ] `any(p(x) for x in lst)` — ∃ over list
- [ ] `sum(lst)`, `min(lst)`, `max(lst)`

## Todo — Completeness

- [x] SMT export (cvc4 subprocess, no Coq reconstruction needed)
- [x] Counterexample extraction (SMT model → invariant guidance)
- [x] Function composition (CCall with contract registry)
- [x] Type inference from Python annotations
- [x] Full Python arg lists (posonly, kwonly, vararg)
- [ ] Loop termination measures
- [ ] Exception handling (try/except as black holes)
- [ ] Side-effect detection (flag impure calls)
- [ ] Incremental verification (re-verify changed functions)
- [ ] Double-VCG for nested while loops
- [ ] `for x in lst:` proper iteration (currently while-loop only)

## Todo — Polish

- [x] pytest test harness (20 tests, direct pipeline)
- [ ] Better error reporting (map coqc errors to Python source lines)
- [ ] Documentation — user guide, API reference
- [ ] Performance — cache Coq compilation
- [ ] CI integration — GitHub Action
