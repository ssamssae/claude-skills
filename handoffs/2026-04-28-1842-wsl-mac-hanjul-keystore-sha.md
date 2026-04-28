---
from: wsl
to: mac
sent_at: 2026-04-28T18:42:27+09:00
status: done
done_at: 2026-04-28T18:50:00+09:00
done_note: SHA-256 추출 + 텔레그램 보고 완료 (msg id 8529). alias=upload. JDK 26 keytool withWeakConstraint formatter 버그 우회 위해 JDK 17 keytool 사용.
---

🪟 한줄일기 Android keystore SHA-256 fingerprint 미리 뽑기 (19:00 출시 사이클 사전 준비)

목표:
2026-04-28 19:00 KST 한줄일기 1,900원 양 스토어 유료 출시 사이클 진입 직전 25분 동안, Play Console 패키지 이름 사전 등록(2026-03 정식 시행 신규 정책) 폼에 즉시 복붙할 수 있도록 hanjul Android upload keystore 의 SHA-256 인증서 fingerprint 한 줄을 미리 추출해 텔레그램으로 보고해둔다. WSL 세션은 keystore SoT(Mac) 정책상 keystore 파일에 접근 못 함 (.gitignore 로 *.jks/*.keystore/key.properties 차단). 그래서 Mac 세션에서 keytool 한 번만 돌리면 됨.

목표 흐름:
이 핸드오프는 19:00 Mac 세션 본 출시 사이클의 사전 준비 단계. 본 출시 사이클은 강대종님이 19:00 KST 에 직접 트리거(`store/launch-checklist-2026-04-28.md` step 0~7) 하므로, 이 핸드오프에서 AAB 빌드·업로드·심사 제출은 절대 시작하지 않는다. SHA-256 한 줄만 뽑아 보고하고 끝.

할일:
1. cd ~/apps/hanjul && git pull --rebase --autostash 로 hanjul repo 최신화 (cc45b72 launch-checklist 포함)
2. ls android/hanjul-upload-keystore.jks 로 keystore 존재 확인 (체크리스트 0번 표 기준 Mac SoT 위치)
3. keytool 로 SHA-256 추출:
   keytool -list -v -keystore android/hanjul-upload-keystore.jks -alias upload 2>/dev/null | grep -i 'SHA256:'
   - alias 'upload' 가 아니면 -alias 인자 빼고 전체 list 후 첫 번째 항목의 SHA256 사용
   - keystore 비번 프롬프트 뜨면 1Password / 환경변수에서 읽어 입력 (인라인 답신 금지)
4. 추출한 SHA-256 fingerprint 한 줄(`SHA256: AB:CD:...:99` 형식) 을 텔레그램 reply 1통으로 보고. chat_id 538806975. 본문 첫 글자 🍎. 추가로 어떤 alias 를 사용했는지 한 줄 명시 (강대종님이 19:00 Play Console > 설정 > 개발자 계정 > Android 패키지 이름 신규 등록 폼에 그대로 복붙).
5. handoffs/2026-04-28-1842-wsl-mac-hanjul-keystore-sha-reply.md 답신 파일은 선택사항 — 텔레그램 보고만으로 충분. 작성하면 frontmatter status=done 으로 닫고 reply_to 명시.
6. 원본 핸드오프 파일(이 파일) frontmatter status 를 done 으로 갱신해서 commit + push.

금지사항:
- keystore 비밀번호 / key alias / store password 를 텔레그램 본문이나 handoffs/ 답신 파일에 인라인 금지 — 1Password 또는 ~/.claude/skills/submit-app/keystore-sot.md 에서 읽어 keytool 입력만 사용. 보고에는 SHA-256 fingerprint 와 사용한 alias 이름만 명시.
- AAB 빌드(`flutter build appbundle`) / TestFlight 업로드 / `/submit-app hanjul` 등 출시 사이클 본 단계 절대 시작하지 말 것 — 강대종님이 19:00 KST 에 직접 트리거. 이 핸드오프 범위는 SHA 한 줄 추출까지.
- Play Console / App Store Connect 웹 UI 자동화(Playwright) 진입 금지 — 강대종님이 직접 폼 작성.
- 핸드오프의 핸드오프 금지 — Mac 에서 끝내기. WSL 로 다시 던지지 말 것.
- destructive 액션(force push, rm -rf, keystore 재생성 등) 금지. keystore 비번 모르면 강대종님께 텔레그램으로 한 번 더 물어볼 것.

종료 조건:
SHA-256 fingerprint + 사용한 alias 이름이 텔레그램 chat_id 538806975 에 reply 로 도착하면 종료. 이 파일 frontmatter status=done 갱신 + commit + push 까지 완료. 강대종님이 19:00 Mac 세션 진입할 때 그 메시지 long-press 복사해서 Play Console 폼에 붙여넣을 수 있어야 함.
