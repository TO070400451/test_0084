# Claude Code 実装指示プロンプト（Runbook）

このドキュメントは、Claude Code に **そのまま貼り付けて実装させるための指示プロンプト**です。  
実装対象は2つのCLIツール（Generator / Patcher）で、英語Excel→patch.yml生成→日本語Excel「試験項目」更新までを実現します。citeturn5file10turn3file6

---

## 0. 前提（最重要）

### 0.1 対象Excel
- 入力（英語）: `OTR-MA-LQC-TEST-RevE13-20260130_E_for MR Testing_分担 (2).xlsx`
  - 対象シート: `Test Items`
  - 主要列: `Test ID`, `Section`, `Sub-section`, `Test Title`, `Pre-Condition`, `Test Procedure`, `Check item`, `Remark`, `チーム分担` citeturn4search1turn5file10
- 出力（日本語）: `【S社向けMRリグレッション2試験】RevE081_Master_v0.5 1 (3).xlsx`
  - 対象シート: `試験項目`
  - 主要列: `No.`, `Test ID`, `Section`, `Sub-section`, `Test Title`, `前提条件`, `試験手順`, `判定基準`, `注意事項` ほか citeturn2search1turn2file4turn3file6

### 0.2 固定ルール（ユーザー確定）
- 行キー: **Test ID のみで一意** citeturn3file6
- 新規行の追加位置: **特定 Test ID の直後**（after_key） citeturn3file6turn5file10
- No.: **自動採番**（patcher側で1,2,3…に振り直す） citeturn3file6turn5file10
- 自動入力列: **上書きしない**（数式/集計を壊さない） citeturn2file4turn3file6
- #MRExclusive は **対象外** citeturn5file10turn4search1
- 追加フィルタ: `Test Items` の **R列（チーム分担）= QC(Verification)** の行のみ対象（括弧 全角/半角は正規化して同一扱い） citeturn5file10turn4search1
- Remark(Q列)は **出力へ格納しない**（フィルタ用途のみ） citeturn5file10turn4search1
- Section/Sub-section/Test Title は **原文維持（日本語化しない）** citeturn5file10turn4search1

### 0.3 参照仕様書
- Patcher仕様: `claude_code_spec_shikenkomoku_patcher_v2.md` citeturn3file6
- Generator仕様: `claude_code_spec_english_to_patch_generator_v2.md` citeturn5file10

---

## 1. Claude Code への最終指示（ここから下を貼り付け）

> **あなた（Claude Code）はリポジトリを新規に作成し、以下の2つのCLIを実装してください。**
> - `generator` : 英語Excel（Test Items）から patch.yml を生成する
> - `patcher` : patch.yml を日本語Excel（試験項目）へ反映し、No.を自動採番する
>
> 実装言語は Python、Excel操作は openpyxl を使用してください。citeturn5file10turn3file6

### 1.1 リポジトリ構成（必須）
以下の構成で作成してください。

```text
repo/
  app/
    __init__.py
    cli_generator.py
    cli_patcher.py
    excel_read.py
    excel_write.py
    filter_rules.py
    normalizer.py
    patch_model.py
    patch_io.py
    after_key.py
    renumber.py
    diff_report.py
    translator.py
  config/
    glossary.yml
  out/
  tests/
    test_normalizer.py
    test_filter_rules.py
    test_after_key.py
  README.md
  pyproject.toml  (or requirements.txt)
```

### 1.2 CLI仕様（必須）

#### generator
```bash
python -m app.cli_generator \
  --english-xlsx "input/OTR.xlsx" \
  --base-xlsx "input/master.xlsx" \
  --out-patch "out/patch.yml" \
  --out-report "out/generate_report.md"
```

要件:
- `Test Items` のヘッダ行を自動検出（1〜50行で `Test ID`/`Test Procedure`/`Check item` を含む行）citeturn5file10
- 対象行フィルタ（AND条件）を適用する citeturn5file10turn4search1
  - `Remark` に `#MR` を含む
  - `Remark` に `#MRExclusive` を含まない
  - `チーム分担` == `QC(Verification)`（括弧を正規化して比較）
- 抽出対象列:
  - `Test ID`, `Section`, `Sub-section`, `Test Title`, `Pre-Condition`, `Test Procedure`, `Check item` citeturn5file10turn4search1
- 文字正規化:
  - `\_x000D\_` → `\n`
  - 連続空行は最大2行
  - 箇条書き/番号体系を保持 citeturn5file10turn4search1
- 変換（平易な日本語）:
  - `Pre-Condition` → `前提条件`
  - `Test Procedure` → `試験手順`
  - `Check item` → `判定基準` citeturn5file10turn4search1
