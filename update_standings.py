"""
NPB順位表を自動取得してSupabaseに保存するスクリプト
GitHub Actionsから毎日自動実行される
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 環境変数が設定されていません")
    exit(1)

print(f"接続先: {SUPABASE_URL}")

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

TEAM_MAP = {
    '読売': '巨人', '巨人': '巨人',
    '阪神': '阪神',
    'ＤｅＮＡ': 'DeNA', 'DeNA': 'DeNA', 'ベイスターズ': 'DeNA', '横浜': 'DeNA',
    '広島': '広島',
    '中日': '中日',
    'ヤクルト': 'ヤクルト',
    'ソフトバンク': 'ソフトバンク', 'ホークス': 'ソフトバンク',
    'ロッテ': 'ロッテ',
    '楽天': '楽天',
    '日本ハム': '日本ハム', 'ファイターズ': '日本ハム',
    '西武': '西武',
    'オリックス': 'オリックス',
}

def normalize_team(name):
    name = name.strip()
    for k, v in TEAM_MAP.items():
        if k in name:
            return v
    return name

def scrape_standings():
    url = 'https://baseball.yahoo.co.jp/npb/standings/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res = requests.get(url, headers=headers, timeout=15)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    result = {'cl': [], 'pl': []}
    tables = soup.find_all('table')
    league_idx = 0
    league_keys = ['cl', 'pl']

    for table in tables:
        teams = []
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            texts = [c.get_text(strip=True) for c in cells]
            try:
                rank = int(texts[0])
                team = normalize_team(texts[1])
                if team and 1 <= rank <= 6:
                    teams.append({'rank': rank, 'team': team})
            except (ValueError, IndexError):
                continue
        if len(teams) == 6 and league_idx < 2:
            result[league_keys[league_idx]] = teams
            league_idx += 1

    return result

def save_to_supabase(year, phase, league, teams):
    if not teams:
        print(f"  データなし: {league}")
        return

    endpoint = f'{SUPABASE_URL}/rest/v1/results'

    # 既存レコードを削除
    del_res = requests.delete(
        f"{endpoint}?year=eq.{year}&phase=eq.{phase}&league=eq.{league}",
        headers=HEADERS
    )
    print(f"  DELETE: {del_res.status_code}")

    # 新規挿入
    data = {
        'year': year, 'phase': phase, 'league': league,
        'rank1': teams[0]['team'] if len(teams) > 0 else None,
        'rank2': teams[1]['team'] if len(teams) > 1 else None,
        'rank3': teams[2]['team'] if len(teams) > 2 else None,
        'rank4': teams[3]['team'] if len(teams) > 3 else None,
        'rank5': teams[4]['team'] if len(teams) > 4 else None,
        'rank6': teams[5]['team'] if len(teams) > 5 else None,
        'updated_at': datetime.utcnow().isoformat()
    }
    ins_res = requests.post(endpoint, headers=HEADERS, json=data)

    if ins_res.status_code in (200, 201):
        print(f"  ✅ 保存OK: {year}年 {phase} {league} → {[t['team'] for t in teams]}")
    else:
        print(f"  ❌ 保存失敗: {ins_res.status_code} {ins_res.text}")

def main():
    year = datetime.now().year
    print(f"NPB順位取得開始: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    standings = scrape_standings()
    print(f"取得結果:")
    print(f"  セ: {[t['team'] for t in standings['cl']]}")
    print(f"  パ: {[t['team'] for t in standings['pl']]}")

    if not standings['cl'] and not standings['pl']:
        print("⚠️ 順位データを取得できませんでした")
        exit(1)

    print("Supabaseに保存中...")
    save_to_supabase(year, 'final', 'cl', standings['cl'])
    save_to_supabase(year, 'final', 'pl', standings['pl'])
    print("完了!")

if __name__ == '__main__':
    main()
