#!/usr/bin/env python3
"""
코레일 KTX 207 자동예매 봇
- Playwright로 코레일 세션 유지 (토큰 자동 생성)
- page.route()로 Device=BH → Device=IP 교체 (봇감지 우회)
- 3분 주기 폴링, 예약가능 시 즉시 예매, 텔레그램 알림

실행: python3 korail_bot.py
필요 파일:
  ~/.claude/secrets/korail_storage.json  — Playwright storageState (로그인 세션)
환경변수:
  TELEGRAM_BOT_TOKEN  — 텔레그램 봇 토큰
  TELEGRAM_CHAT_ID    — 수신 chat_id (기본: 538806975)
"""

import asyncio, json, os, sys, urllib.request
from datetime import datetime
from playwright.async_api import async_playwright

# ── 설정 ────────────────────────────────────────────────────────────────────
TARGET_DATE   = "20260523"
TARGET_TRN_NO = "207"        # KTX 207  09:04 서울→진영
TARGET_DPT_TM = "090400"
TARGET_STN_S  = "서울"
TARGET_STN_E  = "진영"
STN_CD_S      = "0001"       # 서울역 코드
STN_CD_E      = "0056"       # 진영역 코드
POLL_SEC      = 180          # 3분
BASE_URL      = "https://smart.letskorail.com"
SESSION_FILE  = os.path.expanduser("~/.claude/secrets/korail_storage.json")
TG_TOKEN      = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT       = os.environ.get("TELEGRAM_CHAT_ID", "538806975")

# ── 텔레그램 ────────────────────────────────────────────────────────────────
def tg_send(msg: str):
    if not TG_TOKEN:
        print("[TG] " + msg)
        return
    url  = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    body = json.dumps({"chat_id": TG_CHAT, "text": msg}).encode()
    try:
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print("[TG 실패]", e)

# ── Playwright 라우트 핸들러: Device=BH → Device=IP ────────────────────────
async def patch_device(route):
    url = route.request.url
    if "Device=BH" in url:
        url = url.replace("Device=BH", "Device=IP")
        await route.continue_(url=url)
    else:
        await route.continue_()

# ── 열차 조회 ───────────────────────────────────────────────────────────────
SCHEDULE_JS = """
async (args) => {
    const params = new URLSearchParams({
        txtGoAbrdDt:    args.date,
        txtGoStart:     args.start,
        txtGoEnd:       args.end,
        selGoTrain:     '109',
        txtTrnGpCd:     '109',
        txtGoHour:      '000000',
        adjStnScdlOfrFlg: 'S',
        srtCheckYn:     'Y',
        qryDvCd:        '1',
        radJobId:       '1',
        rtYn:           'N',
        txtMenuId:      '11',
        pgPrCnt:        '0',
        ebizCrossCheck: 'Y',
        txtPsgFlg_1:    '01',
        txtPsgFlg_2:    '00',
        txtPsgFlg_3:    '00',
        txtPsgFlg_4:    '00',
        txtPsgFlg_5:    '00',
        txtSeatAttCd_2: '000',
        txtSeatAttCd_3: '000',
        txtSeatAttCd_4: '015',
        Device:         'IP',
        Version:        '250601002',
        Key:            'korail1234567890',
        qryStNo:        '0',
        qryStTrnNo:     '',
        qryStTrnNo2:    '',
    });
    const resp = await fetch(
        'https://smart.letskorail.com/classes/com.korail.mobile.seatMovie.ScheduleView?' + params,
        {headers: {Accept: 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}}
    );
    return await resp.json();
}
"""

# ── 예매 실행 ───────────────────────────────────────────────────────────────
RESERVE_JS = """
async (args) => {
    const params = new URLSearchParams({
        txtPsgTpCd1:    '1',
        txtSeatAttCd1:  '000',
        txtDptTm1:      args.dptTm,
        txtPsrmClCd1:   '1',
        rtYn:           'N',
        txtDiscKndCd1:  '000',
        txtJobId:       '1101',
        txtJrnyCnt:     '0001',
        txtJrnyTpCd1:   '11',
        txtPvaStation1: args.stnS,
        txtNvgStation1: args.stnE,
        txtTrnNo1:      args.trnNo,
        txtRunDt1:      args.date,
        txtRunOrd1:     '001',
        txtTrnGpCd1:    '109',
        txtMenuId:      '11',
        Device:         'IP',
        Version:        '250601002',
        Key:            'korail1234567890',
        srtCheckYn:     'Y',
    });
    const resp = await fetch(
        'https://smart.letskorail.com/classes/com.korail.mobile.certification.TicketReservation?' + params,
        {headers: {Accept: 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}}
    );
    return await resp.json();
}
"""

