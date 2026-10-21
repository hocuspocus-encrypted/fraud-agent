# Fraud Investigation Agent

A framework-free agent that investigates flagged transactions: it decides
which tools to call, gathers evidence, and returns a structured verdict
with cited reasoning. Includes an eval harness that measures how often
it is right, and a rule-based baseline it has to beat.

## Layout

```
fraud-agent/
├── README.md
├── requirements.txt
├── .gitignore
└── agent/
    ├── main.py              run the agent on the two original demo cases
    ├── eval.py              run ALL labeled cases, print a report, save results
    ├── compare.py           diff two saved eval runs side by side
    ├── eval_cases.json      15 hand-labeled cases (expected verdict + reasoning)
    ├── orchestrator.py      dispatcher: picks a provider from MODEL_PROVIDER
    ├── tools.py             4 tools + provider-neutral schemas
    ├── seed_db.py           builds the demo SQLite DB (15 accounts, 62 txns)
    └── adapters/
        ├── shared.py            system prompt + verdict parsing, shared by LLM adapters
        ├── anthropic_adapter.py Claude tool-use loop
        ├── gemini_adapter.py    Gemini Interactions API loop
        └── baseline_adapter.py  rule-based scorer, no LLM
```

## Setup (Windows PowerShell)

```
cd fraud-agent
pip install -r requirements.txt
cd agent
```

Pick a provider. `MODEL_PROVIDER` defaults to `anthropic` if you don't set it.

```
# Gemini
$env:MODEL_PROVIDER = "gemini"
$env:GEMINI_API_KEY = "your-key"

# Claude
$env:MODEL_PROVIDER = "anthropic"
$env:ANTHROPIC_API_KEY = "your-key"

# No LLM, no key, no cost
$env:MODEL_PROVIDER = "baseline"
```

(In cmd, use `set MODEL_PROVIDER=gemini` instead. `set` does nothing useful in PowerShell.)

## Running

```
python main.py                          # the two original demo cases
python eval.py --provider baseline      # free; sanity-check the harness
python eval.py --provider gemini        # the real eval
python eval.py --provider anthropic
python eval.py --provider gemini --case c13_5 --verbose   # one case, show tool calls
python eval.py --provider gemini --sleep 2                # pause between cases if you hit rate limits
python compare.py results\gemini_<stamp>.json results\anthropic_<stamp>.json
```

Every eval run saves its full results (verdicts, explanations, which tools
were called) to `agent/results/`, so you can compare runs later.

## How the eval works

Each case in `eval_cases.json` has an `expected_verdict`, optional
`acceptable_verdicts`, and a `notes` field explaining the reasoning
behind the label. Merchant and amount are read from the database, so
the cases can't drift out of sync with the data.

- **Strict accuracy** counts only the exact expected verdict.
- **Lenient accuracy** also accepts `acceptable_verdicts`, for cases where
  two answers are both defensible (e.g. `suspicious` vs `legitimate` on
  a borderline case).
- **Cost-asymmetric errors** are reported separately. Missing real fraud
  and blocking a good customer are different mistakes from a
  `legitimate`/`suspicious` mix-up, so they get their own counts.
- **Behavior checks** flag verdicts reached with zero tool calls,
  unparseable output, and actions that contradict the agent's own verdict.

### What the cases cover

| Pattern | Cases | What it tests |
|---|---|---|
| Clear fraud | t4, c03_7, c10_6 | Multiple signals, velocity, escalation |
| Impossible travel | c05_4 | Using the geo tool when it's the *only* signal |
| Needs-review | c06_3, c08_3, c14_3 | New accounts, tiny-amount probes |
| Legit but unusual | c04_4, c07_5, c13_5 | Travel, large regular payments, night-shift hours |
| Traps | c11_3, c12_3, c15_4 | Misleading tool output, "unknown" merchant, city bias |
| Pipeline false positive | c09_5, t7 | Clearing flags that shouldn't have been raised |

## Reading the results honestly

- **The dataset is small and synthetic, and I wrote both the data and the
  baseline's rules.** A rule-based baseline scoring ~93% is partly a
  sign the cases are easy and aligned with the rules, not proof that
  rules are enough for real fraud. Don't quote a headline number; quote
  the cases the agent gets wrong and what that taught you.
- **LLM output varies run to run.** One run is a sample, not a measurement.
  Run each provider a few times before trusting a difference of one case.
- **Read the explanations on every miss.** A correct verdict reached for
  a wrong reason (or a "plausible-sounding" claim no tool output
  supports) is a failure the accuracy number hides.

## Next steps

1. Run `eval.py` for Gemini (and Claude if you want the comparison), then
   read the misses before changing anything.
2. Add cases the baseline *fails*. The interesting question is whether
   the LLM beats the rules where the rules are blind, not where they agree.
3. Swap SQLite for your real Postgres pipeline: only the function bodies
   in `tools.py` change.
4. Wire it into the Kafka/PySpark flow so flagged transactions trigger
   an investigation and the verdict is stored with the flag.
5. Surface the tool-call trace in Streamlit.
