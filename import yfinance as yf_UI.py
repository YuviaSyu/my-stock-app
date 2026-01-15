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
st.write("輸入股票代碼，支援上市 (.TW) 與 上櫃 (.TWO) 自動辨識！")

# --- 使用者輸入介面 ---
col1, col2 = st.columns([3, 1])
with col1:
    code_input = st.text_input("請輸入股票代碼 (例如 2330 或 5314):", value="2330")
with col2:
    st.write("") 
    st.write("") 
    analyze_button = st.button("📊 開始診斷")

# --- 診斷邏輯觸發 ---
if analyze_button and code_input:
    code = code_input.strip().upper()
    
    # 預設先抓上市 (.TW)
    ticker = f"{code}.TW" if code.isdigit() else code
    
    with st.spinner(f"正在分析 {ticker}..."):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="4mo", auto_adjust=True)
            
            # --- 【關鍵修正位置】 ---
            # 如果抓不到資料且是純數字，代表可能是上櫃公司，自動改抓 .TWO
            if df.empty and code.isdigit():
                ticker = f"{code}.TWO"
                stock = yf.Ticker(ticker)
                df = stock.history(period="4mo", auto_adjust=True)
            # ------------------------

            if df.empty:
                st.error(f"❌ 無法獲取代碼 '{code}' 的數據。")
            else:
                # 獲取公司名稱
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

                # 計算建議價格
                buy_price_limit = ma20 * 1.02
                target_profit_price = ma20 * 1.10
                stop_loss_price = ma20

                st.markdown(f"### 🔍 **{stock_name}** ({ticker}) 診斷報告")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("**當前市價**", f"{price:.2f}")
                c2.metric("**月線 (MA20)**", f"{ma20:.2f}")
                c3.metric("**月線乖離率**", f"{bias:.2f}%")

                st.markdown("---")

                # 操作建議
                col_buy, col_sell = st.columns(2)
                with col_buy:
                    st.subheader("📥 買入策略")
                    if price > buy_price_limit:
                        st.warning(f"目前價格偏高，建議等拉回")
                        st.write(f"💡 理想買點：**{ma20:.2f} ~ {buy_price_limit:.2f}**")
                    else:
                        st.success(f"目前處於合理買進區間")
                        st.write(f"💡 建議買入點：**{price:.2f}** 附近")

                with col_sell:
                    st.subheader("📤 賣出策略")
                    st.write(f"💰 建議停利價：**{target_profit_price:.2f}**")
                    st.write(f"🚨 建議停損價：**{stop_loss_price:.2f}** (跌破月線)")

                st.markdown("---")
                
                # 量能判斷
                if volume > vol_ma5 * 1.5:
                    st.warning(f"⚠️ 現況：爆量。當前量能為均量的 {volume/vol_ma5:.1f} 倍。")
                elif volume < vol_ma5 * 0.7:
                    st.info(f"📉 現況：縮量。市場觀望氣氛濃厚。")

                st.line_chart(df[['Close', 'MA20']])

        except Exception as e:
            st.error(f"分析時發生錯誤：{e}")

st.markdown("---")
st.caption("數據來源: Yahoo Finance. 僅供參考，不構成投資建議。")