- `Remark` は出力へ入れない citeturn5file10turn4search1
- `Section/Sub-section/Test Title` は原文維持（そのまま patch に入れる） citeturn5file10turn4search1
- 日本語Excel `試験項目` の `Test ID` 一覧を読み、存在すれば `update`、無ければ `insert` にする citeturn3file6turn2search1
- insert の `after_key` は「英語側の並び順」を基準に直前の Test ID を遡って決定する（仕様書のアルゴリズム通り） citeturn5file10turn3file6
- 出力:
  - `patch.yml`
  - `generate_report.md`（件数、update/insert内訳、after_key一覧、警告） citeturn5file10

#### patcher
```bash
python -m app.cli_patcher \
  --base "input/master.xlsx" \
  --patch "out/patch.yml" \
  --sheet "試験項目" \
  --output "out/master_updated.xlsx" \
  --report "out/diff.md"
```

要件:
- `試験項目` のヘッダ行を自動検出（`No.`/`Test ID`/`Test Title` を含む行）citeturn3file6turn2file4turn2search1
- `Test ID` をキーに update/insert を実行する citeturn3file6
- update:
  - patchの `set` にある列だけ更新
  - “自動入力/集計/モデル列”は上書き禁止 citeturn3file6turn2file4
- insert:
  - `after_key.Test ID` 行の直後に行挿入
  - 直上行をテンプレとして **書式/罫線/数式/行高/検証** を複製して保持 citeturn3file6turn2file4turn2search1
- No. 自動採番:
  - `Test ID` が空でない行のみ 1,2,3… を付与（表終了は連続空行N=3） citeturn3file6
- 差分レポート:
  - 追加/更新を Markdown に出力（旧→新、長文は省略） citeturn3file6

### 1.3 Patchファイル形式（YAML）
- 仕様書に従い、以下の構造を守ること。citeturn5file10turn3file6

```yaml
sheet: "試験項目"
key_columns: ["Test ID"]
operations:
  - op: update
    key:
      Test ID: "OTR-MA-LQC-999.001.001"
    set:
      前提条件: "..."
      試験手順: "..."
      判定基準: "..."

  - op: insert
    after_key:
      Test ID: "OTR-MA-LQC-999.001.002"
    row:
      Test ID: "OTR-MA-LQC-999.002.012"
      Section: "Final Test"
      Sub-section: "..."
      Test Title: "..."
      前提条件: "..."
      試験手順: "..."
      判定基準: "..."
```

### 1.4 翻訳（translator.py）に関する指示
- 外部API呼び出しは不要（オフライン前提）。
- 実装は **ルールベース+用語辞書置換** をまず作る。
- 将来LLM接続を差し替えられるよう、translator.py はインターフェース分離する。

最低限のルール:
- `Verify ...` → `...を確認する`
- `Ensure ...` → `...であることを確認する`
- `Capture a screenshot` → `スクリーンショットを取得する`
- 箇条書きと番号（1., 1-1., (1) 等）を維持

※品質を上げるための辞書は `config/glossary.yml` に追加可能にする。citeturn5file10

### 1.5 テスト（最低3本）
- `test_filter_rules.py` : #MR/#MRExclusive/QC フィルタが仕様通り
- `test_after_key.py` : after_key 決定が「直前遡り」になっている
- `test_normalizer.py` : `\_x000D\_` や括弧正規化が動く

---

## 2. READMEに必ず書くこと
- セットアップ（依存関係）
- generator の実行例
- patcher の実行例
- 出力ファイルの説明（patch.yml / diff.md / generate_report.md）
- 制約事項
  - 自動入力列は上書きしない
  - #MRExclusive は対象外
  - QC(Verification)のみ対象

---

## 3. 完了条件（Acceptance）
- 指定したフィルタ条件で英語Excelから対象行だけ抽出できる citeturn5file10turn4search1
- patch.yml が update/insert を正しく分けて生成できる citeturn5file10turn3file6
- patcher が `試験項目` シートへ更新・挿入でき、No.が1..Nに再採番される citeturn3file6turn2search1
- 書式/数式が破壊されない（insertでテンプレ行コピー） citeturn3file6turn2file4turn2search1

---

## 4. 実装メモ（注意）
- openpyxlは画像/図形の完全保持が不得意なため、**元ファイルを直接上書きせず**必ず別名出力する。
- `チーム分担` の値は `QC(Verification)` と `QC（Verification）` の揺れを正規化して比較する。citeturn5file10turn4search1

