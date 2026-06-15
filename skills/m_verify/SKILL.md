---
name: m_verify
description: Feature-verification manager. Reads the .m_verify/ ledger of features that were implemented but not yet confirmed working, auto-runs every check AI can do on its own (build/test/lint/HTTP/CLI + Playwright/browser), hands the user a minimal checklist of only what a human must confirm, and spawns background repair agents for anything that fails — without blocking the conversation. Use when user invokes /m_verify, says "what do I need to test", "what's left to verify", "check the pending features", "verify what we built", or after a chunk of implementation work that needs sign-off.
---

# m_verify

Всегда отвечай на русском. Коротко — по одному предложению на пункт, без воды.

## Формат ледджера (контракт с хуком)

Файл `.m_verify/pending.md`, плоский список секций `## `, ключ — поле `key:`. Подтверждённое → `.m_verify/confirmed.md`.

```
# m_verify ledger — features awaiting verification
<!-- schema:1 -->

## Название фичи
- key: stable-slug
- status: pending
- who: unknown
- how: конкретная проверка — команда / URL / что должно произойти
- files: file1, file2
- added: 2026-06-15
- evidence:
- repair_task:
```

Статусы: `pending → ai-verifying → confirmed` · `pending → needs-human → confirmed` · `failed → repairing → (re-verify)`.

## Шаг 1 — Загрузить ледджер

Прочитай `.m_verify/pending.md`. Если файла нет или нет открытых пунктов — предложи засеять по `git log`/`git diff` последних коммитов. Выведи: `Открыто: N (pending X, needs-human Y, failed Z).`

## Шаг 2 — Триаж

Для каждого `pending` пункта реши `who`:
- `ai` — детерминированно проверяемо: тесты, билд, lint, CLI-команда, HTTP-проба, Playwright-сценарий, файл/роут существует.
- `human` — нужен человеческий взгляд или недоступные тебе учётки / ручные шаги.
- Сомневаешься — ставь `ai`, дай проверке решить. Обнови поля `who` и `how` в файле.

## Шаг 3 — Самопроверка (шум — в агента)

Прогони все `ai`-пункты:
- Тесты / билд / lint / CLI / HTTP → делегируй агенту **`m_code-test-runner`** (возвращает краткий pass/fail).
- Playwright / live-браузер → гони через `npx playwright test` или браузерный MCP; если MCP недоступен — переводи в `needs-human`.
- Широкий поиск «где это вообще» → **`m_code-context-scout`**.

Обнови ледджер: `confirmed` + `evidence` (команда + вывод) или `failed` + `evidence` (текст ошибки).

## Шаг 4 — Чек-лист для человека

Выведи нумерованный список только `needs-human` пунктов — одна строка каждый: что открыть, что сделать, что должно получиться. Рядом — сколько AI подтвердил и что отдано в ремонт.

## Шаг 5 — Цикл с пользователем

Юзер отвечает («1 ок, 2 сломано»):
- `ок` → `status: confirmed`, `evidence: confirmed by user <дата>`, перенеси в `confirmed.md`.
- `сломано` → `status: failed`, запиши описание в `evidence`, запусти **`m_verify-repair`** с `run_in_background: true` (передай `key`, `files`, описание поломки, `how`), поставь `status: repairing`. Продолжай разговор с юзером — не жди агента.
- Когда агент вернётся — перепроверь (AI-проверка если возможно, иначе `needs-human`), обнови ледджер, сообщи юзеру.

## Шаг 6 — Закрытие

Перечитай ледджер с диска. Выведи: `Подтверждено: N · Для человека: M · В ремонте: K · Провалено: J.` Перенеси подтверждённое в `confirmed.md`, убери из `pending.md`.

## Правила

- Читай ледджер с диска перед каждым шагом — не доверяй памяти.
- Никогда не дублируй пункты, не удаляй — только меняй поля или архивируй.
- Никогда не выдумывай результат проверки.
- Агент чинит рабочее дерево, никогда не коммитит — это решение юзера.
- Никаких секретов и прод-хостов в ледджере.

## Files in this skill
- `SKILL.md` — this file
