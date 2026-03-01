#!/usr/bin/env bash
set -euo pipefail

# Skill Trigger Test Harness
# Validates that natural-language prompts trigger the correct Claude Code skill.
#
# Usage:
#   ./tests/trigger-test.sh                          # Run all tests
#   ./tests/trigger-test.sh --skill sse-streaming    # Test one skill
#   ./tests/trigger-test.sh --dry-run                # Show prompts without running
#   ./tests/trigger-test.sh --verbose                # Show full claude output
#   ./tests/trigger-test.sh --concurrency 3          # Run N tests in parallel

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPTS_FILE="$SCRIPT_DIR/trigger-prompts.json"
PARSER="$SCRIPT_DIR/parse-stream.mjs"
RESULTS_DIR="$SCRIPT_DIR/results"
REPORT_FILE="$RESULTS_DIR/trigger-report.md"
RESULTS_JSON="$RESULTS_DIR/trigger-results.json"

# Defaults
FILTER_SKILL=""
DRY_RUN=false
VERBOSE=false
CONCURRENCY=1

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)    FILTER_SKILL="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --verbose)  VERBOSE=true; shift ;;
    --concurrency) CONCURRENCY="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --skill NAME       Test only the named skill"
      echo "  --dry-run          Show prompts without running claude"
      echo "  --verbose          Show full claude output per test"
      echo "  --concurrency N    Run N tests in parallel (default: 1)"
      echo "  -h, --help         Show this help"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Verify dependencies
if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found in PATH" >&2
  exit 1
fi
if ! command -v node &>/dev/null; then
  echo "Error: 'node' not found in PATH" >&2
  exit 1
fi
if ! command -v jq &>/dev/null; then
  echo "Error: 'jq' not found in PATH" >&2
  exit 1
fi
if [[ ! -f "$PROMPTS_FILE" ]]; then
  echo "Error: prompts file not found: $PROMPTS_FILE" >&2
  exit 1
fi

mkdir -p "$RESULTS_DIR"

# --- Build test case list ---
# Each line: skill_name<TAB>prompt<TAB>signals_csv<TAB>expected
TESTS_FILE=$(mktemp)
trap 'rm -f "$TESTS_FILE" 2>/dev/null' EXIT

# Skill tests
SKILLS=$(jq -r '.skills | keys[]' "$PROMPTS_FILE")
for skill in $SKILLS; do
  if [[ -n "$FILTER_SKILL" && "$skill" != "$FILTER_SKILL" ]]; then
    continue
  fi
  SIGNALS=$(jq -r --arg s "$skill" '.skills[$s].signals // [] | join(",")' "$PROMPTS_FILE")
  PROMPT_COUNT=$(jq -r --arg s "$skill" '.skills[$s].prompts | length' "$PROMPTS_FILE")
  for i in $(seq 0 $((PROMPT_COUNT - 1))); do
    PROMPT=$(jq -r --arg s "$skill" --argjson i "$i" '.skills[$s].prompts[$i]' "$PROMPTS_FILE")
    printf '%s\t%s\t%s\t%s\n' "$skill" "$PROMPT" "$SIGNALS" "$skill" >> "$TESTS_FILE"
  done
done

# Negative tests (only if not filtering to a specific skill)
if [[ -z "$FILTER_SKILL" ]]; then
  NEG_COUNT=$(jq -r '.negative | length' "$PROMPTS_FILE")
  for i in $(seq 0 $((NEG_COUNT - 1))); do
    PROMPT=$(jq -r --argjson i "$i" '.negative[$i]' "$PROMPTS_FILE")
    printf '%s\t%s\t%s\t%s\n' "__negative__" "$PROMPT" "" "__none__" >> "$TESTS_FILE"
  done
fi

TOTAL=$(wc -l < "$TESTS_FILE" | tr -d ' ')
echo "=== Skill Trigger Test Harness ==="
echo "Tests to run: $TOTAL"
echo ""

# --- Dry run mode ---
if $DRY_RUN; then
  echo "--- DRY RUN (no API calls) ---"
  echo ""
  CURRENT_SKILL=""
  while IFS=$'\t' read -r skill prompt signals expected; do
    if [[ "$skill" != "$CURRENT_SKILL" ]]; then
      CURRENT_SKILL="$skill"
      echo "[$skill]"
    fi
    echo "  > $prompt"
    if [[ -n "$signals" ]]; then
      echo "    signals: $signals"
    fi
    echo "    expected: $expected"
  done < "$TESTS_FILE"
  echo ""
  echo "Total: $TOTAL test cases"
  exit 0
fi

# --- Run tests ---
PASS=0
FAIL=0
FALLBACK=0
NEG_PASS=0
NEG_TOTAL=0
TEST_NUM=0

# Initialize JSON results array
echo "[]" > "$RESULTS_JSON"

