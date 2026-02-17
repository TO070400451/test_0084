# 英語「Test Items」Excel → 日本語「試験項目」シート Patch 自動生成 仕様書（Claude Code向け）v2

目的:
- 入力元（英語）Excelの `Test Items` シートから、各 Test ID の
  - `Pre-Condition` / `Test Procedure` / `Check item` を抽出
  - 「作業者にもわかりやすい平易な日本語」へ変換
- 変換結果を **patch.yml** として出力し、別モジュール（patcher）で日本語Excelの `試験項目` シートへ
  - 既存行は update
  - 新規行は after_key 指定で insert（直前 Test ID の直後に挿入）
  - 最後に No. を自動採番

入力元サンプル:
- `OTR-MA-LQC-TEST-RevE13-20260130_E_for MR Testing_分担 (2).xlsx`
  - 対象シート: `Test Items`

---

## 0. 決定事項（ユーザー回答反映）
1) **#MRExclusive は対象外**（含めない）
2) `Test Items` シート **R列**（= チーム分担列）の値が **`QC(Verification)` の行のみ**を集計対象
3) `Remark`（Q列）は **出力に格納しない**（ただしフィルタ用途には使用可）
4) `Section/Sub-section/Test Title` は **原文維持**（日本語化しない）

---

## 1. 入力

### 1.1 入力ファイル
- `--english-xlsx` : 英語試験票（.xlsx）
  - 対象シート: `Test Items`
- `--base-xlsx` : 日本語ベースExcel（.xlsx）
  - 対象シート: `試験項目`

### 1.2 抽出条件（AND条件）
対象行は以下をすべて満たすこと:
- `Remark`（Q列）に **`#MR` を含む**
- `Remark`（Q列）に **`#MRExclusive` を含まない**
- `チーム分担`（R列）の値が **`QC(Verification)`**

補足:
- 入力元 `Test Items` のヘッダ定義より、`Remark` は列名として存在する（= Q列相当）。
- 同じく `チーム分担` 列が存在し、ここに `QC（Verification）` 等の値が入る運用になっている。

---

## 2. 抽出（英語Excel）

### 2.1 抽出対象列（Test Items）
- `Test ID`（キー）
- `Section`
- `Sub-section`
- `Test Title`
- `Pre-Condition`
- `Test Procedure`
- `Check item`
- （フィルタ専用）`Remark`（Q列）
- （フィルタ専用）`チーム分担`（R列）

### 2.2 ヘッダ行検出
- 1〜50行を走査し、同一行に `Test ID` / `Test Procedure` / `Check item` が存在する行をヘッダ行とみなす。
- ヘッダ行から「ヘッダ名→列番号」辞書を作成し、列位置の変動に耐える。

### 2.3 文字正規化
Excel内に `\_x000D\_` が混入するケースがあるため、以下を実施:
- `\_x000D\_` → 改行 `\n`
- 連続空行は最大2行へ縮約
- 箇条書き記号 `-`, `*`, `1.` `1-1.` などは保持

---

## 3. 変換（英語→平易な日本語）

### 3.1 変換対象
- `Pre-Condition` → 日本語Excelの `前提条件`
- `Test Procedure` → `試験手順`
- `Check item` → `判定基準`

### 3.2 “平易な日本語”の必須ルール
- 1文を短く（目安 40〜60文字）
- 可能な限り命令形（〜してください/〜を確認する）
- 指示対象を明確化（「それ」など指示語を減らす）
- 数値/条件/閾値/記号は原文の意味を変えず保持
- 箇条書き/番号体系を維持

### 3.3 用語辞書（config/glossary.yml）
- verify → 確認する
- ensure → 〜であることを確認する
- capture screenshot → スクリーンショットを取得する
- power cycle → 電源入れ直し

---

## 4. マッピング（英語→日本語Excel列）

| 英語(Test Items) | 日本語Excel(試験項目) | 方針 |
|---|---|---|
| Test ID | Test ID | キー。完全一致で突合 |
| Section | Section | 原文維持 |
| Sub-section | Sub-section | 原文維持 |
| Test Title | Test Title | 原文維持 |
| Pre-Condition | 前提条件 | 日本語（平易）へ変換 |
| Test Procedure | 試験手順 | 日本語（平易）へ変換 |
| Check item | 判定基準 | 日本語（平易）へ変換 |

※`Remark`（Q列）は **出力に格納しない**（フィルタ用途のみ）。

---

## 5. patch.yml 生成ロジック

### 5.1 update / insert 判定
- 日本語Excelの `試験項目` シートに同一 `Test ID` が存在 → `update`
- 存在しない → `insert`

### 5.2 insert の after_key 決定（直後挿入）
ユーザー要望: **特定 Test ID の直後へ挿入**

アルゴリズム:
1. フィルタ後の英語 `Test Items` の並び順を保持
2. 新規 Test ID の直前に出現する Test ID を遡って探す
3. その Test ID が
   - 既存（日本語Excelに存在）または
   - 直前までの insert で既に追加予定
   のいずれかであれば、それを `after_key.Test ID` とする
4. 見つからない場合
   - strict: エラー
   - lenient: 末尾追加 + 警告

### 5.3 No. 自動採番
- patcher 側で `No.` を 1,2,3… と振り直す（generatorでは No. を出さない）

---

## 6. 出力

### 6.1 patch.yml
- `operations` 配下に update/insert を出力
- update は `set` のみに変更列を書く
- insert は `row` に必要列を書く（No.は不要）

### 6.2 生成レポート（任意）
- `out/generate_report.md`
  - 抽出件数（フィルタ前/後）
  - update 件数 / insert 件数
  - insert の after_key 決定結果一覧
  - 変換の警告（未辞書、長文化、曖昧など）

---

## 7. CLI（案）
```bash
generator \
  --english-xlsx "input/OTR-MA-LQC-TEST-RevE13.xlsx" \
  --base-xlsx "input/master.xlsx" \
  --target-tag "#MR" \
  --exclude-tag "#MRExclusive" \
  --team-col "チーム分担" \
  --team-value "QC(Verification)" \
  --out-patch "out/patch.yml" \
  --out-report "out/generate_report.md"
```

---

## 8. 実装メモ（Claude Code向け）
- Excel読み取り: openpyxl
- `Test Items` のセル値は改行や `\_x000D\_` を正規化する
- フィルタは `Remark` を **含む/除外** で判定
- `チーム分担` は完全一致（前後空白はトリム）