# ── 메인 루프 ───────────────────────────────────────────────────────────────
async def main():
    if not os.path.exists(SESSION_FILE):
        print("[ERROR] 세션 파일 없음:", SESSION_FILE)
        sys.exit(1)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,          # headed 모드 — Device=BH 감지 우회
            args=["--window-size=1,1", "--window-position=-10000,0"],
        )
        ctx = await browser.new_context(
            storage_state=SESSION_FILE,
            user_agent="KorailTalk/4.18.22 (iPhone; iOS 26.3.1; Scale/3.00)",
        )
        page = await ctx.new_page()

        # Device=BH → Device=IP 인터셉터
        await page.route("**/letskorail.com/**", patch_device)

        # 코레일 세션 초기화 (JSESSIONID 활성화)
        await page.goto("https://smart.letskorail.com/", wait_until="domcontentloaded")

        ts = datetime.now().strftime("%H:%M KST")
        msg = "[코레일봇 %s] KTX %s %s→%s %s 모니터링 시작 (3분 주기)" % (
            ts, TARGET_TRN_NO, TARGET_STN_S, TARGET_STN_E, TARGET_DATE)
        print(msg)
        tg_send(msg)

        consec_err = 0
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            try:
                result = await page.evaluate(SCHEDULE_JS, {
                    "date": TARGET_DATE,
                    "start": TARGET_STN_S,
                    "end": TARGET_STN_E,
                })
            except Exception as e:
                consec_err += 1
                print("[%s] 조회 오류(%d): %s" % (now, consec_err, e))
                if consec_err >= 5:
                    tg_send("[코레일봇] 조회 오류 5회 연속, 세션 만료 가능성. 확인 필요.")
                    consec_err = 0
                await asyncio.sleep(POLL_SEC)
                continue

            consec_err = 0
            msg_txt = result.get("h_msg_txt", "")

            # 세션 만료 감지
            if "업데이트" in msg_txt or not result.get("trn_infos"):
                print("[%s] 세션 만료 또는 API 오류: %s" % (now, msg_txt))
                tg_send("[코레일봇] 세션 만료. korail_storage.json 갱신 필요.")
                await asyncio.sleep(POLL_SEC)
                continue

            trains = result["trn_infos"]["trn_info"]
            target = next((t for t in trains if t["h_trn_no"] == TARGET_TRN_NO), None)
            if not target:
                print("[%s] KTX %s 목록에 없음" % (now, TARGET_TRN_NO))
                await asyncio.sleep(POLL_SEC)
                continue

            rsv_cd  = target["h_gen_rsv_cd"]
            rsv_nm  = target["h_gen_rsv_nm"]

            if rsv_cd == "11":
                print("[%s] ✅ 예약가능! 즉시 예매 시도..." % now)
                tg_send("[코레일봇] KTX %s 예약가능 감지! 예매 시도 중..." % TARGET_TRN_NO)
                try:
                    rsv = await page.evaluate(RESERVE_JS, {
                        "date":  TARGET_DATE,
                        "dptTm": TARGET_DPT_TM,
                        "stnS":  STN_CD_S,
                        "stnE":  STN_CD_E,
                        "trnNo": TARGET_TRN_NO,
                    })
                except Exception as e:
                    tg_send("[코레일봇] 예매 요청 오류: %s" % str(e)[:200])
                    await asyncio.sleep(30)
                    continue

                pnr = rsv.get("h_pnr_no")
                if pnr:
                    price = int(rsv.get("h_tot_prc", "0"))
                    success_msg = (
                        "🎉 예매 성공!\n"
                        "KTX %s %s→%s %s\n"
                        "PNR: %s\n"
                        "금액: %s원\n"
                        "⚠️ 30분 내 결제 필요!"
                    ) % (TARGET_TRN_NO, TARGET_STN_S, TARGET_STN_E,
                         TARGET_DPT_TM[:2] + ":" + TARGET_DPT_TM[2:4],
                         pnr, "{:,}".format(price))
                    print(success_msg)
                    tg_send(success_msg)
                    break
                else:
                    err_msg = rsv.get("h_msg_txt", str(rsv)[:200])
                    print("[%s] 예매 실패: %s" % (now, err_msg))
                    tg_send("[코레일봇] 예매 실패: %s" % err_msg)
                    await asyncio.sleep(30)

            else:
                print("[%s] KTX %s: %s(%s) — %ds 후 재시도" % (
                    now, TARGET_TRN_NO, rsv_nm, rsv_cd, POLL_SEC))
                await asyncio.sleep(POLL_SEC)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
