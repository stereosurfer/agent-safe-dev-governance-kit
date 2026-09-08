# ASGK 3.0 — GitHub 原生工作治理候選版

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

## 沒有改掉的邊界

PR body 仍走既有 template／file preflight；MDR、strict check-pr、現有 human gate、
target-owned assessment、普通 revert 與文件驅動自體進化都保留。
`handoff` 和 `closeout` 只產生 GitHub comment 草稿，不自動 post／merge／close。
搜尋以 issue close-out 為入口，不要求翻遍 repo。

這是可測試的 3.0 候選分支，不是已發布或已證實安全的產品。
真正 Bot 互通、跨供應商冷接手、独立 reviewer 與 target pilot 尚需實測。
你的 2.0 原始工作區與全域 Skills 都保持不動。
