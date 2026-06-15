#!/usr/bin/env python3
"""
End-of-turn summary WIDGET hook (Stop).

Upgrade of ~/bin/claude-stop-hook.py: instead of only printing a plain-text
ANSI systemMessage, on real-work turns it asks the assistant to render a rich
in-chat widget (via the visualization / show_widget tool) using the
decision:block -> one-more-turn mechanism.

Flow per turn:
  1. Turn ends -> this Stop hook fires (stop_hook_active = false).
  2. We parse the transcript for THIS turn's metrics (tokens, cost, time,
     tool calls, tool failures, sub-agents launched, last prompt).
  3. If the turn was trivial (few tools) -> emit a one-line systemMessage only.
     If it was real work -> emit {"decision":"block","reason": <render instructions + metrics>}.
  4. The assistant takes one more turn and renders the widget, then stops.
  5. Stop fires again with stop_hook_active = true -> we exit silently. No loop.

FAIL-OPEN: any error -> exit 0 with no output, so a bug here can never trap
the session in a block loop.
"""
import sys, json, os, time, glob as globmod
from datetime import datetime

# --- tunables (env-overridable) ---------------------------------------------
MIN_TOOLS_FOR_WIDGET = int(os.environ.get("CLAUDE_WIDGET_MIN_TOOLS", "2"))
MAX_PROMPT_CHARS = 600
REASON_CHAR_CAP = 9500  # hook output strings are capped at 10k

# m_verify ledger: code-change turns get a silent 4th instruction to upsert
# features-awaiting-verification into <cwd>/.m_verify/pending.md (curated by /m_verify).
LEDGER_REL = os.path.join(".m_verify", "pending.md")
CODE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")

# Branded widget renderer is hosted in this repo and served via jsDelivr; the hook
# only emits a tiny renderMWidget(<metrics>) call so no tokens are spent regenerating
# HTML. Bump this with the plugin release + git tag (jsDelivr serves @v<WIDGET_VER>);
# keep in sync with the BASE/@v tag in docs/widget/m_widget.js.
WIDGET_VER = "2.7.0"

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


