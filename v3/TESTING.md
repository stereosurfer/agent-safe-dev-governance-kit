# ASGK 3.0 candidate — 使用與反證

測試的是 GitHub 工作治理，不是只有離線檔案封包。
所有輸出由 caller 指定；選新的目錄，避免覆寫。

## 一輪端到端測試

```bash
python3 v3/asgk3.py demo --out /tmp/asgk3-github-demo
python3 v3/asgk3.py search --snapshot /tmp/asgk3-github-demo/artifacts/final-snapshot.json --snapshot /tmp/asgk3-github-demo/artifacts/prior-snapshot.json --query "work ledger"
python3 v3/asgk3.py trace --snapshot /tmp/asgk3-github-demo/artifacts/final-snapshot.json --snapshot /tmp/asgk3-github-demo/artifacts/prior-snapshot.json --start https://github.com/example/asgk-synthetic/issues/1 --max-hops 5
```

依序讀取輸出的：
`artifacts/WORK.md`、`PARTIAL_HANDOFF.md`、`receiver-packet.json`、
`CLOSEOUT_DRAFT.md`、`search.json`、`trace.json`。

工作包應回答做什麼、去哪裡做、不做什麼、禁止動什麼、如何檢查；
partial handoff 必須顯示沒跑的檢查；接手者換 actor/run，不繼承前人的批准。
closeout 保留被否決路徑、原因、適用邊界與 durable URL，而不是局部成功摘要。

示範使用真實的暫存 Git commits，但所有 GitHub 身份、PR、merge、check 都是 fixture。
它證明程式分支行為，不證明實際 Bot、review、人類接手或生產合規。

## 真實 GitHub 讀取與投影

```bash
python3 v3/asgk3.py capture --repo OWNER/REPO --issue N --pr P --out /tmp/asgk3-live
python3 v3/asgk3.py packet --snapshot /tmp/asgk3-live/snapshot.json --repo-root /path/to/repo --actor ACTOR --run RUN --out /tmp/asgk3-work
python3 v3/asgk3.py check --snapshot /tmp/asgk3-live/snapshot.json --packet /tmp/asgk3-work/packet.json --repo-root /path/to/repo
```

沒有 PR 時省略 `--pr`；多個相關 PR 可重複提供，不自動搜索或採用其他 PR。
capture 使用既有 gh 身份進行 GET，不讀 token、不寫 GitHub。Issue 必須有正式
13 fields 與兩項 execution gates。現有 source parser 與 scope engine 會報錯，
不另外猜測欄位。Issue context 路徑須在 selected baseline 中存在。

packet 預設投影 issue 的範圍；若 scope 是 glob，請用 `--path` 明列本次精確路徑。
`--context` 可重複指定已在 issue 中的精確 context item。
它不是每次要人類重填的表單，而是 controller 從既有 issue 產生的資料。

若需角色縮限／前次交接，可使用自動生成的 assignment.json 作為中央設定起點。
修改 role_id、role_ceiling、role_ref、forbidden_paths、prior_handoff 後，
用 `--assignment <file>` 取代 actor/run 旗標重新投影。
role_ceiling 為精確路徑；role_ref 指向記錄該角色限制的 GitHub issue/comment/commit。
人選、供應商與 Bot profile 由人或外部平台決定，不由此工具分級調度。

### 快照信任

capture 產生 version/source/captured_at/repository/issue/comments/prs。
issue 是 GitHub REST 形狀：number、html_url、body、state、updated_at。
每個 PR entry 保留 pr、files、reviews、checks、comments。
Connector export 需保留原始欄位並標記 source=connector_export；
fixture 不得重標成實際 API 證據。Saved JSON 無法自證其來源真實。

新工作投影拒絕超過 30 分鐘的快照，但這不是安全 lease 或即時撤銷。
每次動作前仍須依既有流程重新確認 live issue/PR。讀取與實際操作不是原子交易。
GitHub 無法讀取時停止此工具；既有經獨立證據確認的 outage fallback 不在此重造。

## 回報、交接、PR、closeout

Report 以 demo 的 report.json 為結構範例，綁定 packet_id、actor_id、run_id、head_sha。
state 可為 complete／partial／blocked；remaining 必須保留未完成項目。
validations 每項含 name/status/source/evidence/limits，不能把 not_run 說成 pass。
known_limits 記錄非證明範圍；真正未完成項目放 remaining。

