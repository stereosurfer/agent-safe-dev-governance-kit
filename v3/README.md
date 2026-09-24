# ASGK 3.0 候選來源與已整合的 GitHub 工作流

本目錄保留 preview.1 設計與測試來源。GitHub workflow 的正式實作已移至
`scripts/asgk_lib/github_workflow.py`，公開入口是
`python3 scripts/asgk.py workflow --help`；`v3/asgk3.py` 與
`v3/github_workflow.py` 只做代理，不是第二套規則。能力目錄的公開入口是
`python3 scripts/asgk.py catalog --help`，`v3/capability_evolution.py` 也只代理；
根目錄兩份 target 導覽模板已是可選參考，不在 `v3/`；11 個根目錄 Skills
已依 #405 綜合修訂，`v3/skills/` 留作候選歷史而非第二套現行規則。
3.0 尚未發布。

**ASGK 是一套讓人與 AI 能安全、順利交接工作的規則與工具。**
看得懂工作狀態、接得下去長期工作、查得清楚證據與決策；
避免工作依賴特定模型、供應商、Agent 或既有對話。

3.0 保留完整 GitHub 骨幹：

```text
issue 授權 → branch／變更 → 驗證 → PR／MDR／review
→ 合規 merge → issue close-out review → 接手與追溯
```

