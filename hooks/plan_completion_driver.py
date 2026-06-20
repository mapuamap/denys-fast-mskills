#!/usr/bin/env python3
"""
m_plan autodrive — completion-driver Stop hook.

Turns `09_verification.md` (the m_plan completion oracle) into an ENFORCED gate
instead of a suggestion. While an m_plan_implement / m_plan run is "armed", this
Stop hook blocks stopping as long as `09` still has open `[ ]` checks, feeding the
agent a focused "do the next check" instruction — i.e. /goal-style drive-to-done
logic, deterministic and with no user action required.

ARMING (so this never hijacks a normal session):
  The skill writes a run-state file `.m_plan/<slug>/.run.json` when it starts the
  Phase B walk, and deletes it when it reports DONE/PARTIAL/BLOCKED or the user
  aborts. With NO such file, this hook does nothing (exit 0, silent).

LOOP SAFETY (we own it — Claude Code has no built-in turn cap):
  - turn counter vs max_turns (skill-supplied, hard-clamped here)
  - no-progress streak: if the open-count doesn't drop for N fires, stop
  - user takeover: if a new human prompt appears after arming (user interrupted
    and typed), or the last human prompt is a stop-word, disarm and allow stop
  - any error / missing oracle -> fail-open: disarm-safe, exit 0, never trap

WIDGET COEXISTENCE:
  The end-of-turn widget hook (turn_summary_widget.py) is left untouched. During a
  drive both Stop hooks fire; this hook's reason tells the agent to skip the widget
  for that turn (cosmetic only — the gate itself does not depend on it).
"""
import sys, os, json, re, glob

MAX_TURNS_CEILING = 80          # hard upper bound regardless of skill value
MAX_TURNS_FLOOR = 12            # never give up before this many drive turns
NO_PROGRESS_LIMIT = 2           # consecutive fires with no drop in open count
STOP_WORDS = ("stop", "abort", "cancel", "стоп", "хватит", "отмена", "прекрати")
OPEN_RE = re.compile(r"^\s*-\s*\[\s\]\s*(.+)$")   # "- [ ] ..."


def find_run_state(cwd):
    """Most-recently-modified armed .run.json under <cwd>/.m_plan/*/."""
    if not cwd:
        return None, None
    cands = glob.glob(os.path.join(cwd, ".m_plan", "*", ".run.json"))
    best, best_mtime = None, -1
    for p in cands:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m > best_mtime:
            best, best_mtime = p, m
    if not best:
        return None, None
    try:
        with open(best, "r", encoding="utf-8") as f:
            return best, json.load(f)
    except Exception:
        return best, None


