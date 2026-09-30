#!/usr/bin/env bash
# Structural checks for the dev-team plugin. One FAIL line per problem; exit 1 if any.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
P="$ROOT/plugins/dev-team"
FAILS=0
fail() { echo "FAIL: $*"; FAILS=$((FAILS + 1)); }

python3 - "$ROOT" <<'PY' || fail "manifests"
import json, sys
root = sys.argv[1]
problems = []
try:
    m = json.load(open(f"{root}/.claude-plugin/marketplace.json"))
    p = json.load(open(f"{root}/plugins/dev-team/.claude-plugin/plugin.json"))
except (OSError, ValueError) as e:
    print(f"FAIL: cannot load manifests: {e}")
    sys.exit(1)
sources = {e["name"]: e["source"] for e in m["plugins"]}
if m["name"] != "personal-marketplace": problems.append("marketplace name is not personal-marketplace")
if sources.get("dev-team") != "./plugins/dev-team": problems.append("marketplace has no dev-team entry")
if "mobile-devs" in sources: problems.append("marketplace still lists mobile-devs")
if p.get("name") != "dev-team": problems.append("plugin.json name is not dev-team")
if not str(p.get("version", "")).startswith("3."): problems.append("plugin.json version is not 3.x")
for x in problems: print(f"FAIL: {x}")
sys.exit(1 if problems else 0)
PY

[ -e "$ROOT/plugins/mobile-devs" ] && fail "plugins/mobile-devs still present"
[ -e "$P/agents/orchestrator-agent.md" ] && fail "orchestrator-agent.md still present"
[ -e "$P/skills/invoke" ] && fail "skills/invoke still present"
ls "$P"/resources/migrosapp-*-code-conventions.md >/dev/null 2>&1 && fail "plugin copies of migrosapp conventions still present"

for a in spec-agent kmp-agent ios-agent android-agent backend-agent web-agent analyst-agent writer-agent spec-review-agent qa-agent docs-agent cleaner-agent; do
  f="$P/agents/$a.md"
  [ -f "$f" ] || { fail "missing agent $a"; continue; }
  grep -q "^name: $a$" "$f" || fail "$a: frontmatter name"
  grep -q '^description: ' "$f" || fail "$a: frontmatter description"
  grep -qE '^model: (haiku|sonnet|opus)$' "$f" || fail "$a: model must be an alias"
done

for s in ideate spec execute review document archive; do
  f="$P/skills/$s/SKILL.md"
  [ -f "$f" ] || { fail "missing skill $s"; continue; }
  grep -q "^name: $s$" "$f" || fail "$s: frontmatter name"
  grep -q '^description: ' "$f" || fail "$s: frontmatter description"
  grep -qE '^model: (haiku|sonnet|opus)$' "$f" || fail "$s: model must be an alias"
  if [ "$s" != ideate ]; then
    grep -q '^disable-model-invocation: true$' "$f" || fail "$s: must set disable-model-invocation: true"
  fi
done

for r in vault-conventions.md shared-implementation-process.md; do
  [ -f "$P/resources/$r" ] || fail "missing resource $r"
done

S="$P/resources/scripts"
for s in section.py frontmatter.py test_section.py test_frontmatter.py; do
  [ -f "$S/$s" ] || fail "missing script $s"
done
if [ -f "$S/section.py" ] && [ -f "$S/frontmatter.py" ]; then
  python3 -m unittest discover -s "$S" -p 'test_*.py' >/dev/null 2>&1 || fail "script unit tests fail (run: python3 -m unittest discover -s $S -p 'test_*.py')"
fi

T="$P/resources/templates"
check_ids() {
  local f="$T/$1.html"; shift
  [ -f "$f" ] || { fail "missing template $(basename "$f")"; return; }
  for id in meta "$@"; do
    grep -q "id=\"$id\"" "$f" || fail "$(basename "$f"): missing id=\"$id\""
  done
}
check_ids spec-implement goal context scope acceptance-criteria edge-cases dependencies open-questions plan
check_ids spec-analyze goal context questions scope sources output open-questions
check_ids spec-document goal context audience outline sources output open-questions
check_ids report summary answers flows risks open-questions
check_ids doc overview
check_ids review verdict runs
check_ids qa verdict runs
check_ids summary outcome changes decisions verification follow-ups links
if ls "$T"/*.html >/dev/null 2>&1; then
  styles=$(for f in "$T"/*.html; do sed -n '/<style>/,/<\/style>/p' "$f" | md5 -q; done | sort -u | wc -l | tr -d ' ')
  [ "$styles" = "1" ] || fail "templates do not share one identical <style> block"
fi

while read -r ref; do
  [ -z "$ref" ] && continue
  [ -e "$P/${ref#<PLUGIN_ROOT>/}" ] || fail "dangling reference $ref"
done < <(grep -rhoE '<PLUGIN_ROOT>/[A-Za-z0-9_./-]+' "$P" --include='*.md' 2>/dev/null | sed -E 's/[.,]+$//' | sort -u)

for pat in 'mobile-devs' 'orchestrator' '[Cc]abinet' 'claude-(opus|sonnet|haiku)-[0-9]' 'CLAUDE_PLUGIN_ROOT' '(spec|plan|review|qa)\.md'; do
  hits=$(grep -rlE "$pat" "$P" "$ROOT/README.md" 2>/dev/null | sed "s|$ROOT/||" | tr '\n' ' ')
  [ -n "$hits" ] && fail "forbidden pattern '$pat' in: $hits"
done

# Rules that close final-review findings; each must stay in the named file.
must() { grep -qF -- "$2" "$P/$1" || fail "$1: missing rule: $2"; }
must skills/execute/SKILL.md 'If `stacks` is empty for implement/ktlo'
must skills/execute/SKILL.md 'If `kmp` is in `stacks`, run ios-agent and android-agent one after the other'
must skills/execute/SKILL.md 'review PASS but QA not PASS'
must agents/docs-agent.md 'document: `goal outline`'
must agents/docs-agent.md 'Skip `qa.html` if it does not exist'
must skills/spec/SKILL.md 'add `migrosapp` to `repos`'
must resources/vault-conventions.md 'Reject an argument that contains `..` or starts with `/`'
must agents/cleaner-agent.md 'os.path.realpath'
must agents/cleaner-agent.md 'already exists → BLOCKED'

[ -f "$P/resources/visual-guide.md" ] || fail "missing resource visual-guide.md"
must resources/vault-conventions.md '## Repo preconditions'
must resources/vault-conventions.md 'REPO_OVERRIDE'
must resources/shared-implementation-process.md '"Repo preconditions"'
must agents/analyst-agent.md '"Repo preconditions"'
must agents/writer-agent.md '"Repo preconditions"'
must agents/qa-agent.md '"Repo preconditions"'
must agents/spec-review-agent.md '"Repo preconditions"'
must skills/execute/SKILL.md 'REPO_OVERRIDE'
must skills/review/SKILL.md 'REPO_OVERRIDE'
must agents/analyst-agent.md 'visual-guide.md'
must agents/writer-agent.md 'visual-guide.md'
must agents/spec-agent.md 'visual-guide.md'
must agents/docs-agent.md 'Hard rules'
must agents/docs-agent.md 'Before you hand back'

[ "$FAILS" -eq 0 ] && echo "OK: dev-team plugin checks passed"
exit $(( FAILS > 0 ))
