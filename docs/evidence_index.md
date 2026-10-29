# JPetStore Modernization: Evidence Index

This index maps each assessment evaluation area to the artifact that supports it and how to check it.

| Evaluation area | Evidence | How to verify |
| :-- | :-- | :-- |
| Architecture analysis | docs/jpetstore_architecture_decomposition.md | Compare component tables and data dictionary with the legacy source |
| Context building | docs/jpetstore_architecture_decomposition.md, docs/migration_issue_log.md | Decomposition used as the baseline for each milestone; issue log records corrections |
| Specification creation | docs/jpetstore_migration_proposal_and_roadmap.md, docs/modernization_deviations_and_rationales.md | Roadmap defines scope per milestone; deviations list every intentional change |
| Architectural decisions | docs/architecture_decision_records.md (ADR-001 to ADR-009) | Each ADR lists options, decision and trade-offs |
| AI guardrails | docs/ai_guardrails_and_verification.md, pyproject.toml | Run the commands in section 4 of the guardrails report |
| CI/CD | .github/workflows/ci.yml, Dockerfile, docker-compose.yml | Open a CI run and confirm lint, type check, tests and scan steps |
| Demonstration | docs/live_demonstration_guide.md | Follow the step-by-step script against the running application |
| Tokenomics | docs/tokenomics_telemetry_audit.md, Prompt Log | Pool readings and prompt counts per milestone; limits stated |

## Known limitations

* Sessions are signed, not encrypted, cookies limited to about 4 KB.
* Search and the advisor are rule-based and make no LLM calls.
* The demo database is SQLite; the automated tests run against SQLite.
* No load or latency benchmarking was performed.
* AI usage during the build is measured as pool percentage and prompt counts, not tokens.
