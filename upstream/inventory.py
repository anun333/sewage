#!/usr/bin/env python3
"""inventory.py - the context of one intended upstream change, so it is proposed with all of it in view.

  python3 -I upstream/inventory.py REPO HEAD [--base REF] [--gh OWNER/REPO] [--draft FILE]

REPO is a clone of the upstream project; HEAD is the commit (or branch) with our change; BASE
(default origin/HEAD's branch) is what it goes into. --gh names the GitHub repository, for the
checks that read open PRs and issues. --draft is our issue or PR text, whose references are
checked. Read-only: git and gh only, nothing is checked out or built.

For the C, C++, SWIG and Python projects sewage contributes to. Each check prints a control,
so that a "none" is a real none:
  I. Place: each changed file's layer (upstream/inventory-profiles.json) and its neighbours.
  F. Functions the diff changes, and their callers two levels up, across languages (a C++
     method called from Python through SWIG counts).
  T. What should change together, by the project's profile, and whether the diff does.
  S. Shared state: names the diff assigns that other files also use.
  P. Parallel paths: other files that share the change's distinctive strings and identifiers,
     the same job done somewhere else.
  N. Tests next door: test files that use the changed functions, classes or files.
  O. Other open PRs changing the same files, and the same functions (--gh).
  L. Open issues that name the changed functions, files or folders (--gh).
  M. Recent history of the changed files, and who wrote it.
  C. Our draft's claims (--draft): every path:line reference and every backticked name or path
     exists at the commit it is about.
Matching is by name and pattern, not by a compiler: read what it lists before relying on it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

C_LIKE = (".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".i")
SOURCES = ("*.c", "*.h", "*.cpp", "*.hpp", "*.cc", "*.cxx", "*.i", "*.py", "*.pyx")
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "else", "do", "case", "catch", "defined"}
COMMON = {"i", "j", "k", "n", "m", "x", "y", "z", "s", "r", "t", "v", "c", "f", "p", "a", "b", "e", "rc", "err", "errcode",
          "result", "results", "res", "value", "val", "data", "df", "self", "ndx", "index", "name", "args", "kwargs", "msg",
          "out", "ret", "tmp", "line", "lines", "text", "key", "item", "items", "row", "col", "count", "size", "len"}
GENERIC_FUNCS = {"main", "run", "get", "set", "__init__", "init", "solve", "build", "initialize", "evaluate", "update", "close", "open"}
GENERIC_DIRS = {"src", "lib", "include", "test", "tests", "core", "common", "util", "utils", "docs", "documentation", "doc",
                "examples", "scripts", "solver", "python", "cpp"}


def git(repo: Path, *args: str, check: bool = False) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, errors="replace")
    if check and r.returncode != 0:
        sys.exit("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def grep(repo: Path, ref: str, pattern: str, paths: tuple[str, ...] = SOURCES, flags: tuple[str, ...] = ()) -> list[tuple[str, int, str]]:
    """(path, line, text) for each match of an extended regex at REF."""
    out = git(repo, "grep", "-n", "-I", *flags, "-E", pattern, ref, "--", *paths)
    hits = []
    for l in out.split("\n"):
        parts = l.split(":", 3)
        if len(parts) == 4 and parts[2].isdigit():
            hits.append((parts[1], int(parts[2]), parts[3]))
    return hits


def is_comment(path: str, text: str) -> bool:
    s = text.strip()
    if path.endswith(".py"):
        return s.startswith("#")
    return s.startswith(("//", "/*", "*"))


def profile_for(repo: Path) -> dict:
    url = git(repo, "remote", "get-url", "origin").strip()
    profiles = json.loads((Path(__file__).with_name("inventory-profiles.json")).read_text())["projects"]
    return next((p for p in profiles if p["match"].lower() in url.lower()),
                {"name": "unknown (%s)" % url, "layers": [["other", ""]], "together": [], "tests": "test", "docs": "^docs/|\\.md$",
                 "pr_template": "not recorded"})


def layer_of(profile: dict, path: str) -> str:
    return next((name for name, pat in profile["layers"] if re.search(pat, path)), "other")


C_DEF = re.compile(r"^(?!\s)(?:[A-Za-z_][\w\s\*&:<>,~]*?\s+[\*&]*|)~?((?:\w+::)*~?\w+)\s*\([^;]*$")
PY_DEF = re.compile(r"^(\s*)(?:async\s+)?def\s+(\w+)\s*\(")
PY_CLASS = re.compile(r"^(\s*)class\s+(\w+)")


def enclosing(path: str, lines: list[str], no: int) -> tuple[str | None, str | None]:
    """(function, class) around line NO (1-based) of a file, by pattern."""
    if path.endswith(".py"):
        cur_indent = len(lines[no - 1]) - len(lines[no - 1].lstrip()) if no - 1 < len(lines) else 0
        fn = cls = None
        for i in range(no - 1, -1, -1):
            m = PY_DEF.match(lines[i])
            if m and fn is None and (len(m.group(1)) < cur_indent or i == no - 1):
                fn, fn_indent = m.group(2), len(m.group(1))
                cur_indent = fn_indent
                continue
            c = PY_CLASS.match(lines[i])
            if c and fn is not None and len(c.group(1)) < cur_indent:
                cls = c.group(2)
                break
            if c and fn is None:
                break
        return fn, cls
    if path.endswith(C_LIKE):
        for i in range(no - 1, -1, -1):
            l = lines[i]
            if i < no - 1 and re.match(r"^}", l):
                return None, None  # the line sits between functions
            m = C_DEF.match(l)
            if m and not l.rstrip().endswith(";"):
                full = m.group(1)
                name = full.split("::")[-1]
                if name in KEYWORDS:
                    continue
                return name, (full.split("::")[-2] if "::" in full else None)
    return None, None


def changed_lines(repo: Path, base: str, head: str, path: str) -> tuple[set[int], set[int]]:
    """Line numbers changed at head, and at base, for one file."""
    new: set[int] = set()
    old: set[int] = set()
    for h in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", git(repo, "diff", "--unified=0", f"{base}...{head}", "--", path), re.M):
        os_, oc, ns, nc = int(h.group(1)), int(h.group(2) or "1"), int(h.group(3)), int(h.group(4) or "1")
        new.update(range(ns, ns + max(nc, 1)) if nc else [ns])
        old.update(range(os_, os_ + max(oc, 1)) if oc else [os_])
    return new, old


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repo")
    ap.add_argument("head")
    ap.add_argument("--base")
    ap.add_argument("--gh", help="OWNER/REPO on GitHub, for open PRs and issues")
    ap.add_argument("--draft", help="our issue or PR text, whose references are checked")
    a = ap.parse_args()
    repo = Path(a.repo).expanduser()
    if not a.base:
        a.base = git(repo, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD").strip() or "origin/main"
    base = git(repo, "merge-base", a.base, a.head, check=True).strip()
    head = git(repo, "rev-parse", a.head, check=True).strip()
    prof = profile_for(repo)
    files = [f for f in git(repo, "diff", "--name-only", f"{base}...{head}").split("\n") if f]
    tree = [f for f in git(repo, "ls-tree", "-r", "--name-only", head).split("\n") if f]
    diff = git(repo, "diff", f"{base}...{head}")
    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in diff.split("\n") if l.startswith("-") and not l.startswith("---")]
    context = [l[1:] for l in diff.split("\n") if l.startswith(" ")]
    tests_re = re.compile(prof["tests"])

    print(f"# Change inventory: {head[:10]} against {a.base} (merge base {base[:10]})\n")
    print(f"Project profile: {prof['name']}. {len(files)} files changed, {len(added)} lines added, {len(removed)} removed.")
    print(f"PR template: {prof['pr_template']}.\n")

    # I. Place.
    print("## I. Where it sits\n")
    sample = next((f for f in tree if re.search(prof["layers"][0][1], f)), None)
    print(f"Control: `{sample}` is placed in `{layer_of(prof, sample) if sample else '-'}` "
          f"(the profile's first layer, {prof['layers'][0][0]}).\n")
    for f in files:
        folder = f.rsplit("/", 1)[0] if "/" in f else ""
        sib = [x for x in git(repo, "ls-tree", "--name-only", f"{head}:{folder}" if folder else head).split("\n") if x]
        print(f"- `{f}`: {layer_of(prof, f)}; {len(sib)} entries beside it in `{folder or '.'}/`.")

    # F. Functions changed and their callers.
    print("\n## F. Functions the diff changes, and their callers two levels up\n")
    changed: dict[str, dict] = {}
    for f in files:
        if not f.endswith(C_LIKE + (".py",)):
            continue
        new, old = changed_lines(repo, base, head, f)
        for ref, nos in ((head, new), (base, old)):
            text = git(repo, "show", f"{ref}:{f}").split("\n")
            for no in sorted(nos):
                if no - 1 < len(text):
                    fn, cls = enclosing(f, text, no)
                    if fn:
                        e = changed.setdefault((cls or "") + "." + fn if cls else fn, {"files": set(), "class": cls, "name": fn})
                        e["files"].add(f)

    def callers(name: str, cls: str | None, def_files: set[str]) -> list[tuple[str, str, str | None]]:
        if name == "__init__" and not cls:
            return []  # a constructor of unknown class: its callers can't be told apart
        pat = rf"(^|[^\w]){re.escape(cls if name == '__init__' and cls else name)}\s*\("
        found = set()
        stems = {Path(d).stem for d in def_files}
        for path, no, text in grep(repo, head, pat):
            if is_comment(path, text) or tests_re.search(path) or re.match(r"\s*class\s", text):
                continue
            if re.search(rf"\bdef\s+{re.escape(name)}\b", text) or (path.endswith(C_LIKE) and C_DEF.match(text) and not text.rstrip().endswith(";") and re.search(rf"\b{re.escape(name)}\s*\(", text)):
                continue
            if name in GENERIC_FUNCS or len(name) < 5:
                whole = git(repo, "show", f"{head}:{path}")
                if path not in def_files and not any(re.search(rf"\b{re.escape(s)}\b", whole) for s in stems | ({cls} if cls else set())):
                    continue  # a same-named function elsewhere
            if path.endswith((".h", ".hpp", ".i")) and text.rstrip().endswith(";"):
                found.add((path, "(declaration)", None))
                continue
            lines = git(repo, "show", f"{head}:{path}").split("\n")
            fn, fcls = enclosing(path, lines, no)
            found.add((path, fn or "(file scope)", fcls))
        return sorted(found, key=lambda c: (c[0], c[1], c[2] or ""))

    first_callers: dict[str, list] = {}
    print("Callers are matched by name at the head, tests left out (see N). A method of a common name counts only in files that "
          "name its file or class. Check each by reading it.\n")
    for key in sorted(changed):
        e = changed[key]
        name = e["name"]
        shown_name = e["class"] if name == "__init__" and e["class"] else name
        defs = [h for h in grep(repo, head, rf"(\bdef\s+{re.escape(name)}\b|\b{re.escape(shown_name)}\s*\()") if not is_comment(h[0], h[2])]
        first = [c for c in callers(name, e["class"], e["files"]) if c[1] != name or c[0] not in e["files"]]
        first_callers[key] = first
        outside = [c for c in first if c[0] not in files]
        print(f"- `{key}()` in {', '.join(f'`{x}`' for x in sorted(e['files']))}: "
              f"{len(first)} caller(s), {len(outside)} outside the diff. Control: {len(defs)} line(s) name it.")
        for path, fn, fcls in first[:8]:
            up = [f"`{p}`:{(c + '.') if c else ''}{g}" for p, g, c in callers(fn, fcls, {path}) if g != "(declaration)"][:5] \
                if fn not in ("(file scope)", "(declaration)") else []
            print(f"  - `{path}` in `{(fcls + '.') if fcls else ''}{fn}`" + (f"; called from {', '.join(up)}" if up else ""))
    if not changed:
        print("- No function found around the changed lines (data, build or documentation files only).")

    # T. Together.
    print("\n## T. What should change together (the project's profile)\n")
    rules = [r for r in prof["together"] if any(re.search(r[0], f) for f in files)]
    print(f"Control: {len(prof['together'])} rules in the profile, {len(rules)} triggered by this diff.\n")
    for when, check, why in rules:
        trig = [f for f in files if re.search(when, f)]
        targets = []
        for t in trig:
            m = re.search(when, t)
            pat = m.expand(check) if m and "\\1" in check else check
            targets += [x for x in tree if re.search(pat, x)]
        targets = sorted(set(targets) - set(trig))
        touched = [x for x in targets if x in files]
        print(f"- {why}: {len(targets)} file(s) at head, {len(touched)} changed by the diff"
              + (f". Not changed: {', '.join(f'`{x}`' for x in sorted([x for x in targets if x not in files], reverse=True)[:4])}"
                 + (" and more" if len(targets) - len(touched) > 4 else "") if len(targets) > len(touched) else "") + ".")

    # S. Shared state.
    print("\n## S. Shared state: names the diff assigns that other files use\n")
    assign = re.compile(r"(?:^|[;{(\s])((?:self\.)?[A-Za-z_]\w*)(?:\[[^\]]*\]|->\w+|\.\w+)*\s*(?:[-+*/|&]?=)(?!=)")
    names = sorted({m.group(1).split(".")[-1] for l in added + removed for m in assign.finditer(l)} - COMMON)
    c_text = "\n".join(git(repo, "show", f"{head}:{f}") for f in files if f.endswith(C_LIKE))
    local_decl = r"^[ \t]+(?:static\s+|const\s+|unsigned\s+|signed\s+)*(?:int|long|short|char|float|double|size_t|bool|auto|std::\w+(?:<[^;]*>)?|\w+\s*\*)\s+[^;=(]*\b%s\b"
    locals_ = [n for n in names if re.search(local_decl % re.escape(n), c_text, re.M)]
    shown = 0
    for n in names:
        if len(n) < 4 or n in locals_:
            continue
        users = sorted({p for p, _, t in grep(repo, head, rf"\b{re.escape(n)}\b") if not is_comment(p, t)})
        others = [u for u in users if u not in files and not tests_re.search(u)]
        if others:
            shown += 1
            print(f"- `{n}`: {len(others)} other file(s): {', '.join(f'`{u}`' for u in others[:6])}{' and more' if len(others) > 6 else ''}")
    print(f"\nControl: {len(names)} names assigned in changed lines; {len(locals_)} are locals of the changed C/C++ files "
          f"({', '.join(locals_) or 'none'}), left out; {shown} of the rest also used outside the diff.")

    # P. Parallel paths.
    print("\n## P. Parallel paths: other files sharing the change's distinctive strings and names\n")
    pool = added + removed + context
    lit = re.compile(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'')
    strings = {x for l in pool for m in lit.finditer(l) for x in [m.group(1) or m.group(2) or ""]
               if 6 <= len(x) <= 80 and not re.fullmatch(r"[\s\W\d]*", x)}
    # a path in a string is shared as its folders too: "lib/linux-x64/a.so" and "lib/linux-x64/b.so" are one place
    strings |= {"/".join(x.split("/")[:k]) for x in list(strings) if "/" in x for k in range(2, x.count("/") + 1)
                if len("/".join(x.split("/")[:k])) >= 8}
    code_like = re.compile(r"_|[a-z][A-Z]|[A-Z]{2}|\d")
    names_changed = {e["name"] for e in changed.values()}
    idents = {w for l in pool for w in re.findall(r"\b[A-Za-z_]\w{7,}\b", l) if code_like.search(w[1:])} - names_changed
    hits: dict[str, set[str]] = {}
    tried = 0
    for tok in sorted(strings) + sorted(idents):
        pat = re.escape(tok)
        found = {p for p, _, t in grep(repo, head, pat, paths=("*",), flags=("-F",) if tok in strings else ()) if tok in t}
        tried += 1
        if 1 <= len(found) <= 15:
            for p in found:
                if p not in files and not tests_re.search(p):
                    hits.setdefault(p, set()).add(tok)
    print(f"Control: {tried} distinctive tokens searched (strings of 6+ characters and their folders, and names of 8+ in the "
          f"changed and context lines); a token in more than 15 files is too common to count. Files in the change's own "
          f"language come first.\n")
    langs = {Path(f).suffix for f in files if f.endswith(C_LIKE + (".py",))}
    for p, toks in sorted(hits.items(), key=lambda kv: (Path(kv[0]).suffix not in langs, -len(kv[1]), kv[0]))[:12]:
        print(f"- `{p}` ({layer_of(prof, p)}): shares {len(toks)}: {', '.join(f'`{t}`' for t in sorted(toks)[:5])}")
    if not hits:
        print("- No other file shares them.")

    # N. Tests next door.
    print("\n## N. Tests next door\n")
    all_tests = [t for t in tree if tests_re.search(t)]
    print(f"Control: {len(all_tests)} test files at head; the diff changes {len([f for f in files if tests_re.search(f)])} of them.\n")
    subjects = sorted(({e["name"] for e in changed.values()} - GENERIC_FUNCS) | {e["class"] for e in changed.values() if e["class"]} |
                      {Path(f).stem for f in files if not tests_re.search(f) and f.endswith(C_LIKE + (".py",)) and len(Path(f).stem) > 3})
    for s in subjects:
        ts = sorted({p for p, _, _ in grep(repo, head, rf"\b{re.escape(s)}\b", paths=("*",)) if tests_re.search(p)})
        if ts:
            print(f"- `{s}`: {len(ts)} test file(s): {', '.join(f'`{t}`' for t in ts[:5])}{' and more' if len(ts) > 5 else ''}")
        else:
            print(f"- `{s}`: no test file names it.")

    # O and L need GitHub.
    if a.gh:
        print("\n## O. Other open PRs changing the same files, and the same functions\n")
        r = subprocess.run(["gh", "pr", "list", "--repo", a.gh, "--state", "open", "--limit", "100",
                            "--json", "number,title,author,updatedAt"], capture_output=True, text=True)
        prs = json.loads(r.stdout or "[]") if r.returncode == 0 else []
        print(f"Control: {len(prs)} open PRs read.\n")
        if r.returncode != 0:
            print("**Incomplete: the open PRs couldn't be listed, so a \"None\" below proves nothing. Run it again.**\n")
        overlap = unread = 0
        for pr in prs:
            rf = subprocess.run(["gh", "api", f"repos/{a.gh}/pulls/{pr['number']}/files", "--paginate"],
                                capture_output=True, text=True)
            if rf.returncode != 0:
                unread += 1
                continue
            same = [x for x in json.loads(rf.stdout or "[]") if x.get("filename") in files]
            if not same:
                continue
            overlap += 1
            ctx = {m.group(1) for x in same for m in re.finditer(r"^@@[^@]*@@\s*(.*)$", x.get("patch", ""), re.M)}
            fns = sorted({n for n in changed if any(re.search(rf"\b{re.escape(n)}\b", c) for c in ctx)})
            print(f"- #{pr['number']} ({pr['author']['login']}, updated {pr['updatedAt'][:10]}): {pr['title'][:70]}. "
                  f"Same files: {', '.join('`%s`' % x['filename'] for x in same)}; same functions: {', '.join(fns) or 'none seen'}.")
        if not overlap:
            print("- None changes the same files.")
        if unread:
            print(f"\n**Incomplete: the files of {unread} of {len(prs)} PRs couldn't be read. Run it again.**")
        print("\n## L. Open issues that name the changed functions, files or folders\n")
        # An issue often names only the part of the project ("the METAB flowsheet"), so the
        # changed files' own folders are searched too, unless generic or the top-level package.
        top = {f.split("/")[0] for f in files}
        folders = sorted({d for d in (Path(f).parent.name for f in files if not tests_re.search(f))
                          if d and d not in top and d.lower() not in GENERIC_DIRS})
        terms = list(dict.fromkeys(
            [n for n in sorted({e["name"] for e in changed.values()}) if n not in GENERIC_FUNCS and len(n) > 6][:6] +
            [Path(f).name for f in files if not tests_re.search(f)][:4] + folders[:3]))
        seen: dict[int, str] = {}
        answered = 0
        common: list[str] = []
        for t in terms:
            r = subprocess.run(["gh", "search", "issues", "--repo", a.gh, "--state", "open", "--limit", "11",
                                "--json", "number,title,isPullRequest", t], capture_output=True, text=True)
            if r.returncode == 0:
                answered += 1
                found = json.loads(r.stdout or "[]")
                if t in folders and len(found) > 10:
                    common.append(t)
                    continue
                for it in found[:10]:
                    if not it.get("isPullRequest"):
                        seen.setdefault(it["number"], it["title"])
        print(f"Control: {answered} of {len(terms)} searches answered ({', '.join(f'`{t}`' for t in terms)}).\n")
        if answered < len(terms):
            print("**Incomplete: not every search answered (GitHub allows 30 searches a minute), so a \"None\" "
                  "below proves nothing. Run it again.**\n")
        if common:
            print(f"Folders too common to count (more than 10 open issues and PRs name them): "
                  f"{', '.join(f'`{t}`' for t in common)}.\n")
        for n_, t in sorted(seen.items()):
            print(f"- #{n_}: {t[:100]}")
        if not seen:
            print("- None.")

    # M. Recent history.
    print("\n## M. Recent history of the changed files (365 days on the base)\n")
    src = [f for f in files if not tests_re.search(f)]
    log = git(repo, "log", "--since=365.days", "--format=%h\t%ad\t%an\t%s", "--date=short", a.base, "--", *src) if src else ""
    entries = [l.split("\t") for l in log.split("\n") if l]
    who: dict[str, int] = {}
    for e in entries:
        who[e[2]] = who.get(e[2], 0) + 1
    print(f"Control: {len(entries)} commits on `{a.base}` touched these {len(src)} files in 365 days.\n")
    if who:
        print("- Who: " + ", ".join(f"{k} ({v})" for k, v in sorted(who.items(), key=lambda kv: -kv[1])[:8]) + ".")
    for e in entries[:8]:
        print(f"- {e[0]} {e[1]} {e[2]}: {e[3][:100]}")

    # C. The draft's claims.
    if a.draft:
        print("\n## C. Our draft's references\n")
        if not Path(a.draft).is_file():
            print(f"- `{a.draft}` is not a file.")
            return 2
        text = Path(a.draft).read_text()
        refs = sorted(set(re.findall(r"`?([\w./-]+\.(?:c|h|cpp|hpp|i|py|rst|md|txt|csv|toml|yml|cfg|inp))(?![\w])(?::(\d+)(?:-(\d+))?)?`?", text)))
        bad = 0
        for path, l1, l2 in refs:
            cand = [x for x in tree if x == path or x.endswith("/" + path)]
            if not cand:
                bad += 1
                print(f"- `{path}`: not found at head.")
                continue
            if l1:
                lines = git(repo, "show", f"{base}:{cand[0]}").split("\n")
                lo, hi = int(l1), int(l2 or l1)
                if hi > len(lines):
                    bad += 1
                    print(f"- `{path}:{l1}{'-' + l2 if l2 else ''}`: the base has only {len(lines)} lines.")
                else:
                    print(f"- `{path}:{l1}{'-' + l2 if l2 else ''}` at the base reads: `{' / '.join(x.strip() for x in lines[lo - 1:hi])[:150]}`")
        names = sorted({n for n in re.findall(r"`([A-Za-z_][\w.]*)(?:\(\))?`", text) if len(n) > 3 and not re.search(r"\.(c|h|py|cpp|hpp|md|txt|csv)$", n)})
        missing = [n for n in names if not grep(repo, head, rf"\b{re.escape(n.split('.')[-1])}\b", paths=("*",))]
        planted = "zz_no_such_name_qq"
        control_ok = not grep(repo, head, rf"\b{planted}\b", paths=("*",))
        print(f"\nControl: the planted name `{planted}` is {'not found, as it must be' if control_ok else 'FOUND: the name check is broken'}. "
              f"{len(refs)} path references ({bad} not found); {len(names)} backticked names, {len(missing)} not found at head"
              + (f": {', '.join(f'`{m}`' for m in missing)}" if missing else "") + ".")
        print("Names not found may be fine (a PR's new names, other projects', prose in backticks): read each.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
