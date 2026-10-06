# Releasing public skills

The catalog is separate from each plugin's source. Develop in sibling `debrief`, `product-view`, `think-like-fable-5`, and `orchestrate` checkouts. Never edit installed caches. Both marketplace manifests are generated from `catalog.json` and the source manifests, with immutable source commit pins.

1. Update the skill and its references in its source repo. Keep `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and skill version metadata consistent. Preserve licenses and notices for any third-party material.
2. Validate the skill and plugin, then commit and push the source repo. Ensure the commit is available on GitHub before publishing a catalog that points to it.
3. From the catalog checkout, run `python3 scripts/catalog.py generate`, then `python3 scripts/catalog.py check`. Commit and push the generated catalogs together.
4. Run `./install.sh` to refresh both agents' installed plugins. Restart the agents to load new instructions. `./verify.sh` checks the installed versions in default and personal profiles.
5. Run `python3 scripts/catalog.py package`. The four versioned ZIPs and `SHA256SUMS` appear in ignored `dist/`. Packages contain only skill files, manifests, required icons, and notices, never private skills or machine configuration.

## Public directory submission

GitHub catalogs are installable distribution; they do not create a universal directory listing. Upload each ZIP separately in the [OpenAI Plugins dashboard](https://platform.openai.com/plugins). Select your verified developer identity, resolve metadata and skill checks, submit for review, then publish after approval. Do not mark a plugin listed until the dashboard confirms publication. Updates to skills or metadata require another ZIP.

These are skills-only packages: no MCP server or credentials are bundled. `orchestrate` needs local worker capabilities supplied by Claude Code or Codex; ordinary Chat can only help plan. The README and listing describe that limit.

For Claude's official directory, follow its submission process separately; installing this GitHub marketplace already works without an official listing. Approvals do not transfer between directories.

References: [OpenAI package format](https://developers.openai.com/plugins/build/plugins), [submission process](https://developers.openai.com/plugins/deploy/submission), [Claude migration](https://developers.openai.com/plugins/guides/submit-claude-plugin).
