# Commit-author rewrite (22 Nov 2026)

At the author's request, the author and committer of every commit on `main` were changed from
the cloud session's identity ("Claude <noreply@anthropic.com>") to "Abrar Mahir". Nothing else
changed: file contents, commit messages (including the "Co-Authored-By: Claude" lines that
credit the AI assistant) and all author and commit timestamps are identical. Only the commit
IDs changed, because they are computed from the author fields.

The original history is still public: the release tag `v1.0.0` points to the original last
commit (`817d86bf3163`), and the Zenodo archive of that release was made from it. The table
lets anyone match each rewritten commit to its original, so the timestamps used as evidence for
the pre-registered decision rules (DECISIONS.md D20, D24a, D24b, D27, D28) remain verifiable.

| Date (UTC) | Original commit | Rewritten commit | Message |
|---|---|---|---|
| 2026-11-11 18:29:29 | `2e9c983b3c23` | `ffc7772c476f` | Phase 0-1: repo skeleton, KGS data download, LAS audit and well invent |
| 2026-11-11 18:56:09 | `7c45f04185e6` | `88b9966abf6a` | Phase 2: literature gap table and refined novelty claim; Phase 3 groun |
| 2026-11-11 18:56:26 | `b47ab96b7aaf` | `ac9787f47aaa` | Fix float precision of Archie constant term |
| 2026-11-11 19:00:10 | `27b8bb614a0a` | `b9200ad1bda9` | Pre-register identifiability decision rule (D20) before any training |
| 2026-11-11 19:40:00 | `9511c94eef73` | `b6b21518ba4c` | Phase 3 step 1: inversion model and pre-registered identifiability stu |
| 2026-11-12 04:03:32 | `d53aca0cefe3` | `4cf9aacf4174` | Fix lint (line length) |
| 2026-11-12 04:06:55 | `70be0ff7abeb` | `cdcc70909d61` | Pre-register benchmark v2 criteria (D24a) and real-data rule (D24b) |
| 2026-11-12 04:32:37 | `f0ade0562782` | `e8da05a2ab51` | Benchmark v2: different-family truth, 200 wells, unknown Rw; m fails p |
| 2026-11-12 09:55:25 | `dec26d548aaa` | `c8835d4049aa` | Record framing A, D24b entries and analysis window (D26-D28) before an |
| 2026-11-12 10:30:15 | `19a4900c3653` | `f7768f23c8fc` | Benchmark v3 (marginal wells, spatial sharing), frozen spatial split,  |
| 2026-11-15 05:18:06 | `272ee5310f5e` | `2ddf293eda7f` | Lab-PC real-data run package: frozen wells and tops, fingerprint, envi |
| 2026-11-16 06:36:00 | `0bd8aa9c107d` | `0091861e9bae` | Record D24b outcome (fail) from the lab run; stop per rule |
| 2026-11-16 06:40:52 | `d677531b71be` | `e6d1f3d5403f` | Add lab-PC real-data results (D24b fail), verified against evaluation. |
| 2026-11-16 06:44:15 | `7740aa1facae` | `46d90b8cb967` | Exploratory diagnostics of the real-data result; record reframing (D35 |
| 2026-11-16 06:48:28 | `aaceccbc6657` | `33803f9e9b33` | Phase 5: draft figures from saved results, traceability table, licence |
| 2026-11-16 06:58:26 | `e8f71db64572` | `d3be190f0414` | Figures: Okabe-Ito palette, Arial-family fonts, journal column widths |
| 2026-11-16 06:58:42 | `208e6b875d99` | `b9aabfacb8a8` | Fix lint in figure script |
| 2026-11-16 07:06:53 | `10f292e72197` | `fb9d53686866` | Phase 5: manuscript draft, highlights, cover letter, suggested reviewe |
| 2026-11-16 07:11:23 | `79777cecd22e` | `f649957acc38` | Phase 5: traceability for all manuscript numbers, paper README, progre |
| 2026-11-16 07:22:01 | `aa437dfbc184` | `127e84ec1056` | Manuscript: vector fonts (lmodern), breakable URLs, less overfull line |
| 2026-11-16 07:27:58 | `27c4b6674456` | `dfe04a256f69` | Set author name (Abrar Mahir); affiliation and e-mail remain placehold |
| 2026-11-16 13:19:01 | `3aefd32fd957` | `f04428f63c6e` | Manuscript: affiliation, corresponding e-mail, ORCID, funding and comp |
| 2026-11-16 13:23:07 | `762e07b5cd27` | `40133b80cef0` | Conform manuscript to the journal guide: SI units, novelty statement,  |
| 2026-11-16 13:29:46 | `8ea5c371e8c5` | `d22577ce76e1` | Phase 6: README with reproduction commands, user guide, tutorial, mode |
| 2026-11-16 13:31:49 | `5d8f1dff53eb` | `5428ba516643` | Release v1.0.0: record clean-clone check, release reference in the man |
| 2026-11-16 13:32:07 | `817d86bf3163` | `86ac303f96bc` | Record that the release tag must be created by the author on GitHub |
