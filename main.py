import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from typing import Dict, Any, List

# --- 1. 銘柄データ定義 ---
# カテゴリ別主要銘柄
TSE_CATEGORIES = {
    "日経225 (全銘柄)": [], 
    "半導体・ハイテク": ["6857", "8035", "6920", "6146", "7735", "6723", "4062", "6861", "6981"],
    "電気・精密機器": ["6501", "6758", "6702", "6762", "7741", "7733", "7751", "4543"],
    "機械・産業機器": ["6301", "6367", "6326", "6273", "6113", "6471", "7011", "7013"],
    "鉄鋼・非鉄・資源": ["5401", "5411", "5406", "5713", "5541", "5711", "5706", "1605"],
    "金融・銀行・保険": ["8306", "8316", "8411", "8308", "8309", "8591", "8766", "8725", "8601", "8604"],
    "総合商社": ["8001", "8002", "8031", "8053", "8058", "2768"],
    "自動車・輸送機器": ["7203", "7267", "7201", "7269", "7272", "7202", "6902", "9101", "9147"],
    "通信・IT・ゲーム": ["9432", "9433", "9434", "9984", "7974", "3659", "4755", "4689", "6098"],
    "建設・プラント": ["1801", "1802", "1803", "1812", "1925", "1928", "1963"],
    "不動産・住宅": ["8801", "8802", "8830", "3289", "8804"],
    "化学・医薬品": ["4063", "4188", "4452", "4901", "4502", "4503", "4519", "4568"],
    "食品・小売": ["2502", "2503", "2914", "9983", "8267", "3382", "9843", "7453"]
}

# 銘柄名マッピング
STOCK_NAME_MAP = {
    "5541": "太平洋金属",
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
    "8053": "住友商事", "8058": "三菱商事", "1721": "コムシスＨＤ",
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
    "9532": "大阪ガス", "6367": "ダイキン工業", "6594": "ニデック", "8113": "ユニ・チャーム",
    "9613": "エヌ・ティ・ティ・データ", "8035": "東京エレクトロン"
}

# --- 2. 補助ユーティリティ ---
def clean_company_name(name: str) -> str:
    if not name: return name
    suffixes = ["Co., Ltd.", "Corp.", "Inc.", "Ltd.", "Corporation", "Group", "Holdings", "Company"]
    for s in suffixes:
        name = name.replace(s, "").replace(s.upper(), "").replace(s.lower(), "")
    return name.strip()

