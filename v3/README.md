# ASGK 3.0 preview.1 — GitHub 原生工作治理候選版

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

## 從這裡測試

需要 Python 3.10+、Git；線上讀取另用你已登入的 GitHub CLI。
不安裝套件、不呼叫模型、不更改 Bot 設定。

```bash
python3 v3/asgk3.py demo --out /tmp/asgk3-github-test
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
python3 v3/asgk3.py capture --repo OWNER/REPO --issue NUMBER --out /tmp/asgk3-capture
python3 v3/asgk3.py packet --snapshot /tmp/asgk3-capture/snapshot.json --repo-root /path/to/checkout --actor RECEIVER --run RUN-ID --out /tmp/asgk3-packet
```

Issue 必須符合既有 canonical scope；工具重用原有 parser，不接受任意本地 JSON
冒充 issue。可用 `--path`、`--context` 縮小投影。角色上限也是縮限，不是授權。
不能連線時回報失敗；受信任的 connector 匯出必須標成 `connector_export`，
不能說成即時授權或 GitHub 已停機的證明。

## Skills 也一起演進

[候選 Skills](skills/) 保留 11 個用途，已逐份檢討與改寫：
startup、issue scoping、PR evidence/MDR、gatekeeper、closeout、current status、
evidence audit、health check、release prep、target adoption、upgrade assessment。

候選版讓控制層按工作階段使用 Skill，不要求每個 worker 讀完整治理庫；
也修正「語意判斷自動多出人工 gate」與「只有合併後才有 closeout」的誤導。
本分支測試只讀需要的候選 Skill，不要同時載入兩個版本。尚未安裝或全域同步。

研究、影音與翻譯都是能力演進的例子。Bot memory 保持輕薄；大量 Lesson／帳本
可以存在自己的領域庫，但先看小索引、再選分支與全文。只有經 issue／PR、
回歸測試與適用審查後，才把方法升格到版本化 Skill；索引不是新權威。

## 沒有改掉的邊界

PR body 仍走既有 template／file preflight；MDR、strict check-pr、現有 human gate、
target-owned assessment、普通 revert 與文件驅動自體進化都保留。
`handoff` 和 `closeout` 只產生 GitHub comment 草稿，不自動 post／merge／close。
搜尋以 issue close-out 為入口，不要求翻遍 repo。

這是從原 `codex/asgk-3-preview` 另開的 preview.1 候選分支，原候選不變；
不是已發布或已證實安全的產品。
真正 Bot／Kanban 互通、獨立 reviewer 與 target pilot 尚需實測。
跨供應商接手仍是可攜性不變量，但不是自動選型功能，也不是本次主要瓶頸。
你的 2.0 原始工作區與全域 Skills 都保持不動。
