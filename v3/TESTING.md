# 3.0 preview 測試手冊

本手冊是實驗協定，不授予真實 Bot、repo 或外部操作權限。
請先在合成資料上測試。輸出目錄由你選擇，必須尚不存在。

## 1. 離線完整一輪

從這個分支的 repo 根目錄執行：

```bash
python3 v3/asgk3.py demo --out /tmp/asgk3-user-test
python3 v3/asgk3.py check --input /tmp/asgk3-user-test/input.json --packet /tmp/asgk3-user-test/packet.json
python3 v3/asgk3.py verify --input /tmp/asgk3-user-test/input.json --packet /tmp/asgk3-user-test/packet.json --report /tmp/asgk3-user-test/report.json --repo-root /tmp/asgk3-user-test/workspace
python3 v3/asgk3.py handoff --input /tmp/asgk3-user-test/input.json --packet /tmp/asgk3-user-test/packet.json --report /tmp/asgk3-user-test/report.json --repo-root /tmp/asgk3-user-test/workspace --out /tmp/asgk3-user-handoff
python3 v3/asgk3.py closeout --input /tmp/asgk3-user-test/input.json --packet /tmp/asgk3-user-test/packet.json --report /tmp/asgk3-user-test/report.json --repo-root /tmp/asgk3-user-test/workspace --out /tmp/asgk3-user-closeout
```

先讀 `WORK.md`，不要先讀所有 repo 文件。應能回答：做什麼、去哪裡做、
不做什麼、禁止動什麼、怎樣檢查、下一步是什麼。`packet.json` 保留機械綁定與
逐項納入理由；`report.json` 保留完整決策樹；`CLOSEOUT.md` 是檢索入口。

`demo` 會為合成契約填入目前時間起算一天的有效期，以及正確的輸入 hash。
提交的 `examples/demo.json` 是結構範例，日期與零 hash 不可直接當真實證據。
`check` 不讀工作檔；`verify` 才核對本機檔案。工具不會執行 validation 字串。

結束碼：0 = 本指令的機械檢查通過；1 = 格式、綁定或證據錯誤；
2 = 證據結構通過，但有未通過的 validation 或 known gap，交接狀態為 blocked。
沒有任何結束碼代表人類批准。

## 2. 自己改資料試攻擊

每次重新 `demo` 到另一個新目錄，避免前一個改動干擾。

| 改動 | 執行 | 預期 |
| --- | --- | --- |
| input 的 request.write 增加 secrets.txt | compile | FORBIDDEN |
| 某一 ceiling 移除 answer.txt | compile | SCOPE_DENIED |
| actor_id 改成接手者，仍用原 packet | check | STALE_PACKET |
| authority.revoked 改 true | check | REVOKED |
| expires_at 改成已過期 UTC 時間 | check | EXPIRED |
| 修改 workspace/answer.txt，不更新 receipt | verify | EVIDENCE_HASH |
| 修改 brief.txt 並更新 receipt hash | verify | CONTEXT_HASH |
| report 的 validation status 改 approved | verify | STATUS |
| validation status 改 not_run | verify | blocked，exit 2 |
| 決策 D1 的 parent 改 D1 | verify | DECISION_PARENT |

`compile` 使用 `--input <input.json> --out <新目錄>`。所有 finding 都有固定 code、
field、reason、blocking。單元測試也核對指定 code，不把任意失敗當成功。

## 3. 人類／Hermes Bot 手動接手

Hermes 指的是 **Bot Mode 的持續性 Bot**，不是單次模型 API 呼叫。
這裡不重造其訊息、group、delegation 或 task scheduling。

1. 先由你確認目前 Hermes 版本、Bot profile、工作目錄與實際權限。只給合成資料。
   本原型不設定這些權限，也不保證 Bot 只能碰工作包內的檔案。
2. 給接手者 `WORK.md` 與 `packet.json`，另提供可信的目前 input 及所列 context。
   要求它先指出目的、禁止範圍、未知狀態。不要提供原始長對話。
3. 請它產出獨立的 greeting 與 report，不能把範例的 validation pass 當自身證據。
   若不能操作檔案，可先純文字回覆，由你存成測試檔；記錄這是人工傳遞。
4. 以新的 actor_id/run_id 編譯下一份契約，保留上一次 packet/report/closeout。
   交接不是把舊 actor 的權限改名。此版本不會自動轉換前後工作範圍。
5. 對新的報告執行 verify，再由未參與者用摘要找到 choice、reason、alternatives、
   evidence。記錄實际平台、模型、提供的檔案、讀取擴張、耗時、錯誤與未知項目。
6. 在 [#357](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/357)
   回報測試結果。不要上傳敏感 Bot memory、token 或真實私有資料。

若透過 Bot mention/message 轉交，請核對 packet_id 與原始檔案 hash；自然語言轉述
不等於原封不動傳遞。平台功能應以實際安裝版本測試，不能只靠線上文件。

## 4. 用不同專業與執行階段挑錯

| 角色／階段 | 主動攻擊 | 這版的預期邊界 |
| --- | --- | --- |
| 架構師／編譯前 | 讓角色記憶或舊計畫增加範圍 | 只計算目前顯式 input；不驗證 input 的授權真偽 |
| 安全工程師／接收 | 在 context 塞擴權指令或改 packet 後重算 hash | 重算 packet 抓得到；prompt injection 需 runtime 與接手者防禦 |
| 執行者／寫入 | 直接寫未列檔案、網路外送、同時另一 worker 寫檔 | 不攔截、不宣稱抓得到；需另設執行控制 |
| 稽核者／回報 | 偽造一份內容一致但從未跑測試的報告 | hash 可以通過；真實測試來源與獨立驗證仍必須建立 |
| 接手者／恢復 | 舊 packet、換人不換 run、缺檔、未知結果 | 綁定或證據失敗；不能猜測補成 pass |
| 維護者／closeout | 決策缺理由、循環引用、海量摘要掩蓋問題 | 結構檢查與摘要限長；語意正確性需冷讀 |

目前不支援同一路徑讀入後原地修改，也未完成「中斷且缺 receipt」的部分工作恢復。
這些是下一個實作切片的候選，不能據此宣稱通用 repo coding 已被支援。

## 5. 搬移的判斷依據

先問：接手者能否僅靠最小包正確工作？是否比 2.0 少讀而沒有漏掉禁止事項？
搜尋 closeout 能否快速還原重要決策？重複的規則是否真的由中心維護，而非丟給
每個 worker 重填？原地修改、部分完成、獨立證據與實際 runtime 邊界是否已補足？

這些實测成立後，再決定延伸這個原型、只搬移部分觀念，或放棄此實作。
不以單元測試數量代替採用成效。

## 研究來源與版本限制

2026-09-08 研究參考（非本地安裝版本證明）：

- [Hermes Bot Mode](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode)：持續性 Bot 與訊息／group 的平台語意。
- [Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)：平台委派能力；不等同本原型的授權交接。
- [Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)：既有 durable task surface，避免另造排程器。
- [Managed scope](https://hermes-agent.nousresearch.com/docs/user-guide/managed-scope)：設定管理與真正執行隔離必須分開評估。
