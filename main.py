import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from typing import Dict, Any, List

# --- 1. 銘柄データ定義 ---
# 日経225銘柄（主要銘柄のマッピング）
NIKKEI225_MAP = {
    "4151": "協和キリン", "4502": "武田薬品", "4503": "アステラス製薬", "4506": "住友ファーマ",
    "4507": "塩野義製薬", "4519": "中外製薬", "4523": "エーザイ", "4568": "第一三共",
    "4578": "大塚ＨＤ", "4062": "イビデン", "6479": "ミネベアミツミ", "6501": "日立製作所",
    "6503": "三菱電機", "6504": "富士電機", "6506": "安川電機", "6526": "ソシオネクスト",
    "6645": "オムロン", "6674": "ＧＳユアサ", "6701": "ＮＥＣ", "6702": "富士通",
    "6723": "ルネサス", "6724": "エプソン", "6752": "パナＨＤ", "6753": "シャープ",
    "6758": "ソニーＧ", "6762": "ＴＤＫ", "6770": "アルプスアルパイン", "6841": "横河電機",
    "6857": "アドバンテスト", "6861": "キーエンス", "6902": "デンソー", "6920": "レーザーテック",
    "6952": "カシオ計算機", "6954": "ファナック", "6963": "ローム", "6971": "京セラ",
    "6976": "太陽誘電", "6981": "村田製作所", "7735": "スクリーン", "7751": "キヤノン",
    "7752": "リコー", "8035": "東京エレクトロン", "7201": "日産自動車", "7202": "いすゞ自動車",
    "7203": "トヨタ自動車", "7205": "日野自動車", "7211": "三菱自動車", "7261": "マツダ",
    "7267": "ホンダ", "7269": "スズキ", "7270": "ＳＵＢＡＲＵ", "7272": "ヤマハ発動機",
    "4543": "テルモ", "4902": "コニカミノルタ", "6146": "ディスコ", "7731": "ニコン",
    "7733": "オリンパス", "7741": "ＨＯＹＡ", "9432": "ＮＴＴ", "9433": "ＫＤＤＩ",
    "9434": "ソフトバンク", "9984": "ソフトバンクＧ", "5831": "しずおかＦＧ", "8304": "あおぞら銀行",
    "8306": "三菱ＵＦＪ", "8308": "りそなＨＤ", "8309": "三井住友トラスト", "8316": "三井住友ＦＧ",
    "8331": "千葉銀行", "8354": "ふくおかＦＧ", "8411": "みずほＦＧ", "8253": "クレディセゾン",
    "8591": "オリックス", "8697": "日本取引所", "8601": "大和証券Ｇ", "8604": "野村ＨＤ",
    "8630": "ＳＯＭＰＯ", "8725": "ＭＳ＆ＡＤ", "8750": "第一生命ＨＤ", "8766": "東京海上",
    "8795": "Ｔ＆Ｄ", "1332": "ニッスイ", "2501": "サッポロＨＤ", "2502": "アサヒＧＨＤ",
    "2503": "キリンＨＤ", "2801": "キッコーマン", "2802": "味の素", "2871": "ニチレイ",
    "2914": "ＪＴ", "3086": "Ｊフロント", "3092": "ＺＯＺＯ", "3099": "三越伊勢丹",
    "3382": "セブン＆アイ", "7453": "良品計画", "8233": "高島屋", "8252": "丸井Ｇ",
    "8267": "イオン", "9843": "ニトリＨＤ", "9983": "ファーストリテイリング", "2413": "エムスリー",
    "2432": "ディー・エヌ・エー", "3659": "ネクソン", "3697": "ＳＨＩＦＴ", "4324": "電通グループ",
    "4385": "メルカリ", "4661": "オリエンタルランド", "4689": "ラインヤフー", "4704": "トレンドマイクロ",
    "4751": "サイバーエージェント", "4755": "楽天グループ", "6098": "リクルート", "6178": "日本郵政",
    "6532": "ベイカレント", "7974": "任天堂", "9602": "東宝", "9735": "セコム",
    "9766": "コナミＧ", "1605": "ＩＮＰＥＸ", "3401": "帝人", "3402": "東レ",
    "3861": "王子ＨＤ", "3863": "日本製紙", "3405": "クラレ", "3407": "旭化成",
    "4004": "レゾナック", "4005": "住友化学", "4021": "日産化学", "4042": "東ソー",
    "4043": "トクヤマ", "4061": "デンカ", "4063": "信越化学", "4183": "三井化学",
    "4188": "三菱ケミカルＧ", "4208": "ＵＢＥ", "4452": "花王", "4901": "富士フイルム",
    "4911": "資生堂", "6988": "日東電工", "5019": "出光興産", "5020": "ＥＮＥＯＳ",
    "5101": "横浜ゴム", "5108": "ブリヂストン", "5201": "ＡＧＣ", "5214": "日本電気硝子",
    "5233": "太平洋セメント", "5301": "東海カーボン", "5332": "ＴＯＴＯ", "5333": "日本ガイシ",
    "5401": "日本製鉄", "5406": "神戸製鋼所", "5411": "ＪＦＥ", "3436": "ＳＵＭＣＯ",
    "5706": "三井金属", "5711": "三菱マテリアル", "5713": "住友金属鉱山", "5714": "ＤＯＷＡ",
    "5801": "古河電気工業", "5802": "住友電気工業", "5803": "フジクラ", "2768": "双日",
    "8001": "伊藤忠商事", "8002": "丸紅", "8015": "豊田通商", "8031": "三井物産",
    "8035": "東京エレクトロン", "8053": "住友商事", "8058": "三菱商事", "1721": "コムシスＨＤ",
    "1801": "大成建設", "1802": "大林組", "1803": "清水建設", "1808": "長谷工コーポレーション",
    "1812": "鹿島建設", "1925": "大和ハウス工業", "1928": "積水ハウス", "1963": "日揮ＨＤ",
    "5631": "日本製鋼所", "6103": "オークマ", "6113": "アマダ", "6273": "ＳＭＣ",
    "6301": "小松製作所", "6302": "住友重機械", "6305": "日立建機", "6326": "クボタ",
    "6361": "荏原製作所", "6471": "日本精工", "6472": "ＮＴＮ", "6473": "ジェイテクト",
    "7004": "カナデビア", "7011": "三菱重工業", "7013": "ＩＨＩ", "7012": "川崎重工業",
    "7832": "バンダイナムコ", "7911": "ＴＯＰＰＡＮ", "7912": "大日本印刷", "7951": "ヤマハ",
    "3289": "東急不動産ＨＤ", "8801": "三井不動産", "8802": "三菱地所", "8804": "東京建物",
    "8830": "住友不動産", "9001": "東武鉄道", "9005": "東急", "9007": "小田急電鉄",
    "9008": "京王電鉄", "9009": "京成電鉄", "9020": "ＪＲ東日本", "9021": "ＪＲ西日本",
    "9022": "ＪＲ東海", "9064": "ヤマトＨＤ", "9147": "ＮＸＨＤ", "9101": "日本郵船",
    "9104": "商船三井", "9107": "川崎汽船", "9201": "日本航空", "9202": "ＡＮＡＨＤ",
    "9501": "東京電力ＨＤ", "9502": "中部電力", "9503": "関西電力", "9531": "東京ガス",
    "9532": "大阪ガス"
}

