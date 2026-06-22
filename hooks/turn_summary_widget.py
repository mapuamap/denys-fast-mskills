#!/usr/bin/env python3
"""
End-of-turn summary hook (Stop).

The branded in-chat WIDGET (logo + stats card) was removed at the owner's
request (v2.11.0), and the plain-text «Что дальше»/«Задача» summary blocks were
removed too (v2.14.0) — the owner disliked the "what's done / what's next"
recap. What the hook does now:
  * a lightweight one-line ANSI systemMessage with the turn's token/cost stats
    (shown on every non-empty turn);
  * on code-change turns only, the silent .m_verify ledger feed via a
    decision:block whose reason is JUST that file-only instruction (no widget,
    no summary text). This is the sole remaining use of decision:block.

Flow per turn:
  1. Turn ends -> this Stop hook fires (stop_hook_active = false).
  2. We parse the transcript for THIS turn's metrics (tokens, cost, time).
  3. Code changed this turn -> emit {"decision":"block","reason": <silent ledger
     instruction>} + the one-line systemMessage. Otherwise just the one-liner.
  4. (code-change turn) the assistant takes one more turn, upserts the ledger
     file silently, then stops.
  5. Stop fires again with stop_hook_active = true -> we exit silently. No loop.

FAIL-OPEN: any error -> exit 0 with no output, so a bug here can never trap
the session in a block loop.
"""
import sys, json, os, time
from datetime import datetime

# --- tunables (env-overridable) ---------------------------------------------
MIN_TOOLS_FOR_WIDGET = int(os.environ.get("CLAUDE_WIDGET_MIN_TOOLS", "2"))
REASON_CHAR_CAP = 9500  # hook output strings are capped at 10k

# m_verify ledger: code-change turns get a silent instruction to upsert
# features-awaiting-verification into <cwd>/.m_verify/pending.md (curated by /m_verify).
LEDGER_REL = os.path.join(".m_verify", "pending.md")
CODE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")

PRICE_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "claude-pricing.json")
CACHE_MAX_AGE = 86400  # 1 day

# Anthropic direct API pricing fallback (USD per 1M tokens), Opus-class.
FALLBACK_PRICES = {"input": 15.0, "output": 75.0, "cache_read": 1.875, "cache_write": 18.75}


# --- pricing (reused from claude-stop-hook.py) ------------------------------
def fetch_openrouter_prices():
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"User-Agent": "claude-stop-hook/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        for m in data.get("data", []):
            mid = m.get("id", "")
            if "claude-opus" not in mid or "-fast" in mid:
                continue
            p = m.get("pricing", {})
            prices = {
                "input": float(p.get("prompt", 0)) * 1_000_000,
                "output": float(p.get("completion", 0)) * 1_000_000,
                "cache_read": float(p.get("input_cache_read", 0)) * 1_000_000,
                "cache_write": float(p.get("input_cache_write", 0)) * 1_000_000,
                "model": mid,
                "fetched": time.time(),
            }
            os.makedirs(os.path.dirname(PRICE_CACHE), exist_ok=True)
            with open(PRICE_CACHE, "w") as f:
                json.dump(prices, f)
            return prices
    except Exception:
        pass
    return None


def get_prices():
    if os.path.exists(PRICE_CACHE):
        try:
            with open(PRICE_CACHE) as f:
                cached = json.load(f)
            if time.time() - cached.get("fetched", 0) < CACHE_MAX_AGE:
                return cached
        except Exception:
            pass
    fresh = fetch_openrouter_prices()
    return fresh if fresh else FALLBACK_PRICES


def calc_cost(tk, prices):
    return (
        tk["input"] * prices["input"] / 1_000_000
        + tk["output"] * prices["output"] / 1_000_000
        + tk["cache_read"] * prices["cache_read"] / 1_000_000
        + tk["cache_write"] * prices["cache_write"] / 1_000_000
    )


# --- formatting -------------------------------------------------------------
def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(int(n))


def cost_fmt(c):
    return f"${c:.4f}" if c < 0.01 else f"${c:.2f}"


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def fmt_duration(seconds):
    if seconds is None:
        return "?"
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


# --- transcript parsing -----------------------------------------------------
def is_human_prompt(obj):
    """True only for a genuine user-typed prompt (not a tool_result carrier,
    not meta, not a slash-command expansion / sidechain)."""
    if obj.get("type") != "user":
        return False
    if obj.get("isMeta") or obj.get("isSidechain") or obj.get("isCompactSummary"):
        return False
    msg = obj.get("message") or {}
    content = msg.get("content", "")
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                return False  # this is a tool result, not a human turn
        text = " ".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    elif isinstance(content, str):
        text = content
    else:
        return False
    t = text.strip()
    if not t:
        return False
    # skip slash-command expansions / injected stdout
    if t.startswith("<command-") or t.startswith("<local-command"):
        return False
    return True


def human_prompt_text(obj):
    msg = obj.get("message") or {}
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                return b.get("text", "")
            if isinstance(b, str):
                return b
    return ""