def sum_subagent_tokens(transcript_path):
    """Session-cumulative sub-agent token totals + count of non-empty agents."""
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    count = 0
    if not transcript_path:
        return totals, count
    session_id = os.path.splitext(os.path.basename(transcript_path))[0]
    sub_dir = os.path.join(os.path.dirname(transcript_path), session_id, "subagents")
    if not os.path.isdir(sub_dir):
        return totals, count
    for f in globmod.glob(os.path.join(sub_dir, "agent-*.jsonl")):
        a = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
        try:
            for line in open(f, "r", encoding="utf-8"):
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") == "assistant":
                    u = (o.get("message") or {}).get("usage") or {}
                    a["input"] += u.get("input_tokens", 0) or 0
                    a["output"] += u.get("output_tokens", 0) or 0
                    a["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
                    a["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
        except Exception:
            continue
        if sum(a.values()) > 0:
            count += 1
            for k in totals:
                totals[k] += a[k]
    return totals, count


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


def ledger_block(ledger_path, today):
    """Silent 4th step: upsert features-awaiting-verification into the ledger.
    Only appended on turns where code actually changed."""
    p = ledger_path.replace("\\", "/")
    return (
        "\n\n4) ТИХИЙ шаг — ТОЛЬКО файловые операции, НИ строчки в чат: обнови ledger фич, "
        f"ожидающих проверки, по пути «{p}». В этом ходу менялся код, значит могли появиться "
        "фичи/поведение, которые юзеру (или скилу /m_verify) надо подтвердить. Для КАЖДОЙ реально "
        "реализованной в этом ходу вещи, которую имеет смысл проверять, сделай upsert одной секции. "
        "Канонический формат файла (Markdown; плоский список секций `## `; идентичность по полю "
        "key; имена полей пиши РОВНО так, по-английски; заголовок/значения — на рабочем языке):\n"
        "```\n"
        "# m_verify ledger — features awaiting verification\n"
        "<!-- schema:1 — appended by the m_verify Stop hook, curated by /m_verify. Flat list of "
        "`## ` items keyed by `key:`. Do not hand-edit during a /m_verify run. -->\n"
        "\n"
        "## <короткий заголовок фичи>\n"
        "- key: <stable-slug>\n"
        "- status: pending\n"
        "- who: unknown\n"
        "- how: <конкретная проверка — команда / URL / ожидаемое поведение>\n"
        "- files: <через запятую, что менялось>\n"
        f"- added: {today}\n"
        "- evidence:\n"
        "- repair_task:\n"
        "```\n"
        "Правила: создай папку и файл, если их нет (с этим заголовком). Если секция с таким key уже "
        "есть — НЕ дублируй (при необходимости обнови поля). Бери ТОЛЬКО реально сделанное в этом "
        "ходу, ничего не выдумывай. who всегда unknown (триаж сделает /m_verify), status pending, "
        "how — самая дешёвая надёжная проверка. Никаких секретов/токенов/прод-хостов в файле. Если в "
        "этом ходу не появилось ничего проверяемого юзером — НИЧЕГО не пиши и файл не создавай."
    )


def widget_snippet(data_json):
    """The exact (tiny) widget_code the assistant passes to show_widget. All the
    branded design/logo/animation lives in the jsDelivr-hosted m_widget.js, so this
    snippet stays small — no per-turn HTML regeneration, ~no tokens."""
    url = ("https://cdn.jsdelivr.net/gh/mapuamap/denys-fast-mskills@v"
           + WIDGET_VER + "/docs/widget/m_widget.js")
    return (
        '<div id="mw"></div>\n'
        '<script src="' + url + '"></script>\n'
        "<script>try{renderMWidget(" + data_json
        + ",'mw')}catch(e){document.getElementById('mw').textContent='m_widget: '+(e.message||e)}</script>"
    )


def build_reason(metrics, last_prompt, ledger_path=None, today=""):
    data = json.dumps(metrics, ensure_ascii=False)
    prompt = (last_prompt or "").replace("\n", " ").strip()[:MAX_PROMPT_CHARS]
    snippet = widget_snippet(data)
    reason = (
        "[end-of-turn summary hook] Сделай по порядку:\n\n"
        "1) Вызови инструмент визуализации show_widget (render_visualization / визуальный "
        "артефакт) РОВНО ОДИН раз: title=\"turn_stats\", а widget_code задай В ТОЧНОСТИ равным "
        "следующему блоку — скопируй дословно, НИЧЕГО не меняй и не дописывай свой HTML/CSS "
        "(весь брендовый дизайн, логотип и анимации уже внутри подключаемого скрипта):\n"
        "```\n" + snippet + "\n```\n"
        "Если инструмент визуализации недоступен — выведи компактную Markdown-таблицу из чисел "
        "в renderMWidget(...) выше (tokens.new, cost_usd, время, тулы, ошибки, агенты) и иди дальше.\n\n"
        "2) ПОСЛЕ виджета, обычным форматированным ТЕКСТОМ (НЕ внутри виджета) напиши блок "
        "«Что дальше» — заголовок и 1–3 коротких пункта: что сделал в этом ходу и логичный "
        "следующий шаг.\n\n"
        "3) В САМОМ КОНЦЕ, обычным текстом, напиши блок «Задача» — ОДНО предложение: суть того, "
        f"что я просил (НЕ дословно). Источник для перефраза (не цитируй целиком): «{prompt}»"
    )
    if ledger_path:
        reason += ledger_block(ledger_path, today)
    reason += "\n\nВ ЧАТ больше ничего не выводи" + (
        " (шаг 4 пишет ТОЛЬКО в файл, в чат — ничего)." if ledger_path else "."
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

    # sub-agents launched this turn (Task calls); fall back to non-empty agent files
    sub_tokens, sub_files = sum_subagent_tokens(transcript_path)
    subagents = turn["tasks"] if turn["tasks"] else sub_files

    dur_human = fmt_duration(turn["duration_seconds"])

    real_work = turn["tools_total"] >= MIN_TOOLS_FOR_WIDGET

    if not real_work:
        # trivial turn: keep the lightweight one-liner, no widget
        print(json.dumps({
            "systemMessage": one_line_summary(project, tk, total, cost, dur_human),
            "suppressOutput": True,
        }))
        return

    # code-change turns also (silently) feed the m_verify ledger
    code_changed = any(t in turn["tools_by_name"] for t in CODE_TOOLS)
    ledger_path = os.path.join(cwd, LEDGER_REL) if (cwd and code_changed) else None
    today = datetime.now().strftime("%Y-%m-%d")

    metrics = {
        "project": project,
        "model": turn["model"],
        "duration_human": dur_human,
        "duration_seconds": round(turn["duration_seconds"]) if turn["duration_seconds"] else None,
        "tokens": {
            "new": tk["input"] + tk["output"],  # реально сгенерировано/добавлено за ход
            "input": tk["input"], "output": tk["output"],
            "cache_read": tk["cache_read"], "cache_write": tk["cache_write"],
            "total": total,
        },
        "cost_usd": round(cost, 4),
        "pricing_model": prices.get("model", "fallback"),
        "tools_total": turn["tools_total"],
        "tools_by_name": turn["tools_by_name"],
        "tool_results": turn["tool_results"],
        "tool_failures": turn["tool_failures"],
        "subagents_launched": subagents,
    }

    print(json.dumps({
        "decision": "block",
        "reason": build_reason(metrics, turn["last_prompt"], ledger_path, today),
        "systemMessage": one_line_summary(project, tk, total, cost, dur_human),
        "suppressOutput": True,
    }))  # ensure_ascii=True -> pure-ASCII output, encoding-safe for any consumer


if __name__ == "__main__":
    main()