# --- 3. 分析ロジック ---
@st.cache_data(ttl=3600)
def fetch_and_analyze(symbol: str):
    try:
        yf_symbol = symbol if symbol.endswith(".T") else f"{symbol}.T"
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="2y")
        
        if df.empty or len(df) < 201:
            return None

        pure_symbol = symbol.replace(".T", "")
        company_name = STOCK_NAME_MAP.get(pure_symbol, clean_company_name(ticker.info.get('longName', symbol)))

        # 指標計算
        df['MA5'] = ta.sma(df['Close'], length=5)
        df['MA25'] = ta.sma(df['Close'], length=25)
        df['MA75'] = ta.sma(df['Close'], length=75)
        df['MA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['VolAvg3'] = df['Volume'].rolling(window=3).mean()
        df['VolAvg25'] = df['Volume'].rolling(window=25).mean()
        df['Body'] = (df['Close'] - df['Open']).abs()
        df['LowShadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']

        # シグナル判定 (5日線と25日線の交差)
        df['GC'] = (df['MA5'] > df['MA25']) & (df['MA5'].shift(1) <= df['MA25'].shift(1))
        df['DC'] = (df['MA5'] < df['MA25']) & (df['MA5'].shift(1) >= df['MA25'].shift(1))

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price = latest['Close']
        
        # ファンダメンタル情報の取得 (yfinanceの仕様に合わせて調整)
        info = ticker.info
        per = info.get('trailingPE')
        pbr = info.get('priceToBook')
        div_raw = info.get('dividendYield', 0) or 0
        # 0.2を超える場合は既に%表記であると判断（例: 2.79% -> 2.79）
        div_yield = div_raw if div_raw > 0.2 else div_raw * 100
        
        # MA乖離
        ma_info = {}
        for m_name in ["MA25", "MA75", "MA200"]:
            val = float(latest[m_name])
            ma_info[m_name] = {"val": val, "diff": round((price - val) / val * 100, 2), "up": val > prev[m_name]}

        return {
            "Symbol": pure_symbol, "Name": company_name, "Price": round(price, 1),
            "MA25_diff": ma_info["MA25"]["diff"], "MA75_diff": ma_info["MA75"]["diff"], "MA200_diff": ma_info["MA200"]["diff"],
            "MA25_up": ma_info["MA25"]["up"], "MA75_up": ma_info["MA75"]["up"], "MA200_up": ma_info["MA200"]["up"],
            "RSI": round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else None,
            "RSI_prev": round(prev['RSI'], 1) if not pd.isna(prev['RSI']) else None,
            "IsTrend": ma_info["MA25"]["up"] or ma_info["MA75"]["up"] or ma_info["MA200"]["up"],
            "IsVolDry": latest['VolAvg3'] < latest['VolAvg25'],
            "IsHammer": latest['LowShadow'] > (latest['Body'] * 2) if latest['Body'] > 0 else latest['LowShadow'] > 5,
            "IsRsiRev": (latest['RSI'] <= 40) and (latest['RSI'] > prev['RSI']),
            "PER": round(per, 1) if per else None,
            "PBR": round(pbr, 2) if pbr else None,
            "DivYield": round(div_yield, 2),
            "Volume": int(latest['Volume'])
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

st.title("🏹 日本株スクリーナー Pro (最終版)")

# サイドバー
st.sidebar.header("🔍 スキャン設定")
category_sel = st.sidebar.selectbox("スキャン対象 (ジャンル)", list(TSE_CATEGORIES.keys()))

st.sidebar.divider()
st.sidebar.header("🎯 判定ロジック")
st.sidebar.subheader("MAタッチ判定 (複数選択可)")
use_ma25 = st.sidebar.checkbox("25日線タッチ", value=True)
tol_ma25 = st.sidebar.slider("25日線 許容誤差 (±%)", 0.0, 5.0, 0.5, 0.1)
use_ma75 = st.sidebar.checkbox("75日線タッチ", value=True)
tol_ma75 = st.sidebar.slider("75日線 許容誤差 (±%)", 0.0, 5.0, 1.0, 0.1)
use_ma200 = st.sidebar.checkbox("200日線タッチ", value=True)
tol_ma200 = st.sidebar.slider("200日線 許容誤差 (±%)", 0.0, 5.0, 1.5, 0.1)

st.sidebar.subheader("追加フィルタ")
f_trend = st.sidebar.checkbox("上昇トレンド限定 (MA上向き)", value=True)
f_vol_dry = st.sidebar.checkbox("売り枯れ判定 (出来高減少)", value=False)
f_shadow = st.sidebar.checkbox("下ヒゲ検知 (反発期待)", value=False)
f_rsi = st.sidebar.checkbox("RSI反転 (40以下から反転)", value=False)
f_vol_100k = st.sidebar.checkbox("出来高10万株以上", value=True)

st.sidebar.divider()
st.sidebar.header("💼 ファンダメンタル")
max_per = st.sidebar.slider("PER 15倍以下など (上限)", 0.0, 100.0, 100.0)
max_pbr = st.sidebar.slider("PBR 1倍以下など (上限)", 0.0, 10.0, 10.0)
min_yield = st.sidebar.slider("配当利回り %以上 (下限)", 0.0, 10.0, 0.0)

st.sidebar.divider()
st.sidebar.header("📈 チャート設定")
show_signals = st.sidebar.toggle("売買シグナルを表示 (5/25 GC・DC)", value=True)

run_btn = st.sidebar.button("スキャン開始", type="primary", use_container_width=True)

if 'res' not in st.session_state:
    st.session_state.res, st.session_state.plots, st.session_state.sel = None, {}, None

if run_btn:
    tickers = list(STOCK_NAME_MAP.keys()) if category_sel == "日経225 (全銘柄)" else TSE_CATEGORIES[category_sel]
    results, plots = [], {}
    prog = st.progress(0)
    status = st.empty()
    
    for i, s in enumerate(tickers):
        status.text(f"分析中... {s} ({i+1}/{len(tickers)})")
        analysis = fetch_and_analyze(s)
        if analysis:
            r, d = analysis
            results.append(r); plots[s] = (r, d)
        prog.progress((i + 1) / len(tickers))
    
    st.session_state.res, st.session_state.plots = results, plots
    st.success(f"スキャン完了！ ({len(results)}銘柄のデータを取得)")

# 表示エリア
if st.session_state.res:
    df_all = pd.DataFrame(st.session_state.res)
    
    def filter_logic(df):
        # MAタッチ判定 (選択時のみ適用、OR条件)
        ma_filters = []
        if use_ma25: ma_filters.append(df['MA25_diff'].abs() <= tol_ma25)
        if use_ma75: ma_filters.append(df['MA75_diff'].abs() <= tol_ma75)
        if use_ma200: ma_filters.append(df['MA200_diff'].abs() <= tol_ma200)
        
        if ma_filters:
            ma_mask = ma_filters[0]
            for f in ma_filters[1:]:
                ma_mask |= f
            f_df = df[ma_mask].copy()
        else:
            f_df = df.copy() # MA判定チェックなしなら全件表示
            
        if f_trend: f_df = f_df[f_df['IsTrend']]
        if f_vol_dry: f_df = f_df[f_df['IsVolDry']]
        if f_shadow: f_df = f_df[f_df['IsHammer']]
        if f_rsi: f_df = f_df[f_df['IsRsiRev']]
        if f_vol_100k: f_df = f_df[f_df['Volume'] >= 100000]
        
        # ファンダメンタルフィルタ (値がある場合のみ、0を除く)
        if max_per < 100:
            f_df = f_df[f_df['PER'].fillna(999) <= max_per]
        if max_pbr < 10:
            f_df = f_df[f_df['PBR'].fillna(99) <= max_pbr]
        if min_yield > 0:
            f_df = f_df[f_df['DivYield'].fillna(0) >= min_yield]
        
        return f_df

    df_filtered = filter_logic(df_all)
    
    c1, c2 = st.columns([1, 1.3])
    
    with c1:
        st.subheader(f"📋 抽出結果: {len(df_filtered)} 件")
        if df_filtered.empty:
            st.info("条件に合う銘柄はありませんでした。フィルタを緩和してください。")
        else:
            # 表示データの加工
            def get_touched_ma(row):
                t = []
                if abs(row['MA25_diff']) <= tol_ma25: t.append("25日")
                if abs(row['MA75_diff']) <= tol_ma75: t.append("75日")
                if abs(row['MA200_diff']) <= tol_ma200: t.append("200日")
                return ", ".join(t) if t else "-"
            
            def get_primary_kairi(row):
                # 選択されているMAのうち、最も近いものの乖離率を返す
                diffs = []
                if use_ma25: diffs.append(row['MA25_diff'])
                if use_ma75: diffs.append(row['MA75_diff'])
                if use_ma200: diffs.append(row['MA200_diff'])
                if not diffs: return row['MA25_diff'] # デフォルト
                # 絶対値が最小（最も近い）ものを選択
                return min(diffs, key=abs)

            df_filtered['タッチMA'] = df_filtered.apply(get_touched_ma, axis=1)
            df_filtered['乖離率'] = df_filtered.apply(get_primary_kairi, axis=1)
            
            disp = df_filtered[["Symbol", "Name", "Price", "乖離率", "RSI", "タッチMA"]].rename(columns={
                "Symbol": "コード", "Name": "銘柄名", "Price": "現在値", "乖離率": "乖離率(%)", "RSI": "RSI"
            })
            
            # スキャン統計の表示
            st.caption(f"全体 {len(df_all)} 銘柄中 {len(df_filtered)} 銘柄が条件に一致")
            
            selection = st.dataframe(
                disp, use_container_width=True, hide_index=True, 
                on_select="rerun", selection_mode="single-row"
            )
            
            if selection and selection.get("selection") and selection["selection"]["rows"]:
                st.session_state.sel = df_filtered.iloc[selection["selection"]["rows"][0]]["Symbol"]

    with c2:
        if st.session_state.sel and st.session_state.sel in st.session_state.plots:
            res_s, df_s = st.session_state.plots[st.session_state.sel]
            st.subheader(f"📈 {res_s['Name']} ({st.session_state.sel})")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_s.index, open=df_s['Open'], high=df_s['High'], low=df_s['Low'], close=df_s['Close'], name='株価'))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA25'], name='25日', line=dict(color='yellow', width=1)))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA75'], name='75日', line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['MA200'], name='200日', line=dict(color='red', width=1)))
            
            # 売買シグナルの表示
            if show_signals:
                gc_df = df_s[df_s['GC']]
                dc_df = df_s[df_s['DC']]
                fig.add_trace(go.Scatter(
                    x=gc_df.index, y=gc_df['Low'] * 0.98,
                    mode='markers+text', name='BUY (GC)',
                    marker=dict(symbol='triangle-up', size=12, color='lime'),
                    text="▲BUY", textposition="bottom center"
                ))
                fig.add_trace(go.Scatter(
                    x=dc_df.index, y=dc_df['High'] * 1.02,
                    mode='markers+text', name='SELL (DC)',
                    marker=dict(symbol='triangle-down', size=12, color='red'),
                    text="▼SELL", textposition="top center"
                ))
            
            fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("株価", f"¥{res_s['Price']}")
            m2.metric("RSI", f"{res_s['RSI']}", delta=round(res_s['RSI'] - res_s['RSI_prev'], 1) if res_s['RSI_prev'] else None)
            
            trends = []
            if res_s['MA25_up']: trends.append("25日↑")
            if res_s['MA75_up']: trends.append("75日↑")
            if res_s['MA200_up']: trends.append("200日↑")
            m3.metric("傾向", trends[0] if trends else "下向き")
            
            m4.metric("配当利回り", f"{res_s['DivYield']}%")

            # 詳細ファンダメンタル表示
            f1, f2, f3 = st.columns(3)
            f1.metric("PER", f"{res_s['PER']}倍" if res_s['PER'] else "-")
            f2.metric("PBR", f"{res_s['PBR']}倍" if res_s['PBR'] else "-")
            f3.metric("出来高", f"{res_s['Volume']:,}枚")
        else:
            st.info("👈 左側のリストから銘柄を選択してチャートを表示")

st.sidebar.markdown("---")
st.sidebar.caption("Data: Yahoo Finance")