# 東証主要銘柄 (TOPIX100 + 選興銘柄 合計約300-500銘柄をカバーするターゲット)
# 実運用上、主要な銘柄を網羅
TSE_MAJOR_LIST = sorted(list(set(list(NIKKEI225_MAP.keys()) + [
    "1801", "1925", "1928", "2502", "2503", "2801", "2802", "2914", "3382", "3402", "3407",
    "4063", "4188", "4452", "4502", "4503", "4519", "4523", "4543", "4568", "4661", "4901",
    "4911", "5020", "5108", "5401", "5802", "6098", "6146", "6273", "6301", "6367", "6501",
    "6503", "6594", "6702", "6723", "6752", "6758", "6857", "6861", "6902", "6920", "6954",
    "6981", "7011", "7203", "7267", "7741", "7751", "7974", "8001", "8031", "8035", "8053",
    "8058", "8113", "8267", "8306", "8316", "8411", "8591", "8725", "8750", "8766", "8801",
    "8802", "9020", "9022", "9101", "9201", "9432", "9433", "9434", "9502", "9503", "9613",
    "9735", "9843", "9983", "9984"
])))

# --- 2. 補助ユーティリティ ---
def clean_company_name(name: str) -> str:
    if not name: return name
    suffixes = ["Co., Ltd.", "Corp.", "Inc.", "Ltd.", "Corporation", "Group", "Holdings", "Company"]
    for s in suffixes:
        name = name.replace(s, "").replace(s.upper(), "").replace(s.lower(), "")
    return name.strip()