def disarm(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def save_state(path, state):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
    except Exception:
        pass


def count_human_prompts(transcript_path):
    """Count genuine user-typed prompts (not tool_results / meta / slash expansions)
    and return (count, last_text)."""
    count, last = 0, ""
    if not transcript_path or not os.path.exists(transcript_path):
        return count, last
    try:
        for line in open(transcript_path, "r", encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "user" or o.get("isMeta") or o.get("isSidechain") or o.get("isCompactSummary"):
                continue
            msg = o.get("message") or {}
            content = msg.get("content", "")
            text = ""
            if isinstance(content, list):
                if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                    continue  # tool result carrier, not a human turn
                text = " ".join(b.get("text", "") for b in content
                                if isinstance(b, dict) and b.get("type") == "text")
            elif isinstance(content, str):
                text = content
            t = text.strip()
            if not t or t.startswith("<command-") or t.startswith("<local-command"):
                continue
            count += 1
            last = t
    except Exception:
        pass
    return count, last


def read_open_rows(verif_path):
    """Return (open_count, [open row texts])."""
    rows = []
    try:
        for line in open(verif_path, "r", encoding="utf-8"):
            m = OPEN_RE.match(line.rstrip("\n"))
            if m:
                rows.append(m.group(1).strip())
    except Exception:
        return None, []
    return len(rows), rows


def build_reason(open_count, rows, turns_used, max_turns):
    head = (
        f"[m_plan autodrive] План не закончен: в 09_verification.md осталось {open_count} "
        f"открытых проверок (ход {turns_used}/{max_turns}). НЕ останавливайся и НЕ перепланируй — "
        "сделай следующую: прогони её cited-команду из 05_step_plan.md / 07_test_plan.md (или "
        "выполни шаг из 05), затем флипни [ ]→[x] в 09 с доказательством. Если строка реально "
        "заблокирована — пометь её [!] с описанием блокера (это разрешено остановить драйв).\n"
        "Не рендери в этом ходу end-of-turn виджет и блоки «Что дальше»/«Задача» — идёт автодрайв; "
        "виджет покажется один раз, когда план завершится.\nОсталось:\n"
    )
    listed = "\n".join(f"- {r}" for r in rows[:6])
    if open_count > 6:
        listed += f"\n- …и ещё {open_count - 6}"
    return head + listed


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        return  # fail-open

    cwd = hook_input.get("cwd", "") or ""
    transcript_path = hook_input.get("transcript_path", "")

    run_path, state = find_run_state(cwd)
    if not run_path:
        return  # not armed -> stay completely silent
    if not isinstance(state, dict) or state.get("mode") != "autodrive":
        disarm(run_path)
        return

    slug_dir = os.path.dirname(run_path)
    verif = os.path.join(slug_dir, state.get("verification_file", "09_verification.md"))
    if not os.path.exists(verif):
        disarm(run_path)  # no oracle -> cannot drive
        return

    # --- user takeover detection -------------------------------------------
    human_now, last_human = count_human_prompts(transcript_path)
    baseline = state.get("human_prompts_at_arm")
    if baseline is None:
        state["human_prompts_at_arm"] = human_now  # first fire sets the baseline
    elif human_now > baseline:
        disarm(run_path)  # user interrupted and typed -> hand control back
        return
    if last_human and any(w in last_human.lower() for w in STOP_WORDS) \
            and len(last_human) < 40:
        disarm(run_path)
        return

    # --- completion check --------------------------------------------------
    open_count, rows = read_open_rows(verif)
    if open_count is None:
        disarm(run_path)
        return
    if open_count == 0:
        disarm(run_path)  # done -> allow stop; agent reports normally
        return

    # --- progress + caps ---------------------------------------------------
    last_open = state.get("last_open_count")
    if last_open is not None and open_count >= last_open:
        state["no_progress_streak"] = int(state.get("no_progress_streak", 0)) + 1
    else:
        state["no_progress_streak"] = 0
    state["last_open_count"] = open_count
    state["turns_used"] = int(state.get("turns_used", 0)) + 1

    try:
        max_turns = int(state.get("max_turns", 0))
    except (TypeError, ValueError):
        max_turns = 0
    max_turns = max(MAX_TURNS_FLOOR, min(max_turns or MAX_TURNS_FLOOR, MAX_TURNS_CEILING))

    if state["turns_used"] >= max_turns:
        disarm(run_path)
        print(json.dumps({
            "systemMessage": f"m_plan autodrive: turn cap {max_turns} reached, "
                             f"{open_count} check(s) still open — stopping.",
            "suppressOutput": True,
        }))
        return
    if state["no_progress_streak"] >= NO_PROGRESS_LIMIT:
        disarm(run_path)
        print(json.dumps({
            "systemMessage": f"m_plan autodrive: no progress for {NO_PROGRESS_LIMIT} turns, "
                             f"{open_count} check(s) still open — stopping for review.",
            "suppressOutput": True,
        }))
        return

    # --- keep driving ------------------------------------------------------
    save_state(run_path, state)
    print(json.dumps({
        "decision": "block",
        "reason": build_reason(open_count, rows, state["turns_used"], max_turns),
        "suppressOutput": True,
    }))


if __name__ == "__main__":
    main()
