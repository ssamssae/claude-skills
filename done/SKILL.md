---
name: done
description: 오늘 한 일을 체크리스트 형식으로 자동 수집해 ~/daejong-page/done/YYYY-MM-DD.md 에 저장하고 홈페이지 /done 페이지에 반영한다. worklog 가 산문체 상세 기록이라면 done 은 한 눈에 파악하는 체크리스트. 사용자가 "/done", "done", "오늘 한 일 체크리스트", "체크리스트 찍어줘" 등을 말하면 이 스킬 호출.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# /done — 오늘 한 일 체크리스트

## 컨셉

- **worklog** = 산문체 상세 기록 (네이버 카페 붙여넣기 용)
- **done** = 체크박스 한 줄씩 담백하게. 한 눈에 "오늘 뭐 했나" 파악
- 두 스킬은 공존하며 서로 참조·수정하지 않는다

## 실행 흐름

### 1. 날짜 결정
- 인자로 `YYYY-MM-DD` 가 주어지면 그 날짜
- 없으면 오늘 KST: `date +%Y-%m-%d`
- 이후 `TARGET_DATE` 로 지칭

### 2. 데이터 수집 (자동)

**(A) 프로젝트별 git 커밋 (오늘, KST 기준)**
```bash
for repo in ~/simple_memo_app ~/daejong-page ~/todo ~/claude-skills ~/yakmukja ~/dutch_pay_calculator ~/babmeokja; do
  [ -d "$repo/.git" ] || continue
  git -C "$repo" log --since="TARGET_DATE 00:00 +0900" --until="TARGET_DATE 23:59 +0900" --pretty=format:"%s" --all 2>/dev/null
done
```

**(B) todos.md 에서 오늘 완료된 항목**
- `~/todo/todos.md` 의 `## 완료` 섹션에서 `(완료: TARGET_DATE)` 가 포함된 줄만

**(C) 이 세션 주요 액션**
- 대화 컨텍스트에서 오늘 수행한 주요 작업 (세션이 텔레그램 드롭 해결, 인프라 수정 등)
- 단순 질문/잡담은 제외, 의미 있는 결과물만

### 3. 카테고리 분류

자동으로 그룹핑:
- **메모요**: simple_memo_app 커밋
- **daejong-page**: daejong-page 커밋 (단, 오늘 생성된 done/ worklog/ 파일은 제외 — 메타 작업은 별도)
- **할일**: todo 커밋 + todos.md 완료 항목
- **인프라/도구**: ~/.claude 하위 변경, 스킬, 훅, settings, claude-skills
- **기타**: 위 카테고리에 안 맞는 것 (dutch_pay_calculator, yakmukja 등은 해당 앱명 단독 섹션)

### 4. 파일 작성

저장 경로: `~/daejong-page/done/YYYY-MM-DD.md`

**파일명 규칙**: 같은 날짜 중복 호출 시 이전 파일을 **덮어쓰기** (worklog 처럼 버전 스냅샷 안 만듦 — 가장 최신 상태 하나만).

포맷:
```markdown
# TARGET_DATE done

## 메모요
- [x] 첫 번째 커밋 제목
- [x] 두 번째 커밋 제목

## daejong-page
- [x] ...

## 할일 완료
- [x] ...

## 인프라/도구
- [x] ...

## 기타
(필요시)
```

주의:
- 커밋 제목이 길면 `feat: abc 추가` → `abc 추가` 정도로 접두사 정리
- 중복(같은 날 같은 내용 여러 커밋) 은 한 줄로 합치기
- 이모지/URL 금지

### 5. index.json 갱신

파일: `~/daejong-page/done/index.json`

구조:
```json
{
  "entries": [
    {
      "file": "YYYY-MM-DD.md",
      "date": "YYYY-MM-DD",
      "summary": "한 줄 요약 (해당 파일의 주요 카테고리나 건수)",
      "count": 12,
      "updated": "ISO 8601 KST"
    }
  ]
}
```

- 같은 `file` 이 이미 있으면 **갱신** (count, summary, updated 덮어쓰기)
- 없으면 상단에 추가 (최신순)
- entries 전체 정렬: date 내림차순

### 6. 수동 추가 지원

사용자가 `/done 오늘 병원 다녀옴` 처럼 인자를 넘기면:
- 자동 수집 결과에 추가로 "기타" 섹션에 해당 문장을 체크박스로 추가
- 여러 건은 쉼표 또는 줄바꿈으로 구분

### 7. 커밋 & 푸시

daejong-page 저장소에만 커밋:
```bash
cd ~/daejong-page
git add done/YYYY-MM-DD.md done/index.json
git commit -m "done: YYYY-MM-DD"
git push origin main
```

### 8. 결과 응답

텔레그램 세션이면 reply 도구로 체크리스트 전문 전송.
파일 본문 그대로 복사해서 보내도 되고, 앞에 "오늘의 done 체크리스트" 헤딩만 붙여도 된다.

마지막 줄에 홈페이지 링크 1줄:
`https://ssamssae.github.io/daejong-page/done.html`

## 주의사항

- 이미 커밋된 파일(오늘 done.md 가 있다면) 덮어쓰기 전에 읽어서 수동 추가된 항목이 유실되지 않게 할 것. 병합 로직: 이전 파일의 수동 추가 항목 유지 + 자동 수집 갱신
- 쓸데없이 길게 만들지 말 것. 전체 20줄 이내 목표
- "학습/상담" 같은 질문성 작업은 제외 — 체크리스트는 "한 것" 만
