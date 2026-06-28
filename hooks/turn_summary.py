#!/usr/bin/env python3
"""
End-of-turn summary hook (Stop).

On every substantive turn (>= MIN_TOOLS tool calls since the last human prompt)
this hook makes the agent take one more turn and end it with two plain-text
blocks — NO widget, NO stats line, NO .m_verify ledger:

  «Что дальше» — heading + 1-3 short bullets: what was done this turn and the
                 logical next step;
  «Задача»     — at the very end, ONE sentence restating (not quoting) what the
                 user asked for.

History: the branded logo widget was removed in v2.11.0, the autodrive
completion-driver in v2.12.0; the «Что дальше»/«Задача» text summary lived in
v2.13.0, was removed in v2.14.0, the whole hook (stats line + .m_verify ledger
feed) was deleted in v3.0.0 — and this file restores ONLY the text summary in
v3.1.0 at the owner's request. There is no ledger feed and no stats line here.

Flow per turn:
  1. Turn ends -> this Stop hook fires (stop_hook_active = false).
  2. Trivial turn (< MIN_TOOLS tools) -> exit silently, no block.
  3. Substantive turn -> emit {"decision":"block","reason": <summary instruction>};
     the agent writes the two blocks, then stops.
  4. Stop fires again with stop_hook_active = true -> exit silently. No loop.

FAIL-OPEN: any error -> exit 0 with no output, so a bug here can never trap the
session in a block loop.
"""
import sys, json, os

# --- tunables (env-overridable) ---------------------------------------------
MIN_TOOLS = int(os.environ.get("CLAUDE_SUMMARY_MIN_TOOLS", "2"))
MAX_PROMPT_CHARS = 800   # how much of the user's prompt to pass as paraphrase source
REASON_CHAR_CAP = 9500   # hook output strings are capped at 10k


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
    """For the LAST human turn -> EOF, return tool-use count + the prompt text."""
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
    tools_total = 0
    for obj in lines[start_idx:]:
        if obj.get("type") != "assistant":
            continue
        msg = obj.get("message") or {}
        for b in (msg.get("content") or []):
            if isinstance(b, dict) and b.get("type") == "tool_use":
                tools_total += 1

    return {"tools_total": tools_total, "last_prompt": last_prompt}


# --- output builder ---------------------------------------------------------
def build_reason(last_prompt):
    """Real-work turns: two plain-text blocks (NO widget, NO show_widget, NO
    ledger) — «Что дальше» + «Задача». Owner's personal hook text, Russian by
    design (see AGENTS.md conventions)."""
    prompt = (last_prompt or "").replace("\n", " ").strip()[:MAX_PROMPT_CHARS]
    reason = (
        "[end-of-turn summary hook] Обычным форматированным ТЕКСТОМ (НИКАКИХ виджетов, "
        "НЕ вызывай show_widget) сделай по порядку:\n\n"
        "1) Блок «Что дальше» — заголовок и 1–3 коротких пункта: что сделал в этом ходу "
        "и логичный следующий шаг.\n\n"
        "2) В САМОМ КОНЦЕ блок «Задача» — ОДНО предложение: суть того, что я просил "
        f"(НЕ дословно). Источник для перефраза (не цитируй целиком): «{prompt}»\n\n"
        "Кроме этих двух блоков в чат больше ничего не выводи."
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

    turn = parse_turn(hook_input.get("transcript_path", ""))
    if not turn:
        return  # nothing to summarize -> stay silent, fail-open

    # trivial turn (conversational, few/no tools) -> no forced summary
    if turn["tools_total"] < MIN_TOOLS:
        return

    print(json.dumps({
        "decision": "block",
        "reason": build_reason(turn["last_prompt"]),
        "suppressOutput": True,
    }))  # ensure_ascii=True -> pure-ASCII output, encoding-safe for any consumer


if __name__ == "__main__":
    main()
