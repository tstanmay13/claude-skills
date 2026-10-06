# Tanmay Singh’s agent skills

A public plugin catalog for **Claude Code and Codex**. Each plugin has its own source repository and release version. The catalog contains installation metadata and release tooling; skill instructions live in the source repos.

The existing repository and marketplace names stay unchanged so current Claude installs keep working.

| Plugin | Purpose | Source |
|---|---|---|
| **debrief** | Turn finished work into understanding through recall and feedback | [debrief](https://github.com/tstanmay13/debrief) |
| **product-view** | Explain features, bugs, and plans through the user’s experience | [product-view](https://github.com/tstanmay13/product-view) |
| **think-like-fable-5** | Outcome-first reporting, scoped autonomy, honest verification | [think-like-fable-5](https://github.com/tstanmay13/think-like-fable-5) |
| **orchestrate** | Brief workers, coordinate separate ownership, verify their reports | [orchestrate](https://github.com/tstanmay13/orchestrate) |

## Install

Claude Code:

```sh
claude plugin marketplace add tstanmay13/claude-skills
claude plugin install debrief@tstanmay13-skills
claude plugin install product-view@tstanmay13-skills
claude plugin install think-like-fable-5@tstanmay13-skills
claude plugin install orchestrate@tstanmay13-skills
```

Codex:

```sh
codex plugin marketplace add tstanmay13/claude-skills
codex plugin add debrief@tstanmay13-skills
codex plugin add product-view@tstanmay13-skills
codex plugin add think-like-fable-5@tstanmay13-skills
codex plugin add orchestrate@tstanmay13-skills
```

Install only the plugins you want. Restart the agent after installation. Invoke `/debrief`, `/product-view`, `/think-like-fable-5`, or `/orchestrate` in Claude Code; use `$debrief`, `$product-view`, `$think-like-fable-5`, or `$orchestrate` in Codex. Debrief and Product View also support contextual activation. The other two are explicitly invoked.

Orchestrate requires a local coding environment with worker capabilities. Its instructions adapt to Claude Code or Codex tools; it does not supply those tools. Plain Chat can help plan but cannot run the local workflow.

## Personal setup and maintenance

Clone this catalog and the four source repos as sibling directories. `./install.sh` refreshes all four released plugins in default and personal Claude and Codex profiles, and `./verify.sh` checks versions and enabled state. To target different profiles, pass repeated `--claude-home <path>` and `--codex-home <path>` flags to either script. These scripts do not modify account logins.

`catalog.json` identifies the source repos. `scripts/catalog.py generate` reads their committed release metadata and emits `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and `releases.json`. Both catalogs pin the same source commits. Source editing and installed caches remain separate. See [PUBLISHING.md](PUBLISHING.md) for validation, release, and submission steps.

## Public directories

This GitHub marketplace is installable directly. It does not imply a listing or approval in either agent’s official directory. OpenAI submission ZIPs are generated with `python3 scripts/catalog.py package`; public publication requires developer identity verification and directory review.

## License and attribution

The catalog is [MIT](LICENSE). Each plugin preserves its own license and `NOTICE.md`. Third-party skills bundled in the private dev setup keep their upstream licenses and provenance there; they are not republished as these four original plugins. Private reviewer examples, voice samples, and company profiles stay in their private repo.
