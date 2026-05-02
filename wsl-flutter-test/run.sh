#!/usr/bin/env bash
# wsl-flutter-test/run.sh — WSL bash 에서 Flutter analyze/test 4단계 우회 자동화
# SoT: ~/claude-skills/wsl-flutter-test/SKILL.md

set -uo pipefail

usage() {
  cat <<'EOF'
usage: run.sh <repo_path> [--analyze | --test | --both]

기본 모드: --both (analyze 후 test, analyze 실패 시 test 스킵).

WSL bash → Windows flutter 호출 시 cmd.exe pushd UNC 거부 함정 4단계 우회를
자동 처리:
  1) repo 를 Windows 측 임시 디렉토리(/mnt/c/tmp/...)로 rsync (.dart_tool/build/.git 제외)
  2) powershell.exe Set-Location 으로 Win cwd 진입 후 flutter analyze/test
  3) exit code 보존 후 임시 디렉토리 정리

exit 0 = 모든 단계 PASS / 그 외 = 첫 실패 단계의 exit code
EOF
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

REPO="$1"
MODE="${2:---both}"

if [[ ! -d "$REPO" ]]; then
  echo "ERR: repo path not a directory: $REPO" >&2
  exit 2
fi
if [[ ! -f "$REPO/pubspec.yaml" ]]; then
  echo "ERR: pubspec.yaml missing under $REPO (Flutter repo 인지 확인)" >&2
  exit 3
fi

case "$MODE" in
  --analyze|--test|--both) ;;
  *) echo "ERR: unknown mode '$MODE' (use --analyze|--test|--both)" >&2; exit 4 ;;
esac

if ! command -v rsync >/dev/null 2>&1; then
  echo "ERR: rsync not installed in WSL" >&2
  exit 5
fi
if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "ERR: powershell.exe not in PATH (WSL 환경 확인)" >&2
  exit 6
fi

BASENAME="$(basename "$(realpath "$REPO")")"
STAMP="$(date +%Y%m%d-%H%M%S)"
TMP_WSL="/mnt/c/tmp/wsl-ft-${BASENAME}-${STAMP}"
TMP_WIN="C:\\tmp\\wsl-ft-${BASENAME}-${STAMP}"

mkdir -p /mnt/c/tmp
echo "[1/4] rsync $REPO → $TMP_WSL (skip .dart_tool/build/.git)"
rsync -a \
  --exclude '.dart_tool' \
  --exclude 'build' \
  --exclude '.git' \
  "$REPO/" "$TMP_WSL/"

cleanup() {
  echo "[4/4] cleanup $TMP_WSL"
  rm -rf "$TMP_WSL"
}
trap cleanup EXIT

run_step() {
  local name="$1"
  echo "[run] flutter $name"
  powershell.exe -Command "Set-Location '$TMP_WIN'; flutter $name"
  return $?
}

EXIT=0
case "$MODE" in
  --analyze)
    echo "[2/4] flutter analyze"
    run_step analyze || EXIT=$?
    ;;
  --test)
    echo "[2/4] flutter test"
    run_step test || EXIT=$?
    ;;
  --both)
    echo "[2/4] flutter analyze"
    run_step analyze || EXIT=$?
    if [[ $EXIT -eq 0 ]]; then
      echo "[3/4] flutter test"
      run_step test || EXIT=$?
    else
      echo "[3/4] skip flutter test (analyze failed)"
    fi
    ;;
esac

echo "[done] exit=$EXIT"
exit "$EXIT"
