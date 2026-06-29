# tstanmay13's Claude Code skills

A marketplace of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills. Each one is a **conversational skill** — it changes *how* Claude works with you, rather than adding a command you have to remember.

Add the marketplace once and install any of them:

```
/plugin marketplace add tstanmay13/claude-skills
/plugin install debrief@tstanmay13-skills
/plugin install product-view@tstanmay13-skills
```

## The skills

| Skill | What it does | Repo |
|---|---|---|
| **debrief** | At the end of a session, turns finished work into actual learning — makes *you* reconstruct what happened before it fills any gaps, so the AI's fluency stops standing in for your own understanding. | [tstanmay13/debrief](https://github.com/tstanmay13/debrief) |
| **product-view** | Flips Claude out of code-language and into the perspective of whoever's on the other side of the screen — the customer, user, player, reader — until you ask for the code. | [tstanmay13/product-view](https://github.com/tstanmay13/product-view) |

### debrief

> *"did I actually learn that, or did I just watch you do it?"*

Working with a capable AI is a fluency-illusion machine: the work flows past, it all feels understood, and you retain nothing. `debrief` runs a recall-first ritual at the end of a session — you reconstruct the one or two ideas worth keeping, it catches the gaps, and distills a durable lesson.

![debrief in action](https://github.com/tstanmay13/debrief/raw/main/assets/demo.gif)

### product-view

> *"what's actually broken for our customers?"*

Most software explanations sneak implementation language into descriptions of what the product does. `product-view` keeps Claude describing what the human on the other side of the screen experiences — what they see, do, and feel — until you explicitly ask to cross into code.

![product-view in action](https://github.com/tstanmay13/product-view/raw/main/assets/demo.gif)

## Installing a single skill directly

Each skill is also its own standalone marketplace, if you only want one:

```
/plugin marketplace add tstanmay13/debrief
/plugin install debrief@tstanmay13-debrief
```

```
/plugin marketplace add tstanmay13/product-view
/plugin install product-view@tstanmay13-product-view
```

## License

[MIT](LICENSE). Each skill's source and full docs live in its own repo, linked above.
