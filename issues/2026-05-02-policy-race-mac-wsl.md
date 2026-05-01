---
prevention_deferred: null
---

# 본진·WSL 가 globals/CLAUDE.md 를 stale-on-stale 로 동시 수정 — 「지휘관 1명 원칙」 폐기 사이클의 race

- **발생 일자:** 2026-05-02 01:27 KST (WSL eedef42 직접 push) → 01:58 KST (본진 PR #4 1405ad1 squash 머지)
- **해결 일자:** 2026-05-02 01:58 KST (본진 PR #4 안에서 의도적으로 8항 풀 정책으로 통합)
- **심각도:** medium (정책 파일 → 잘못 통합되면 두 작업자 행동 룰 자체가 깨짐)
- **재발 가능성:** medium (정책 갱신 사이클 또는 같은 파일 동시 작업 발생 시 동일 패턴)
- **영향 범위:** claude-skills repo `globals/CLAUDE.md` + `globals/AGENT.md`, 본진/WSL 룰 자체

## 증상

5/2 새벽 강대종이 「지휘관 1명 원칙」 폐기 직후 본진·WSL 양쪽이 같은 파일 `globals/CLAUDE.md` 를 거의 동시에 수정.

1. **01:27:24 KST — WSL eedef42** (main 직접 push): 「지휘관 1명 원칙」 섹션(L38-51) 통째 제거 + 「역할 분담」 3줄 요약으로 대체. WSL 자율 제안 OK + 본진 결정권 유지 한 줄.
2. **01:58:07 KST — 본진 PR #4 1405ad1** (squash 머지, 브랜치 e7b334c): 같은 파일에 8항 풀 정책 (병렬 / 작업명 / 브랜치 분리 / 파일 충돌 방지 / store/* / 동기화 / 충돌 / self-mod) 작성 + 역할 분담 보존. WSL 의 3줄 요약 위에 풀 정책으로 덮어씀.

git 머지 충돌은 0 (본진 PR #4 의 base 가 WSL push 후 시점이었거나 squash 머지가 자동 정리). 그러나 같은 파일을 같은 31분 윈도 안에 양쪽이 수정한 race 는 사실.

## 원인

1. **「지휘관 1명 원칙」 폐기 사이클이 본진/WSL 양쪽에 동시 도착** — 강대종 directive 가 양 기기에 거의 동시에 흘러갔고, 양쪽 다 자기 페이스로 같은 파일 작업 시작.
2. **WSL 가 main 직접 push** — 정책상 WSL 는 wsl/* 브랜치 + PR 흐름이지만, 「3줄 요약 폐기」를 main 직접 push 로 처리. 작업 시작 전 본진이 같은 파일 작업 중인지 텔레그램 선언/확인 절차 부재.
3. **본진은 PR #4 흐름이지만 base 가 WSL eedef42 후로 자동 갱신됨** — 본진 e7b334c 가 WSL push 후에 만들어졌거나, PR squash 시점에 base 가 최신으로 fetch 되어 자동으로 WSL 변경 위에 얹힘. 결과적으로 충돌 0, 그러나 WSL 의 3줄 요약은 본진 풀 정책으로 의도적 덮어쓰기.
4. **「같은 파일 동시 수정 금지」 룰이 사고 시점엔 없었음** — 5/1 race 후 도입 deferred 상태. 사고 직후 강대종이 새 8항 정책 #4 「파일 충돌 방지」를 본진 PR #4 안에 박아 forcing function 으로 설치.

## 조치

본진 PR #4 1405ad1 안에서 한 번에 통합:

- WSL eedef42 의 3줄 요약 → 풀 8항 정책으로 흡수 (역할 분담 섹션은 보존, WSL 자율 OK 보존)
- 새 정책 #4 「파일 충돌 방지」 도입 — 작업 시작 전 git fetch + 수정 예정 파일 텔레그램 선언 + 같은 파일 즉시 중단 + 강대종 결정 위임
- 새 정책 #6 「동기화 규칙」 도입 — 작업 시작/종료 시 작업자명·작업명·브랜치명·수정 예정 파일 텔레그램 보고
- 새 정책 #8 「자기 정책 수정 권한」 도입 — 본 정책 자체 수정은 강대종 명시 1회 권한 부여 시에만, SCOPE 한정

이번 사이클은 강대종 directive 「본진 self-mod 1회 권한」 으로 본진이 직접 정책 통합. 후속 손실 0.

## 예방 (Forcing function 우선)

이미 본진 PR #4 1405ad1 머지 시점에 forcing function 박힘:

1. **(설치 완료) 정책 #4 「파일 충돌 방지」** — 작업 시작 전 `git fetch` + 수정 예정 파일 텔레그램 선언 의무. 다른 작업자가 이미 선언한 파일은 수정 금지. 같은 파일을 건드려야 하면 즉시 중단 + 강대종 확인.
2. **(설치 완료) 정책 #6 「동기화 규칙」** — 작업 시작/종료 시 작업자명·작업명·브랜치명·수정 예정 파일 텔레그램 보고. 양쪽 작업자가 서로 무엇을 만지는지 가시화.
3. **(설치 완료) 정책 #3 「main 직접 push 금지 + PR 없이 main 반영 금지」** — WSL eedef42 같은 main 직접 push 자체를 정책 레벨에서 금지. 다음에 같은 사이클이 와도 PR 흐름 강제.
4. **(추가 후보) wsl-directive.sh / mac-report.sh 양 운반체에 「작업 시작 시점 main HEAD SHA 자동 첨부」** — 5/1 race 후 wsl-directive.sh 에 한 번 박힘 (b440f27, 21:46 KST). mac-report.sh 거울 추가는 deferred. 다음 race 발생 시 추가.

## 재발 이력

<생성 시 비어있음. 다음 같은 패턴 발생 시 한 줄 추가>

## 관련 링크

- 커밋: WSL `eedef42` (01:27:24 KST), 본진 PR #4 `1405ad1` (01:58:07 KST), PR 브랜치 commit `e7b334c`
- 직전 race 이슈: [`2026-05-01-wsl-mac-race-skill-edit.md`](2026-05-01-wsl-mac-race-skill-edit.md) — 5/1 race 가 forcing function (a)(b)(c) surface 한 직전 사고
- 정책 파일: `globals/CLAUDE.md` (8항 풀 정책), `globals/AGENT.md` (운영 상세)
- 메모리: 본진 self-mod 1회 권한 직전 결정
- todos: someday `~/todo/someday.md` "정책 race 사고 issue 기록" 항목 → 본 issue 로 closure
