# NPB ペナントレース予想アプリ

スマホ・PCどこからでもアクセスできるペナントレース予想分析アプリです。

## セットアップ手順

### 1. Supabase の設定

1. [Supabase](https://supabase.com/) にログイン
2. 新しいプロジェクトを作成（または既存のプロジェクトを使用）
3. 左メニュー「SQL Editor」を開く
4. `supabase_setup.sql` の内容をコピペして「Run」をクリック
5. 左メニュー「Settings」→「API」から以下をメモ：
   - **Project URL**（例：`https://xxxxxxxx.supabase.co`）
   - **anon public key**（`eyJ...` から始まる長い文字列）

### 2. アプリの設定

1. `index.html` をテキストエディタで開く
2. 冒頭の設定欄を書き換える：
```javascript
const SUPABASE_URL = 'https://xxxxxxxx.supabase.co';  // ← あなたのURL
const SUPABASE_KEY = 'eyJ...';                          // ← あなたのanon key
```

### 3. GitHub Pages の設定

1. このリポジトリを GitHub に作成・プッシュ
2. リポジトリの「Settings」→「Pages」を開く
3. Source を「Deploy from a branch」→ branch を `main`、フォルダを `/ (root)` に設定
4. 「Save」をクリック
5. 数分後に `https://あなたのユーザー名.github.io/リポジトリ名/` でアクセス可能に

## ファイル構成

```
npb-app/
├── index.html          # メインアプリ
├── supabase_setup.sql  # Supabase テーブル作成SQL
└── README.md           # このファイル
```

## 使い方

1. 毎年の予想Excelファイル（.xlsm/.xlsx）をアップロード
2. データが自動的にSupabaseに保存される
3. スマホからアクセスしても同じデータが見える
4. 「順位表比較」タブから現在の順位を手入力できる
