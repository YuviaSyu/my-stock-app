import streamlit as st
import yfinance as yf
import pandas as pd

# --- Streamlit 網頁基本設定 ---
st.set_page_config(
    page_title="📈 股票智能診斷 APP", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("📈 股票智能診斷 APP")
st.markdown("---")
st.write("輸入股票代碼，獲取精確的 **建議買入/賣出價格**！")

# --- 使用者輸入介面 ---
col1, col2 = st.columns([3, 1])
with col1:
    code_input = st.text_input("請輸入股票代碼 (例如 2330 或 AAPL):", value="2330")
with col2:
    st.write("") 
    st.write("") 
    analyze_button = st.button("📊 開始診斷")

if analyze_button and code_input:
    ticker = f"{code_input.strip().upper()}.TW" if code_input.strip().isdigit() else code_input.strip().upper()
    
    with st.spinner(f"正在分析 {ticker} 的精確價格建議..."):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="4mo", auto_adjust=True)
            
            if df.empty:
                st.error(f"❌ 無法獲取代碼 '{ticker}'")
            else:
                try:
                    info = stock.info
                    stock_name = info.get('shortName') or info.get('longName') or ticker
                except:
                    stock_name = ticker

                # 指標計算
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['VolMA5'] = df['Volume'].rolling(window=5).mean()
                
                price = float(df['Close'].iloc[-1])
                ma20 = float(df['MA20'].iloc[-1])
                ma5 = float(df['MA5'].iloc[-1])
                vol_ma5 = float(df['VolMA5'].iloc[-1])
                volume = float(df['Volume'].iloc[-1])
                bias = ((price - ma20) / ma20) * 100

                # --- 計算精確建議價格 ---
                buy_price_limit = ma20 * 1.02  # 買入區間上限：月線 +2%
                target_profit_price = ma20 * 1.10 # 停利目標：月線 +10%
                stop_loss_price = ma20 # 停損點：跌破月線

                # 顯示報告
                st.markdown(f"### 🔍 **{stock_name}** ({ticker}) 價格分析")
                
                # 核心指標卡片
                c1, c2, c3 = st.columns(3)
                c1.metric("**當前市價**", f"{price:.2f}")
                c2.metric("**關鍵月線 (MA20)**", f"{ma20:.2f}")
                c3.metric("**月線乖離率**", f"{bias:.2f}%")

                st.markdown("---")

                # --- 價格操作建議區 ---
                col_buy, col_sell = st.columns(2)

                with col_buy:
                    st.subheader("📥 買入策略")
                    if price > buy_price_limit:
                        st.warning(f"目前價格 ({price:.2f}) 偏高")
                        st.write(f"💡 建議等待拉回至：**{ma20:.2f} ~ {buy_price_limit:.2f}**")
                    else:
                        st.success(f"目前處於合理買進區間")
                        st.write(f"💡 建議買入點：**{price:.2f}** 附近")

                with col_sell:
                    st.subheader("📤 賣出策略")
                    st.write(f"💰 建議停利價：**{target_profit_price:.2f}** (預期 10% 獲利)")
                    st.write(f"🚨 建議停損價：**{stop_loss_price:.2f}** (跌破月線)")

                st.markdown("---")
                
                # --- 原有的量能與診斷邏輯 ---
                st.subheader("📈 綜合診斷")
                
                # 量能判斷
                if volume > vol_ma5 * 1.5:
                    st.warning(f"⚠️ 現況：爆量。當前量能為均量的 {volume/vol_ma5:.1f} 倍。")
                elif volume < vol_ma5 * 0.7:
                    st.info(f"📉 現況：縮量。市場觀望氣氛濃厚。")
                
                # 買賣具體文字建議
                if price < ma20:
                    st.error(f"🔴 趨勢診斷：跌破月線。除非站回 {ma20:.2f}，否則不建議持有。")
                elif bias > 10:
                    st.warning(f"🟠 趨勢診斷：過熱。目前已達目標停利區間，建議開始分批落袋。")
                else:
                    st.success(f"🟢 趨勢診斷：多頭格局。回測 {ma20:.2f} 若不破，仍是好買點。")

                st.line_chart(df[['Close', 'MA20']])

        except Exception as e:
            st.error(f"分析時發生錯誤：{e}")

st.caption("註：建議價格僅基於 MA20 計算，投資有風險，請自行斟酌。")