改變的是資訊如何交給執行者：控制層維護規則與角色能力，
人或 Bot 只收到本次工作所需的範圍、脈絡與交接要求。
GitHub 仍是正式工作紀錄；工作包、搜尋快取都不是第二套權威。
Hermes Kanban 可保存 Bot 的卡片、run 與 review 狀態，但不能取代 GitHub
issue 的授權、PR/MDR 或 close-out。獨立 reviewer 守材料／能力升格等關口，
不是每件事都要經過一個常駐「警察 Bot」。
沒有 Hermes 的 Codex＋GitHub 工作也可沿用 GitHub 骨幹；定期排程只負責啟動，
不是當次寫入或發布授權。這是 [#372 的必要驗收案例](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/372#issuecomment-5807050375)，
尚未由本候選版的網站試點證明，也不預設每個網站都需要導入 ASGK。

若要在這個 repo 實際修改檔案，先讀**目前 main** 的 `AGENTS.md`、`README.md`、
`docs/handoff/CURRENT_STATUS.md` 和選定的 live issue／PR；本 `v3/` 候選來源
及 preview.1 分支內較舊的根目錄文件不能取代它們。[#372](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/372)
只協調 3.0 發布工作，不單獨授權寫入。若只是接手評估候選版，先讀本頁與
[候選交接](HANDOFF.md)；設計、測試、Kanban、Lesson 與歷史證據按問題逐層展開。

## 從這裡測試

需要 Python 3.10+、Git；線上讀取另用你已登入的 GitHub CLI。
不安裝套件、不呼叫模型、不更改 Bot 設定。

```bash
python3 scripts/asgk.py workflow demo --out /tmp/asgk3-github-test
python3 -m unittest discover -s v3 -p 'test_*.py' -v
```

請選尚不存在的輸出目錄。示範建立自己的暫存 Git repo，
模擬 issue → 原地修改 → 中斷交接 → 新人接手 → merged PR → closeout → 跨 issue 追溯。
GitHub issue／PR／review／merge 都明確標成合成資料，不冒充真實執行證據。

- [完整設計與 11 個 Skills 檢討](DESIGN.md)
- [Kanban 與 GitHub 的責任邊界](KANBAN_BRIDGE.md)
- [Lesson／帳本到版本化能力](CAPABILITY_EVOLUTION.md)
- [操作、GitHub 接手與攻擊測試](TESTING.md)
- [分支交付狀態與限制](HANDOFF.md)

## 真實 issue 的工作包

```bash
python3 scripts/asgk.py workflow capture --repo OWNER/REPO --issue NUMBER --out /tmp/asgk3-capture
python3 scripts/asgk.py workflow packet --snapshot /tmp/asgk3-capture/snapshot.json --repo-root /path/to/checkout --actor RECEIVER --run RUN-ID --out /tmp/asgk3-packet
python3 scripts/asgk.py workflow card-draft --snapshot /tmp/asgk3-capture/snapshot.json --packet /tmp/asgk3-packet/packet.json --repo-root /path/to/checkout --out /tmp/asgk3-card
```

Issue 必須符合既有 canonical scope；工具重用原有 parser 檢查提供的 JSON
內容與 scope，但無法證實本地快照真的來自 GitHub。可用 `--path`、`--context`
縮小投影。角色上限也是縮限，不是授權。
不能連線時回報失敗；受信任的 connector 匯出必須標成 `connector_export`，
不能說成即時授權或 GitHub 已停機的證明。
`card-draft` 只產生 `CARD.md` 與來源 metadata，不建立 Hermes 卡片。若 Bot 沒有
可觀察的 GitHub 唯讀查詢，卡片僅供部分交接；不得憑快照改 repo 或自稱已核對
當下 issue。#361 的 Luna 實測曾出現這種錯誤聲稱，修正與重測記在 #362。

## Skills 也一起演進

[候選 Skills](skills/) 保留 11 個用途，已逐份檢討與改寫：
startup、issue scoping、PR evidence/MDR、gatekeeper、closeout、current status、
evidence audit、health check、release prep、target adoption、upgrade assessment。

根目錄正式來源吸收候選版可證實的交接改進，按工作階段使用 Skill，
不要求每個 worker 讀完整治理庫；
也修正「語意判斷自動多出人工 gate」與「只有合併後才有 closeout」的誤導。
需要回溯 preview.1 時只讀對應候選 Skill；日常工作用根目錄版，
不要同時載入兩個版本。尚未安裝或全域同步。

研究、影音與翻譯都是能力演進的例子。Bot memory 保持輕薄；大量任務證據由
各領域自己的交付契約管理。研究員的實例是「Agent 入口 → 當前問題節點 →
觀察 → 選定的完整證據單元」，人可先看精簡交接。跨工作可再利用的 Lesson／
方法則由版本化能力庫逐層揭露；兩者不合併成一個總帳。只有經 issue／PR、
回歸測試與適用審查後，才把方法升格到版本化 Skill；索引不是新權威。

## 沒有改掉的邊界

PR body 仍走既有 template／file preflight；MDR、strict check-pr、現有 human gate、
target-owned assessment、普通 revert 與文件驅動自體進化都保留。
`handoff` 和 `closeout` 只產生 GitHub comment 草稿，不自動 post／merge／close。
搜尋以 issue close-out 為入口，不要求翻遍 repo；JSON 只做有限形狀檢查，
YAML 只回傳待核實候選網址，遇到候選不能宣稱追溯完整。
每次查找同一 issue 只接受一份快照，同一 PR 也只接受一份觀測；已關閉 issue 若沒有提供可辨識的
結案，也會明示不完整，不能把舊式文字結案當成不存在。

本目錄源自從原 `codex/asgk-3-preview` 另開的 preview.1 候選分支，原候選不變。
它的 GitHub workflow 部分已由 #397 整合到根目錄 CLI 與 doctor；
其餘尚未整合的候選來源不是已發布或已證實安全的產品。
真正 Bot／Kanban 的範圍化交接已有 #361 實測，但其首次 issue 核對聲稱失敗；
這不是生產安全或獨立 reviewer 證明。修正後的重測結果見 #362；target pilot
仍未實測。
[#369](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/369) 已把修正合併進
preview.1；[#371](https://github.com/stereosurfer/agent-safe-dev-governance-kit/pull/371)
也已合併一筆 `observed` Lesson。#370 的[結案](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/370#issuecomment-5806869845)
保留了合併前 MDR 尚為 `merge_blocked` 的時間差，不把事後結案冒充事前通關。
Hermes 的[#367 留言測試](https://github.com/stereosurfer/agent-safe-dev-governance-kit/issues/367)
與 #370 限定路徑寫入是分別受控的實測，不是本 CLI 已有自動 GitHub 發文功能，
也不證明一般寫入隔離或可上線。
跨供應商接手仍是可攜性不變量，但不是自動選型功能，也不是本次主要瓶頸。
舊 #379/#381 是候選匯入階段的決策與證據，不是目前的下一工作指令。
後續工作依 #372 的 live child issue；不得由候選來源推定 root 模板的
target 採用、Lesson 適用性、全域 Skills 同步或發布已獲授權。