# --- 3. 分析ロジック (キャッシュ適用) ---
@st.cache_data(ttl=3600)
def fetch_and_analyze(symbol: str):
    try:
        yf_symbol = symbol if symbol.endswith(".T") else f"{symbol}.T"
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="2y")
        
        if df.empty or len(df) < 201:
            return None

        pure_symbol = symbol.replace(".T", "")
        company_name = NIKKEI225_MAP.get(pure_symbol, clean_company_name(ticker.info.get('longName', symbol)))

        # 指標計算
        df['MA25'] = ta.sma(df['Close'], length=25)
        df['MA75'] = ta.sma(df['Close'], length=75)
        df['MA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['VolAvg3'] = df['Volume'].rolling(window=3).mean()
        df['VolAvg25'] = df['Volume'].rolling(window=25).mean()
        df['Body'] = (df['Close'] - df['Open']).abs()
        df['LowShadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price = latest['Close']
        
        # MAタッチ判定
        ma_configs = [("MA25", 25, 0.5), ("MA75", 75, 1.0), ("MA200", 200, 1.5)]
        ma_info = {}
        for m_name, _, thresh in ma_configs:
            val = float(latest[m_name])
            prev_val = float(prev[m_name])
            if pd.isna(val) or pd.isna(prev_val):
                ma_info[m_name] = {"diff": 999.0, "up": False}
                continue
            ma_info[m_name] = {"diff": round((price - val) / val * 100, 2), "up": val > prev_val}

        # 追加フィルタ判定
        is_trend = ma_info["MA25"]["up"] or ma_info["MA75"]["up"] or ma_info["MA200"]["up"]
        is_vol_dry = latest['VolAvg3'] < latest['VolAvg25']
        is_hammer = latest['LowShadow'] > (latest['Body'] * 2) if latest['Body'] > 0 else latest['LowShadow'] > 5
        is_rsi_rev = (latest['RSI'] <= 40) and (latest['RSI'] > prev['RSI'])

        ma_tags = [n for n, _, t in ma_configs if abs(ma_info[n]["diff"]) <= t]
        trends = [f"{n}↑" for n, _, _ in ma_configs if ma_info[n]["up"]]

        return {
            "Symbol": pure_symbol, "Name": company_name, "Price": round(price, 1),
            "MA25_diff": ma_info["MA25"]["diff"], "MA75_diff": ma_info["MA75"]["diff"], "MA200_diff": ma_info["MA200"]["diff"],
            "MA25_up": ma_info["MA25"]["up"], "MA75_up": ma_info["MA75"]["up"], "MA200_up": ma_info["MA200"]["up"],
            "RSI": round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else None,
            "RSI_prev": round(prev['RSI'], 1) if not pd.isna(prev['RSI']) else None,
            "VolAvg3": latest['VolAvg3'], "VolAvg25": latest['VolAvg25'],
            "LowShadow": latest['LowShadow'], "Body": latest['Body'],
            "IsTrend": is_trend, "IsVolDry": is_vol_dry, "IsHammer": is_hammer, "IsRsiRev": is_rsi_rev,
            "MA_Tags": ", ".join(ma_tags) if ma_tags else "なし",
            "Trends": ", ".join(trends) if trends else "なし"
        }, df
    except Exception:
        return None

# --- 4. Streamlit UI ---
st.set_page_config(page_title="日本株スクリーナー Pro", layout="wide")

st.markdown("""
<style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    .stDataFrame { border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

st.title("🏹 日本株スクリーナー Pro (最終完成版)")

# サイドバー
st.sidebar.header("🔍 スキャン設定")
scan_mode = st.sidebar.radio("対象範囲", ["日経225", "東証主要銘柄"])

st.sidebar.divider()
st.sidebar.header("🎯 判定ロジック")
f_trend = st.sidebar.checkbox("上昇トレンド限定 (MA上向き)", value=True)
f_vol = st.sidebar.checkbox("売り枯れ判定 (出来高減)", value=False)
f_shadow = st.sidebar.checkbox("下ヒゲ検知 (底打ち反発)", value=False)
f_rsi = st.sidebar.checkbox("RSI反転 (40以下かつ上昇)", value=False)

run_btn = st.sidebar.button("スキャン実行", type="primary", use_container_width=True)

if 'res' not in st.session_state:
    st.session_state.res, st.session_state.plots, st.session_state.sel = None, {}, None

if run_btn:
    tickers = list(NIKKEI225_MAP.keys()) if scan_mode == "日経225" else TSE_MAJOR_LIST
    results, plots = [], {}
    prog = st.progress(0)
    status = st.empty()
    
    for i, s in enumerate(tickers):
        status.text(f"スキャン中... {s} ({i+1}/{len(tickers)})")
        analysis = fetch_and_analyze(s)
        if analysis:
            r, d = analysis
            results.append(r); plots[s] = (r, d)
        prog.progress((i + 1) / len(tickers))
    
    st.session_state.res, st.session_state.plots = results, plots
    status.success("スキャン完了！")

# 表示エリア
if st.session_state.res:
    df_all = pd.DataFrame(st.session_state.res)
    
    # フィルタ
    def filter_logic(df):
        # MAタッチ(いずれか)
        mask = (df['MA25_diff'].abs() <= 0.5) | (df['MA75_diff'].abs() <= 1.0) | (df['MA200_diff'].abs() <= 1.5)
        f_df = df[mask].copy()
        if f_trend: f_df = f_df[f_df['IsTrend']]
        if f_vol: f_df = f_df[f_df['IsVolDry']]
        if f_shadow: f_df = f_df[f_df['IsHammer']]
        if f_rsi: f_df = f_df[f_df['IsRsiRev']]
        return f_df

    df_f = filter_logic(df_all)
    
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader(f"📋 抽出結果: {len(df_f)} 件")
        if df_f.empty:
            st.info("条件に合う銘柄はありませんでした。設定を緩めてみてください。")
        else:
            disp = df_f[["Symbol", "Name", "Price", "RSI", "MA_Tags"]].rename(columns={
                "Symbol": "コード", "Name": "銘柄名", "Price": "現在値", "RSI": "RSI", "MA_Tags": "タッチMA"
            })
            evt = st.dataframe(disp, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            if evt and evt.get("selection") and evt["selection"]["rows"]:
                st.session_state.sel = df_f.iloc[evt["selection"]["rows"][0]]["Symbol"]

    with c2:
        if st.session_state.sel and st.session_state.sel in st.session_state.plots:
            res_s, df_s = st.session_state.plots[st.session_state.sel]
            st.subheader(f"📊 {res_s['Name']} ({st.session_state.sel})")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_s.index, open=df_s['Open'], high=df_s['High'], low=df_s['Low'], close=df_s['Close'], name='価格'))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA25'], name='25日', line=dict(color='yellow', width=1)))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA75'], name='75日', line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA200'], name='200日', line=dict(color='red', width=1)))
            
            fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("現在値", f"¥{res_s['Price']}")
            m2.metric("RSI", f"{res_s['RSI']}", delta=round(res_s['RSI'] - res_s['RSI_prev'], 1) if res_s['RSI_prev'] else None)
            m3.metric("MA傾向", res_s['Trends'].split(",")[0] if res_s['Trends'] != "なし" else "平坦")
        else:
            st.info("👈 左側のリストから銘柄を選択してチャートを表示")