run_single_test() {
  local skill="$1" prompt="$2" signals="$3" expected="$4" test_num="$5" total="$6"

  echo "[$test_num/$total] Testing: $skill"
  echo "  Prompt: \"${prompt:0:70}$([ ${#prompt} -gt 70 ] && echo '...')\""

  # Build parser args
  local parser_args=(--expected "$expected")
  if [[ -n "$signals" ]]; then
    parser_args+=(--signals "$signals")
  fi

  # Unset CLAUDECODE to allow nested invocation, run claude
  local stream_output
  stream_output=$(
    unset CLAUDECODE
    claude -p \
      --output-format stream-json \
      --max-turns 1 \
      "$prompt" 2>/dev/null
  ) || true

  if $VERBOSE; then
    echo "  --- raw output ---"
    echo "$stream_output" | head -20
    echo "  --- end ---"
  fi

  # Parse the stream
  local result
  result=$(echo "$stream_output" | node "$PARSER" "${parser_args[@]}") || {
    echo "  ERROR: parser failed"
    result='{"skill":null,"method":"none","text_snippet":"parser error","pass":false,"status":"ERROR"}'
  }

  local status detected method snippet
  status=$(echo "$result" | jq -r '.status // "ERROR"')
  detected=$(echo "$result" | jq -r '.skill // "none"')
  method=$(echo "$result" | jq -r '.method // "none"')
  snippet=$(echo "$result" | jq -r '.text_snippet // ""' | head -c 80)

  echo "  Result: $status (detected=$detected via $method)"
  echo ""

  # Append to JSON results
  local entry
  entry=$(jq -n \
    --arg skill "$skill" \
    --arg prompt "$prompt" \
    --arg expected "$expected" \
    --arg detected "$detected" \
    --arg method "$method" \
    --arg status "$status" \
    --arg snippet "$snippet" \
    '{skill: $skill, prompt: $prompt, expected: $expected, detected: $detected, method: $method, status: $status, snippet: $snippet}')

  # Thread-safe append to results JSON
  local tmpfile
  tmpfile=$(mktemp)
  jq --argjson entry "$entry" '. + [$entry]' "$RESULTS_JSON" > "$tmpfile" && mv "$tmpfile" "$RESULTS_JSON"

  echo "$status"
}

while IFS=$'\t' read -r skill prompt signals expected; do
  TEST_NUM=$((TEST_NUM + 1))

  STATUS=$(run_single_test "$skill" "$prompt" "$signals" "$expected" "$TEST_NUM" "$TOTAL")

  case "$STATUS" in
    PASS)
      if [[ "$expected" == "__none__" ]]; then
        NEG_PASS=$((NEG_PASS + 1))
        NEG_TOTAL=$((NEG_TOTAL + 1))
      else
        PASS=$((PASS + 1))
      fi
      ;;
    FALLBACK) FALLBACK=$((FALLBACK + 1)) ;;
    FAIL|ERROR)
      if [[ "$expected" == "__none__" ]]; then
        NEG_TOTAL=$((NEG_TOTAL + 1))
      fi
      FAIL=$((FAIL + 1))
      ;;
  esac
done < "$TESTS_FILE"

# --- Generate markdown report ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SKILL_TOTAL=$((PASS + FALLBACK + FAIL))

{
  echo "# Skill Trigger Test Report"
  echo "Generated: $TIMESTAMP"
  echo ""
  echo "## Summary"
  echo "- Total: $TOTAL | Pass: $PASS | Fallback: $FALLBACK | Fail: $FAIL"
  if [[ $NEG_TOTAL -gt 0 ]]; then
    echo "- Negative (no trigger): $NEG_PASS/$NEG_TOTAL"
  fi
  echo ""
  echo "## Results"
  echo ""
  echo "| # | Skill | Prompt | Expected | Detected | Method | Status |"
  echo "|---|-------|--------|----------|----------|--------|--------|"

  ROW=0
  jq -c '.[]' "$RESULTS_JSON" | while read -r entry; do
    ROW=$((ROW + 1))
    e_skill=$(echo "$entry" | jq -r '.skill')
    e_prompt=$(echo "$entry" | jq -r '.prompt' | head -c 50)
    e_expected=$(echo "$entry" | jq -r '.expected')
    e_detected=$(echo "$entry" | jq -r '.detected')
    e_method=$(echo "$entry" | jq -r '.method')
    e_status=$(echo "$entry" | jq -r '.status')

    # Status emoji
    case "$e_status" in
      PASS)     badge="PASS" ;;
      FALLBACK) badge="FALLBACK" ;;
      FAIL)     badge="**FAIL**" ;;
      *)        badge="ERROR" ;;
    esac

    printf '| %d | %s | "%s" | %s | %s | %s | %s |\n' \
      "$ROW" "$e_skill" "$e_prompt" "$e_expected" "$e_detected" "$e_method" "$badge"
  done

  echo ""
  echo "## Failed Tests"
  echo ""

  FAIL_COUNT=$(jq '[.[] | select(.status == "FAIL" or .status == "ERROR")] | length' "$RESULTS_JSON")
  if [[ "$FAIL_COUNT" -eq 0 ]]; then
    echo "No failures."
  else
    jq -c '.[] | select(.status == "FAIL" or .status == "ERROR")' "$RESULTS_JSON" | while read -r entry; do
      f_skill=$(echo "$entry" | jq -r '.skill')
      f_prompt=$(echo "$entry" | jq -r '.prompt')
      f_expected=$(echo "$entry" | jq -r '.expected')
      f_detected=$(echo "$entry" | jq -r '.detected')
      f_snippet=$(echo "$entry" | jq -r '.snippet')
      echo "### $f_skill"
      echo "- **Prompt**: \"$f_prompt\""
      echo "- **Expected**: $f_expected"
      echo "- **Detected**: $f_detected"
      echo "- **Snippet**: $f_snippet"
      echo ""
    done
  fi
} > "$REPORT_FILE"

echo "========================================="
echo "DONE"
echo "  Pass: $PASS | Fallback: $FALLBACK | Fail: $FAIL"
if [[ $NEG_TOTAL -gt 0 ]]; then
  echo "  Negative: $NEG_PASS/$NEG_TOTAL"
fi
echo ""
echo "Report:  $REPORT_FILE"
echo "Data:    $RESULTS_JSON"