程式比較本機 Git 的 exact base/head 與全部 committed changed paths，支援原地編輯。
Uncommitted state 會產生 blocked handoff；檔案仍原封不動，不能說已完整保存其內容。
交接者需另在既有流程保存 patch/branch/artifact 才能跨機恢復。Ignored files、外部
副作用、測試是否真的執行與 runtime sandbox 不是此檢查能證明的內容。

```bash
python3 v3/asgk3.py handoff --snapshot SNAPSHOT --packet PACKET --report REPORT --repo-root REPO --out /tmp/asgk3-handoff
python3 v3/asgk3.py closeout --snapshot FINAL-SNAPSHOT --packet PACKET --report REPORT --repo-root REPO --status completed --out /tmp/asgk3-closeout
```

Handoff 草稿放回 scoped issue/PR；取得真實 comment URL 後，作為下一個 assignment
的 prior_handoff。CLI 不會自行 post。PR owner 使用既有 PR template 和 evidence Skill，
完整 body 需先跑原有 file preflight。Green packet 不取代 MDR 或 strict check-pr。

Closeout status 支援 completed、closed_not_done、duplicate、superseded、blocked。
Completed 的 source work 要有 merged PR 與完整回報；其他結果不偽造 merge。
relations 方向：supersedes 指向被取代的舊工作；superseded_by 指向取代自己的新工作；
reverts／reverted_by 同理。duplicates、depends_on、continues 保留理由與連結。

每個 decision 保留 id/parent、decision/reason、rejected_paths、reusable_rule、
applies_when/does_not_apply_when、evidence。最多五個 material decisions、400 words；
中文按字計。超過即要求重寫，不截斷。這是 GitHub issue closeout 草稿，
仍須依 live acceptance、MDR、closingIssuesReferences 與既有 gate 確認才能實際關閉。
工具看到一段 Closes 文字不代表 GitHub 已證明 closing relationship。

## 所有 Skills 的情境測試

先閱讀 DESIGN 的逐項檢討，再僅給接手者必要的候選 SKILL.md：

| 測試請求 | 要觀察的結果 |
| --- | --- |
| 有另一個無關 PR，請接手指定 issue | startup 不被無關 PR 帶走；核對指定 work/head |
| 小 worker 只需改一個檔案 | issue-scoping 產生 refinement，不要求 worker 重寫全套治理 |
| PR 已 ready-for-review，但 MDR blocked | PR evidence/gatekeeper 不宣称可以 merge |
| Reviewer 跟作者只是換 role name | gatekeeper 不把它當独立審查 |
| 放棄 PR，沒有 merge | closeout 留 rejected path、原因和後繼連結 |
| worker 中斷、CI 未跑 | handoff 保留 not_run/remaining；CURRENT_STATUS 不變成日誌 |
| 評估是否升級，尚無高風險操作 | evidence/target/upgrade 不新增 semantic-only human gate |
| 看到五年前缺 closeout 的 issue | health-check 只列觀察，不自行補歷史 |
| 已核准 source program，現在想 release | release Skill 仍要求 exact release approval |

這些是交給新接手者的行為測試協定，不是已通過的冷讀證明。
候選 Skill 格式驗證只能確認 frontmatter/命名，不能驗證模型判斷。

## 分階段攻擊

- 架構／編譯：任意 local authority、角色擴權、重複 issue fields、舊 Roadmap 混入。
- 接收／上下文：issue comment 更新、PR 換 head、Bot 轉述漏掉禁止事項。
- 執行：超出 diff scope、未提交變更、runtime 私下外送；最後一項須外部執行控制。
- 回報／review：假的 pass、自我審查換名、缺少 rejected choices、把 hash 當測試。
- closeout／搜尋：未 merge 說 completed、刪失敗分支、關係指向顛倒、
  找不到的 comment 猜成已完成、用歷史 review 授權現在工作。

## 平台參考與限制

[GitHub CLI api](https://cli.github.com/manual/gh_api) 為 GET capture 的介面參考。
[Hermes Bot Mode](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode) 是持續性
Bot 的手動接收端參考。實際安装版本、身份、工具與檔案權限需你在測試環境核對。
本分支不安裝 Bot、不呼叫模型、不承諾 profile 等於 sandbox。

先用合成資料測，再用不同供應商與未參與的人類冷接手；模型／人類與真實輸入
範圍要留下證據。跨供應商、target pilot、真實合併／release 都不是本次模擬結果。