def parse_turn(transcript_path):
    """Aggregate metrics for the LAST human turn -> EOF."""
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    tools_by_name = {}
    tools_total = 0
    tool_failures = 0
    tool_results = 0
    tasks = 0
    start_ts = None
    last_ts = None
    last_prompt = ""
    model = ""

    if not transcript_path or not os.path.exists(transcript_path):
        return None

    lines = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except Exception:
                continue

    # find index of last genuine human prompt
    start_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if is_human_prompt(lines[i]):
            start_idx = i
            break
    if start_idx is None:
        return None

    last_prompt = human_prompt_text(lines[start_idx])
    start_ts = parse_ts(lines[start_idx].get("timestamp"))
    last_ts = start_ts

    for obj in lines[start_idx:]:
        ts = parse_ts(obj.get("timestamp"))
        if ts and (last_ts is None or ts > last_ts):
            last_ts = ts
        typ = obj.get("type")
        msg = obj.get("message") or {}
        if typ == "assistant":
            u = msg.get("usage") or {}
            tokens["input"] += u.get("input_tokens", 0) or 0
            tokens["output"] += u.get("output_tokens", 0) or 0
            tokens["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
            tokens["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
            model = msg.get("model") or model
            for b in (msg.get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    name = b.get("name", "?")
                    tools_by_name[name] = tools_by_name.get(name, 0) + 1
                    tools_total += 1
                    if name == "Task":
                        tasks += 1
        elif typ == "user":
            for b in (msg.get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    tool_results += 1
                    if b.get("is_error"):
                        tool_failures += 1

    duration = (last_ts - start_ts).total_seconds() if (start_ts and last_ts) else None
    return {
        "tokens": tokens,
        "tools_by_name": tools_by_name,
        "tools_total": tools_total,
        "tool_results": tool_results,
        "tool_failures": tool_failures,
        "tasks": tasks,
        "duration_seconds": duration,
        "last_prompt": last_prompt,
        "model": model,
    }


# --- output builders --------------------------------------------------------
def one_line_summary(project, tk, total, cost, dur):
    DIM, GREEN, RED, RESET = "\033[2m", "\033[32m", "\033[31m", "\033[0m"
    return (
        f"{GREEN}◆{RESET} {project}  "
        f"{DIM}▲{fmt(tk['input'])} ▼{fmt(tk['output'])} "
        f"⤷{fmt(tk['cache_read'])} ⤶{fmt(tk['cache_write'])}  "
        f"∑{fmt(total)}  ⏱{dur}{RESET}  {RED}{cost_fmt(cost)}{RESET}"
    )


def build_ledger_reason(ledger_path, today):
    """Silent step (the ONLY decision:block use left): upsert features-awaiting-
    verification into the ledger. Used only on turns where code actually changed.
    File IO only — NOTHING in chat (no widget, no summary text).

    Compact form: one-line-per-field template instead of a fenced schema dump,
    to keep this reason (re-sent every code-change turn) small in context. The
    produced file format is unchanged — same header, same English field names,
    same `schema:1` — so the contract with skills/m_verify/SKILL.md still holds."""
    p = ledger_path.replace("\\", "/")
    reason = (
        "[end-of-turn ledger hook] ТИХИЙ шаг — ТОЛЬКО файл, НИ строчки в чат, "
        "НИКАКИХ виджетов и НИКАКИХ блоков-саммари. В этом ходу менялся код → обнови ledger "
        f"фич на проверку: «{p}». Для КАЖДОЙ реально сделанной проверяемой вещи — upsert одной "
        "секции `## `; идентичность по полю key (не дублируй; при нужде обнови поля). Имена полей "
        "пиши РОВНО так (англ.), значения — на рабочем языке:\n"
        "`## <заголовок>` · `- key: <slug>` · `- status: pending` · `- who: unknown` · "
        "`- how: <дешёвая надёжная проверка: команда/URL/поведение>` · `- files: <что менялось>` · "
        f"`- added: {today}` · `- evidence:` · `- repair_task:`\n"
        "Файл/папку создай, если их нет, с шапкой `# m_verify ledger — features awaiting "
        "verification` и строкой `<!-- schema:1 -->`. Бери ТОЛЬКО сделанное в этом ходу, ничего не "
        "выдумывай; никаких секретов/токенов/прод-хостов. Нечего проверять — НИЧЕГО не пиши. "
        "В ЧАТ больше ничего не выводи (этот шаг пишет ТОЛЬКО в файл)."
    )
    return reason[:REASON_CHAR_CAP]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # hook stdout is cp1252 on Windows
    except Exception:
        pass
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        return  # fail-open

    # second firing after our own block: do nothing -> breaks the loop
    if hook_input.get("stop_hook_active"):
        return

    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", "") or ""
    project = os.path.basename(cwd) if cwd else "?"

    turn = parse_turn(transcript_path)
    if not turn:
        return  # nothing to summarize -> stay silent, fail-open

    tk = turn["tokens"]
    total = sum(tk.values())
    prices = get_prices()
    cost = calc_cost(tk, prices)
    dur_human = fmt_duration(turn["duration_seconds"])
    one_liner = one_line_summary(project, tk, total, cost, dur_human)

    # Widget removed (v2.11.0); «Что дальше»/«Задача» summary blocks removed
    # (v2.14.0). The ONLY remaining decision:block is the silent .m_verify ledger
    # feed on real-work turns where code changed. Every other turn is just the
    # one-line stats systemMessage, no block.
    real_work = turn["tools_total"] >= MIN_TOOLS_FOR_WIDGET
    code_changed = any(t in turn["tools_by_name"] for t in CODE_TOOLS)

    if real_work and code_changed and cwd:
        ledger_path = os.path.join(cwd, LEDGER_REL)
        today = datetime.now().strftime("%Y-%m-%d")
        print(json.dumps({
            "decision": "block",
            "reason": build_ledger_reason(ledger_path, today),
            "systemMessage": one_liner,
            "suppressOutput": True,
        }))
        return

    print(json.dumps({
        "systemMessage": one_liner,
        "suppressOutput": True,
    }))  # ensure_ascii=True -> pure-ASCII output, encoding-safe for any consumer


if __name__ == "__main__":
    main()
