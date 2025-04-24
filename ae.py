import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
# 字型設定（避免重複導入 plt）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
#

# 設定 API 金鑰（建議改為環境變數）
load_dotenv()  # 讀取 .env 檔案
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key



# 讀取資料並轉換數值型態
df_113 = pd.read_excel("11309a (1).xlsx", sheet_name="Sheet1")
df_112 = pd.read_excel("11209.xlsx", sheet_name="工作表1")

df_113['錄取總分數'] = pd.to_numeric(df_113['錄取總分數'], errors='coerce')
df_112['錄取總分數'] = pd.to_numeric(df_112['錄取總分數'], errors='coerce')

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 5px;}
    .stNumberInput input {border-radius: 5px;}
    h1, h2, h3 {color: #2C3E50;}
    .stSelectbox {margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# 主標題與簡介
st.title("📚 學生成績分發系統")
st.markdown("**探索 112 與 113 學年錄取資訊，輸入成績即刻評估！**", unsafe_allow_html=True)
st.markdown("---")

# 年度選擇
with st.container():
    st.subheader("步驟 1：選擇查詢年度")
    year_option = st.radio("選擇年度：", ["113", "112", "全部"], horizontal=True, key="year_radio")

# 合併資料
if year_option == "全部":
    df_113["年度"] = "113"
    df_112["年度"] = "112"
    df = pd.concat([df_113, df_112], ignore_index=True)
else:
    df = df_113 if year_option == "113" else df_112

# 學校與科系選擇
with st.container():
    st.subheader("步驟 2：選擇學校與科系")
    
    # 添加學校類型選擇
    school_type = st.radio("學校類型：", ["全部", "公立", "私立"], horizontal=True, key="school_type")
    
    # 根據學校類型篩選學校
    if school_type == "公立":
        filtered_schools = [school for school in df["學校名稱"].unique() if school.startswith("國立")]
    elif school_type == "私立":
        filtered_schools = [school for school in df["學校名稱"].unique() if not school.startswith("國立")]
    else:  # 全部
        filtered_schools = df["學校名稱"].unique()
    
    col1, col2 = st.columns(2)
    with col1:
        school_name = st.selectbox("學校名稱", filtered_schools, key="school_select")
    with col2:
        filtered_df = df[df["學校名稱"] == school_name]
        department_name = st.selectbox("科系名稱", filtered_df["系科組學程名稱"].unique(), key="dept_select")

# 顯示加權資料與錄取資訊
if department_name:
    selected_rows = df[(df["學校名稱"] == school_name) & (df["系科組學程名稱"] == department_name)]
    if selected_rows.empty:
        st.warning("⚠️ 查無資料")
    else:
        with st.container():
            st.subheader("📊 錄取加權與分數資訊")
            for index, row in selected_rows.iterrows():
                st.markdown(f"#### 年度：{row['年度'] if '年度' in row else year_option}")
                st.write(f"加權公式：國文 × {row['國文加權']} + 英文 × {row[' 英文加權']} + 數學 × {row[' 數學加權']} + 專業(一) × {row[' 專業(一)加權']} + 專業(二) × {row[' 專業(二)加權']}")
                st.info(f"錄取總分（參考）：**{row['錄取總分數']:.2f} 分**")

        # 年度比較與柱狀圖
        if year_option == "全部" and len(selected_rows) == 2:
            with st.expander("🔍 查看年度比較", expanded=True):
                row_113 = selected_rows[selected_rows["年度"] == "113"].iloc[0]
                row_112 = selected_rows[selected_rows["年度"] == "112"].iloc[0]

                def compare_val(a, b):
                    diff = a - b
                    return f"{a:.2f} ({'↑' if diff > 0 else '↓' if diff < 0 else '='} {abs(diff):.2f})"

                # 美化表格
                st.markdown("**加權與總分比較表**")
                table_data = {
                    "項目": ["國文加權", "英文加權", "數學加權", "專業(一)加權", "專業(二)加權", "錄取總分"],
                    "113": [row_113[col] for col in ["國文加權", " 英文加權", " 數學加權", " 專業(一)加權", " 專業(二)加權", "錄取總分數"]],
                    "112": [row_112[col] for col in ["國文加權", " 英文加權", " 數學加權", " 專業(一)加權", " 專業(二)加權", "錄取總分數"]],
                    "差異": [compare_val(row_113[col], row_112[col]) for col in ["國文加權", " 英文加權", " 數學加權", " 專業(一)加權", " 專業(二)加權", "錄取總分數"]]
                }
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

                # 美化柱狀圖
                st.markdown("**錄取總分柱狀圖**")
                fig, ax = plt.subplots(figsize=(6, 4))
                years = ['112', '113']
                scores = [float(row_112['錄取總分數']), float(row_113['錄取總分數'])]
                bars = ax.bar(years, scores, color=['#4CAF50', '#2196F3'], edgecolor='black', linewidth=1)
                ax.set_xlabel('學年', fontsize=12)
                ax.set_ylabel('錄取總分', fontsize=12)
                ax.set_title(f'{school_name} {department_name}\n錄取總分比較', fontsize=14, pad=10)
                ax.set_ylim(0, max(scores) * 1.15)
                ax.grid(True, linestyle='--', alpha=0.7)
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.2f}', ha='center', va='bottom', fontsize=10)
                st.pyplot(fig)

        # 輸入成績區塊
        with st.container():
            st.subheader("步驟 3：輸入您的成績")
            st.write("請輸入 0~100 分之間的成績：")
            col3, col4 = st.columns(2)
            with col3:
                chinese_score = st.number_input("國文成績", min_value=0, max_value=100, step=1, value=0, key="chinese")
                english_score = st.number_input("英文成績", min_value=0, max_value=100, step=1, value=0, key="english")
                math_score = st.number_input("數學成績", min_value=0, max_value=100, step=1, value=0, key="math")
            with col4:
                special_one_score = st.number_input("專業(一)成績", min_value=0, max_value=100, step=1, value=0, key="special1")
                special_two_score = st.number_input("專業(二)成績", min_value=0, max_value=100, step=1, value=0, key="special2")

            if st.button("計算成績", key="calc_button"):
                # 如果選擇了"全部"，則需要分別計算 113 和 112 的結果
                if year_option == "全部" and len(selected_rows) == 2:
                    # 獲取 113 和 112 的數據
                    row_113 = selected_rows[selected_rows["年度"] == "113"].iloc[0]
                    row_112 = selected_rows[selected_rows["年度"] == "112"].iloc[0]
                    
                    # 計算 113 年度的加權分數
                    chinese_weight_113 = row_113['國文加權']
                    english_weight_113 = row_113[' 英文加權']
                    math_weight_113 = row_113[' 數學加權']
                    special_one_weight_113 = row_113[' 專業(一)加權']
                    special_two_weight_113 = row_113[' 專業(二)加權']
                    admission_score_113 = row_113['錄取總分數']
                    
                    weighted_total_113 = (chinese_score * chinese_weight_113 +
                                          english_score * english_weight_113 +
                                          math_score * math_weight_113 +
                                          special_one_score * special_one_weight_113 +
                                          special_two_score * special_two_weight_113)
                    total_weight_113 = chinese_weight_113 + english_weight_113 + math_weight_113 + special_one_weight_113 + special_two_weight_113
                    weighted_average_113 = weighted_total_113 / total_weight_113 if total_weight_113 > 0 else 0
                    
                    # 計算 112 年度的加權分數
                    chinese_weight_112 = row_112['國文加權']
                    english_weight_112 = row_112[' 英文加權']
                    math_weight_112 = row_112[' 數學加權']
                    special_one_weight_112 = row_112[' 專業(一)加權']
                    special_two_weight_112 = row_112[' 專業(二)加權']
                    admission_score_112 = row_112['錄取總分數']
                    
                    weighted_total_112 = (chinese_score * chinese_weight_112 +
                                          english_score * english_weight_112 +
                                          math_score * math_weight_112 +
                                          special_one_score * special_one_weight_112 +
                                          special_two_score * special_two_weight_112)
                    total_weight_112 = chinese_weight_112 + english_weight_112 + math_weight_112 + special_one_weight_112 + special_two_weight_112
                    weighted_average_112 = weighted_total_112 / total_weight_112 if total_weight_112 > 0 else 0
                    
                    # 計算差異
                    def compare_val(a, b):
                        diff = a - b
                        return f"{diff:+.2f}"
                    
                    # 顯示比較表格
                    st.markdown("### 年度比較結果")
                    
                    # 創建比較表格
                    compare_data = {
                        "項目": ["加權總分", "加權平均", "錄取總分", "是否達到錄取標準"],
                        "113年度": [
                            f"{weighted_total_113:.2f} 分",
                            f"{weighted_average_113:.2f} 分",
                            f"{admission_score_113:.2f} 分",
                            "✅ 已達到" if weighted_total_113 >= admission_score_113 else "❌ 未達到"
                        ],
                        "112年度": [
                            f"{weighted_total_112:.2f} 分",
                            f"{weighted_average_112:.2f} 分",
                            f"{admission_score_112:.2f} 分",
                            "✅ 已達到" if weighted_total_112 >= admission_score_112 else "❌ 未達到"
                        ],
                        "差異": [
                            compare_val(weighted_total_113, weighted_total_112),
                            compare_val(weighted_average_113, weighted_average_112),
                            compare_val(admission_score_113, admission_score_112),
                            "相同" if (weighted_total_113 >= admission_score_113) == (weighted_total_112 >= admission_score_112) else "不同"
                        ]
                    }
                    compare_df = pd.DataFrame(compare_data)
                    st.table(compare_df)
                    
                    # 顯示詳細的加權計算
                    with st.expander("查看詳細加權計算", expanded=False):
                        # 113 年度加權計算
                        st.markdown("#### 113 年度加權計算")
                        weight_data_113 = {
                            "科目": ["國文", "英文", "數學", "專業(一)", "專業(二)", "總計"],
                            "原始分數": [
                                f"{chinese_score:.2f}",
                                f"{english_score:.2f}",
                                f"{math_score:.2f}",
                                f"{special_one_score:.2f}",
                                f"{special_two_score:.2f}",
                                f"{chinese_score + english_score + math_score + special_one_score + special_two_score:.2f}"
                            ],
                            "加權值": [
                                f"{chinese_weight_113:.2f}",
                                f"{english_weight_113:.2f}",
                                f"{math_weight_113:.2f}",
                                f"{special_one_weight_113:.2f}",
                                f"{special_two_weight_113:.2f}",
                                f"{total_weight_113:.2f}"
                            ],
                            "加權分數": [
                                f"{chinese_score * chinese_weight_113:.2f}",
                                f"{english_score * english_weight_113:.2f}",
                                f"{math_score * math_weight_113:.2f}",
                                f"{special_one_score * special_one_weight_113:.2f}",
                                f"{special_two_score * special_two_weight_113:.2f}",
                                f"{weighted_total_113:.2f}"
                            ]
                        }
                        weight_df_113 = pd.DataFrame(weight_data_113)
                        st.table(weight_df_113)
                        
                        # 112 年度加權計算
                        st.markdown("#### 112 年度加權計算")
                        weight_data_112 = {
                            "科目": ["國文", "英文", "數學", "專業(一)", "專業(二)", "總計"],
                            "原始分數": [
                                f"{chinese_score:.2f}",
                                f"{english_score:.2f}",
                                f"{math_score:.2f}",
                                f"{special_one_score:.2f}",
                                f"{special_two_score:.2f}",
                                f"{chinese_score + english_score + math_score + special_one_score + special_two_score:.2f}"
                            ],
                            "加權值": [
                                f"{chinese_weight_112:.2f}",
                                f"{english_weight_112:.2f}",
                                f"{math_weight_112:.2f}",
                                f"{special_one_weight_112:.2f}",
                                f"{special_two_weight_112:.2f}",
                                f"{total_weight_112:.2f}"
                            ],
                            "加權分數": [
                                f"{chinese_score * chinese_weight_112:.2f}",
                                f"{english_score * english_weight_112:.2f}",
                                f"{math_score * math_weight_112:.2f}",
                                f"{special_one_score * special_one_weight_112:.2f}",
                                f"{special_two_score * special_two_weight_112:.2f}",
                                f"{weighted_total_112:.2f}"
                            ]
                        }
                        weight_df_112 = pd.DataFrame(weight_data_112)
                        st.table(weight_df_112)
                    
                    # 顯示加權公式
                    st.markdown("#### 113 年度加權公式")
                    st.info(f"國文 × {chinese_weight_113} + 英文 × {english_weight_113} + 數學 × {math_weight_113} + 專業(一) × {special_one_weight_113} + 專業(二) × {special_two_weight_113}")
                    
                    st.markdown("#### 112 年度加權公式")
                    st.info(f"國文 × {chinese_weight_112} + 英文 × {english_weight_112} + 數學 × {math_weight_112} + 專業(一) × {special_one_weight_112} + 專業(二) × {special_two_weight_112}")
                    
                    # 處理錄取結果
                    if weighted_total_113 >= admission_score_113:
                        st.success(f"🎉 恭喜！您的加權總分 ({weighted_total_113:.2f}) 達到或超過 113 年度錄取總分 ({admission_score_113:.2f})！")
                        prompt = f"使用者錄取了 {school_name} 的 {department_name}，請提供該學校與科系的相關資訊。"
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=500
                        )
                        st.write("### 錄取學校與科系資訊")
                        st.write(response.choices[0].message["content"])
                    else:
                        st.warning(f"⚠️ 您的加權總分 ({weighted_total_113:.2f}) 低於 113 年度錄取總分 ({admission_score_113:.2f})，差 {admission_score_113 - weighted_total_113:.2f} 分。")
                        similar_df = df[(df["錄取總分數"] <= weighted_total_113 + 50) & (df["錄取總分數"] >= weighted_total_113 - 50)].head(3)
                        if not similar_df.empty:
                            st.write("### 建議：分數相近的學校與科系")
                            for index, row in similar_df.iterrows():
                                st.write(f"- {row['學校名稱']} - {row['系科組學程名稱']}（錄取總分：{row['錄取總分數']:.2f} 分）")
                        else:
                            st.write("目前資料中沒有分數相近的學校與科系可推薦。")
                        prompt = f"使用者的加權總分為 {weighted_total_113:.2f}，未達到 {school_name} 的 {department_name} 錄取總分 {admission_score_113:.2f}，請提供建議或鼓勵的話。"
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=500
                        )
                        st.write("### AI 建議")
                        st.write(response.choices[0].message["content"])
                else:
                    # 原有的單一年度計算邏輯
                    for idx, row in selected_rows.iterrows():
                        chinese_weight = row['國文加權']
                        english_weight = row[' 英文加權']
                        math_weight = row[' 數學加權']
                        special_one_weight = row[' 專業(一)加權']
                        special_two_weight = row[' 專業(二)加權']
                        admission_score = row['錄取總分數']
                        year = row['年度'] if '年度' in row else year_option

                        weighted_total = (chinese_score * chinese_weight +
                                          english_score * english_weight +
                                          math_score * math_weight +
                                          special_one_score * special_one_weight +
                                          special_two_score * special_two_weight)
                        total_weight = chinese_weight + english_weight + math_weight + special_one_weight + special_two_weight
                        weighted_average = weighted_total / total_weight if total_weight > 0 else 0

                        # 使用表格顯示年度結果
                        st.markdown(f"### {year} 年度結果")
                        
                        # 創建結果表格
                        result_data = {
                            "項目": ["加權總分", "加權平均", "錄取總分", "是否達到錄取標準"],
                            "分數": [
                                f"{weighted_total:.2f} 分",
                                f"{weighted_average:.2f} 分",
                                f"{admission_score:.2f} 分",
                                "✅ 已達到" if weighted_total >= admission_score else "❌ 未達到"
                            ]
                        }
                        result_df = pd.DataFrame(result_data)
                        st.table(result_df)
                        
                        # 顯示詳細的加權計算
                        with st.expander("查看詳細加權計算", expanded=False):
                            weight_data = {
                                "科目": ["國文", "英文", "數學", "專業(一)", "專業(二)", "總計"],
                                "原始分數": [
                                    f"{chinese_score:.2f}",
                                    f"{english_score:.2f}",
                                    f"{math_score:.2f}",
                                    f"{special_one_score:.2f}",
                                    f"{special_two_score:.2f}",
                                    f"{chinese_score + english_score + math_score + special_one_score + special_two_score:.2f}"
                                ],
                                "加權值": [
                                    f"{chinese_weight:.2f}",
                                    f"{english_weight:.2f}",
                                    f"{math_weight:.2f}",
                                    f"{special_one_weight:.2f}",
                                    f"{special_two_weight:.2f}",
                                    f"{total_weight:.2f}"
                                ],
                                "加權分數": [
                                    f"{chinese_score * chinese_weight:.2f}",
                                    f"{english_score * english_weight:.2f}",
                                    f"{math_score * math_weight:.2f}",
                                    f"{special_one_score * special_one_weight:.2f}",
                                    f"{special_two_score * special_two_weight:.2f}",
                                    f"{weighted_total:.2f}"
                                ]
                            }
                            weight_df = pd.DataFrame(weight_data)
                            st.table(weight_df)
                        
                        # 顯示加權公式
                        st.info(f"加權公式：國文 × {chinese_weight} + 英文 × {english_weight} + 數學 × {math_weight} + 專業(一) × {special_one_weight} + 專業(二) × {special_two_weight}")

                        if weighted_total >= admission_score:
                            st.success(f"🎉 恭喜！您的加權總分 ({weighted_total:.2f}) 達到或超過錄取總分 ({admission_score:.2f})！")
                            prompt = f"使用者錄取了 {school_name} 的 {department_name}，請提供該學校與科系的相關資訊。"
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=500
                            )
                            st.write("### 錄取學校與科系資訊")
                            st.write(response.choices[0].message["content"])
                        else:
                            st.warning(f"⚠️ 您的加權總分 ({weighted_total:.2f}) 低於錄取總分 ({admission_score:.2f})，差 {admission_score - weighted_total:.2f} 分。")
                            similar_df = df[(df["錄取總分數"] <= weighted_total + 50) & (df["錄取總分數"] >= weighted_total - 50)].head(3)
                            if not similar_df.empty:
                                st.write("### 建議：分數相近的學校與科系")
                                for index, row in similar_df.iterrows():
                                    st.write(f"- {row['學校名稱']} - {row['系科組學程名稱']}（錄取總分：{row['錄取總分數']:.2f} 分）")
                            else:
                                st.write("目前資料中沒有分數相近的學校與科系可推薦。")
                            prompt = f"使用者的加權總分為 {weighted_total:.2f}，未達到 {school_name} 的 {department_name} 錄取總分 {admission_score:.2f}，請提供建議或鼓勵的話。"
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=500
                            )
                            st.write("### AI 建議")
                            st.write(response.choices[0].message["content"])