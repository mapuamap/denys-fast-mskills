#!/usr/bin/env python3
"""Build Desktop/web-ready skill .zip packages from skills/.

Claude Code installs this repo as a plugin (marketplace). Claude Desktop and
claude.ai cannot add marketplaces — they take individual Agent Skills uploaded
as a .zip (Customize -> Skills -> Create skill -> Upload). This script produces
one zip per skill in docs/skills-pack/ so those surfaces can install the skills.

Two transforms make the skills usable off Claude Code:
  * `disable-model-invocation: true` is stripped — Desktop/web have no slash
    invocation, so a skill must be model-invocable to ever run there.
  * the `evals/` folder is omitted — it's only for skill testing.

Each zip contains a single top-level folder named exactly after the skill
(folder name must match the skill name on upload).

Run from the repo root:  python scripts/build_skills_pack.py
"""
import os
import re
import zipfile

SKILLS_DIR = "skills"
OUT_DIR = os.path.join("docs", "skills-pack")
# Skills that only make sense in Claude Code (autonomous orchestration + execution +
# deploy) and should NOT ship as Desktop/web skill uploads:
SKIP = {"m_plan_roll"}
STRIP_RE = re.compile(r"(?m)^disable-model-invocation:\s*true[ \t]*\r?\n")


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".zip"):
            os.remove(os.path.join(OUT_DIR, f))

    built = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        if name in SKIP:
            continue
        sdir = os.path.join(SKILLS_DIR, name)
        if not os.path.isfile(os.path.join(sdir, "SKILL.md")):
            continue
        zpath = os.path.join(OUT_DIR, name + ".zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(sdir):
                dirs[:] = [d for d in dirs if d != "evals"]
                for fn in files:
                    fp = os.path.join(root, fn)
                    arc = os.path.relpath(fp, SKILLS_DIR).replace(os.sep, "/")
                    if fn == "SKILL.md":
                        with open(fp, encoding="utf-8") as fh:
                            txt = STRIP_RE.sub("", fh.read())
                        z.writestr(arc, txt)
                    else:
                        z.write(fp, arc)
        built.append(name)
        print("wrote", zpath)
    print("done:", len(built), "skills ->", OUT_DIR)


if __name__ == "__main__":
    build()
