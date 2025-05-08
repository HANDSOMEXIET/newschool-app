import streamlit as st
import pandas as pd

# 設定頁面配置
st.set_page_config(
    page_title="成績分析系統",
    page_icon="📊",
    layout="wide"
)

# 自訂 CSS 樣式
st.markdown("""
    <style>
    /* 主要背景和字體 */
    .main {
        background-color: #f8f9fa;
        font-family: 'Microsoft JhengHei', sans-serif;
    }
    
    /* 標題樣式 */
    h1 {
        color: #2C3E50;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    h2 {
        color: #2C3E50;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #2C3E50;
        font-size: 1.4rem;
        margin-top: 1.2rem;
    }
    
    /* 按鈕樣式 */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 輸入框樣式 */
    .stNumberInput input {
        border-radius: 5px;
        border: 1px solid #ddd;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stNumberInput input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 5px rgba(76,175,80,0.3);
    }
    
    /* 下拉選單樣式 */
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    /* 表格樣式 */
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .dataframe th {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
    }
    
    .dataframe td {
        padding: 0.5rem;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    .dataframe tr:hover {
        background-color: #e8f5e9;
    }
    
    /* 卡片樣式 */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 成功/警告訊息樣式 */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* 分隔線樣式 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #4CAF50, #2196F3);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# 頁面標題
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1>📊 成績分析系統</h1>
        <p style='color: #666; font-size: 1.2rem;'>詳細分析您的成績，找出最適合的學校與科系</p>
    </div>
""", unsafe_allow_html=True)

# 讀取資料
try:
    df_113 = pd.read_excel("11309a (1).xlsx", sheet_name="Sheet1")
    df_113['錄取總分數(沒加權)'] = pd.to_numeric(df_113['錄取總分數(沒加權)'], errors='coerce')
    df_113['平均'] = pd.to_numeric(df_113['平均'], errors='coerce')
    
    # 讀取 112 學年資料
    df_112 = pd.read_excel("11209.xlsx", sheet_name="工作表1")
    df_112['平均'] = pd.to_numeric(df_112['平均'], errors='coerce')
    
    # 合併 112 和 113 的資料
    df_merged = pd.merge(df_113, df_112[['學校名稱', '系科組學程名稱', '平均']], 
                        on=['學校名稱', '系科組學程名稱'], 
                        how='left', 
                        suffixes=('', '_112'))
    
    st.sidebar.success("✅ 成功載入 112 和 113 學年度資料")
except Exception as e:
    st.sidebar.error(f"❌ 無法載入資料: {str(e)}")
    df_113 = pd.DataFrame()

# 初始化 session state
if 'show_scores' not in st.session_state:
    st.session_state.show_scores = False
if 'school_type' not in st.session_state:
    st.session_state.school_type = "全部"
if 'similar_school' not in st.session_state:
    st.session_state.similar_school = None
if 'similar_dept' not in st.session_state:
    st.session_state.similar_dept = None

# 成績輸入區塊
with st.container():
    st.markdown("### 📝 請輸入您的成績")
    st.markdown("所有科目成績範圍為 0-100 分")
    
    # 使用卡片式佈局
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # 使用兩列佈局來排列輸入框
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 主要科目")
            chinese_score = st.number_input("國文成績", min_value=0, max_value=100, step=1, value=0, key="chinese")
            english_score = st.number_input("英文成績", min_value=0, max_value=100, step=1, value=0, key="english")
            math_score = st.number_input("數學成績", min_value=0, max_value=100, step=1, value=0, key="math")
        
        with col2:
            st.markdown("#### 專業科目")
            special_one_score = st.number_input("專業(一)成績", min_value=0, max_value=100, step=1, value=0, key="special1")
            special_two_score = st.number_input("專業(二)成績", min_value=0, max_value=100, step=1, value=0, key="special2")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 計算總分
    total_score = chinese_score + english_score + math_score + special_one_score + special_two_score
    average_score = total_score / 5
    
    # 顯示已輸入的成績
    if st.button("🔍 計算成績並尋找相近學校", key="show_scores_button"):
        st.session_state.show_scores = True
        st.session_state.school_type = "全部"
        st.session_state.similar_school = None
        st.session_state.similar_dept = None

# 如果已經點擊了計算按鈕，顯示結果
if st.session_state.show_scores:
    st.markdown("### 📊 您輸入的成績")
    
    # 使用卡片顯示成績
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 主要科目")
            st.write(f"- 國文: {chinese_score} 分")
            st.write(f"- 英文: {english_score} 分")
            st.write(f"- 數學: {math_score} 分")
        
        with col2:
            st.markdown("#### 專業科目")
            st.write(f"- 專業(一): {special_one_score} 分")
            st.write(f"- 專業(二): {special_two_score} 分")
        
        with col3:
            st.markdown("#### 總分統計")
            st.success(f"總分: {total_score:.2f} 分")
            st.info(f"平均分數: {average_score:.2f} 分")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 尋找相近的學校及科系
    if not df_merged.empty:
        # 設定分數範圍（上下浮動 20 分）
        score_range = 5
        similar_df = df_merged[
            (df_merged["平均"] <= (total_score/5) + score_range) & 
            (df_merged["平均"] >= (total_score/5) - score_range)
        ].sort_values("平均")
        
        if not similar_df.empty:
            st.markdown("### 🎯 分數相近的學校及科系")
            st.write(f"找到 {len(similar_df)} 個與您的平均分數 ({total_score/5:.2f}) 相近的學校及科系（上下浮動 {score_range} 分）")
            
            # 顯示使用者的平均分數
            st.markdown(f"**您的平均分數**: {total_score/5:.2f} 分")
            
            # 顯示所有相近的學校和科系的表格
            st.markdown("#### 📋 所有分數相近的學校與科系")
            
            # 準備表格數據
            table_data = []
            for index, row in similar_df.iterrows():
                school_type = "公立" if row['學校名稱'].startswith("國立") else "私立"
                # 計算加權總分
                weighted_total = (chinese_score * row['國文加權'] +
                                english_score * row[' 英文加權'] +
                                math_score * row[' 數學加權'] +
                                special_one_score * row[' 專業(一)加權'] +
                                special_two_score * row[' 專業(二)加權'])
                
                # 計算加權總和
                total_weight = (row['國文加權'] + row[' 英文加權'] + row[' 數學加權'] + 
                              row[' 專業(一)加權'] + row[' 專業(二)加權'])
                
                # 計算加權平均
                weighted_average = weighted_total / total_weight

                # 計算分數差距
                diff_113 = weighted_average - row['平均']
                diff_112 = row['平均_112'] - (total_score/5) if pd.notna(row['平均_112']) else None
                
                # 計算分數差距的符號
                diff_symbol_113 = "↑" if diff_113 > 0 else "↓" if diff_113 < 0 else "="
                diff_symbol_112 = "↑" if diff_112 and diff_112 < 0 else "↓" if diff_112 and diff_112 > 0 else "=" if diff_112 is not None else "N/A"

                # 格式化加權乘數
                weight_multipliers = f"國文×{row['國文加權']} 英文×{row[' 英文加權']} 數學×{row[' 數學加權']} 專一×{row[' 專業(一)加權']} 專二×{row[' 專業(二)加權']}"

                table_data.append({
                    "學校類型": school_type,
                    "學校名稱": row['學校名稱'],
                    "科系名稱": row['系科組學程名稱'],
                    "加權乘數": weight_multipliers,
                    "113年平均": f"{row['平均']:.2f} ({diff_symbol_113} {abs(diff_113):.2f})",
                    "加權平均": f"{weighted_average:.2f}",
                    "112年平均": f"{row['平均_112']:.2f} ({diff_symbol_112} {abs(diff_112):.2f})" if pd.notna(row['平均_112']) else "N/A",
                })
            
            # 顯示表格
            table_df = pd.DataFrame(table_data)
            # 根據113年平均分數排序
            table_df = table_df.sort_values(by="113年平均", ascending=False)
            table_df = table_df.style.set_properties(**{
                'text-align': 'center',
                'font-size': '14px'
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]},
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]}
            ])
            
            st.dataframe(table_df, use_container_width=True)
            
            # 找出分數最低的科目
            scores = {
                '國文': chinese_score,
                '英文': english_score,
                '數學': math_score,
                '專業(一)': special_one_score,
                '專業(二)': special_two_score
            }
            lowest_subject = min(scores.items(), key=lambda x: x[1])
            
            st.markdown(f"#### 📊 分數分析")
            st.markdown(f"您的{lowest_subject[0]}分數最低，為 {lowest_subject[1]} 分")

            # 找出該科目加權最低的校系
            lowest_weight_schools = []
            for index, row in similar_df.iterrows():
                if lowest_subject[0] == '國文':
                    weight = row['國文加權']
                elif lowest_subject[0] == '英文':
                    weight = row[' 英文加權']
                elif lowest_subject[0] == '數學':
                    weight = row[' 數學加權']
                elif lowest_subject[0] == '專業(一)':
                    weight = row[' 專業(一)加權']
                else:  # 專業(二)
                    weight = row[' 專業(二)加權']
                
                lowest_weight_schools.append({
                    '學校名稱': row['學校名稱'],
                    '科系名稱': row['系科組學程名稱'],
                    '加權': weight
                })

            # 找出加權最低的校系
            lowest_weight = min(lowest_weight_schools, key=lambda x: x['加權'])['加權']
            lowest_weight_schools = [school for school in lowest_weight_schools if school['加權'] == lowest_weight]
            
            st.markdown(f"#### 🎯 建議校系")
            st.markdown(f"根據您的{lowest_subject[0]}分數最低，建議您考慮以下校系（{lowest_subject[0]}加權均為 {lowest_weight}）：")
            
            # 建立表格顯示所有建議校系
            suggested_schools_data = []
            for school in lowest_weight_schools:
                # 找到對應的原始資料行
                original_row = similar_df[
                    (similar_df['學校名稱'] == school['學校名稱']) & 
                    (similar_df['系科組學程名稱'] == school['科系名稱'])
                ].iloc[0]
                
                # 計算加權總分
                weighted_total = (chinese_score * original_row['國文加權'] +
                                english_score * original_row[' 英文加權'] +
                                math_score * original_row[' 數學加權'] +
                                special_one_score * original_row[' 專業(一)加權'] +
                                special_two_score * original_row[' 專業(二)加權'])
                
                # 計算加權總和
                total_weight = (original_row['國文加權'] + original_row[' 英文加權'] + 
                              original_row[' 數學加權'] + original_row[' 專業(一)加權'] + 
                              original_row[' 專業(二)加權'])
                
                # 計算加權平均
                weighted_average = weighted_total / total_weight

                # 計算分數差距
                diff_113 = weighted_average - original_row['平均']
                diff_112 = original_row['平均_112'] - (total_score/5) if pd.notna(original_row['平均_112']) else None
                
                # 計算分數差距的符號
                diff_symbol_113 = "↑" if diff_113 > 0 else "↓" if diff_113 < 0 else "="
                diff_symbol_112 = "↑" if diff_112 and diff_112 < 0 else "↓" if diff_112 and diff_112 > 0 else "=" if diff_112 is not None else "N/A"

                # 格式化加權乘數
                weight_multipliers = f"國文×{original_row['國文加權']} 英文×{original_row[' 英文加權']} 數學×{original_row[' 數學加權']} 專一×{original_row[' 專業(一)加權']} 專二×{original_row[' 專業(二)加權']}"

                suggested_schools_data.append({
                    "學校類型": "公立" if original_row['學校名稱'].startswith("國立") else "私立",
                    "學校名稱": school['學校名稱'],
                    "科系名稱": school['科系名稱'],
                    "加權乘數": weight_multipliers,
                    "113年平均": f"{original_row['平均']:.2f} ({diff_symbol_113} {abs(diff_113):.2f})",
                    "加權平均": f"{weighted_average:.2f}",
                    "112年平均": f"{original_row['平均_112']:.2f} ({diff_symbol_112} {abs(diff_112):.2f})" if pd.notna(original_row['平均_112']) else "N/A"
                })
            
            suggested_schools_df = pd.DataFrame(suggested_schools_data)
            # 根據113年平均分數排序
            suggested_schools_df = suggested_schools_df.sort_values(by="113年平均", ascending=False)
            suggested_schools_df = suggested_schools_df.style.set_properties(**{
                'text-align': 'center',
                'font-size': '14px'
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]},
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]}
            ])
            
            st.dataframe(suggested_schools_df, use_container_width=True)
            
            # 顯示未被選中的校系
            non_recommended_schools = similar_df[~similar_df.apply(
                lambda row: (row['學校名稱'], row['系科組學程名稱']) in 
                [(school['學校名稱'], school['科系名稱']) for school in lowest_weight_schools], 
                axis=1
            )]
            
            if not non_recommended_schools.empty:
                st.markdown("#### ❌ 其他相近校系（不建議）")
                st.markdown("以下校系雖然分數相近，但對您分數最低的科目加權較高：")
                
                non_recommended_data = []
                for _, row in non_recommended_schools.iterrows():
                    # 計算加權總分
                    weighted_total = (chinese_score * row['國文加權'] +
                                    english_score * row[' 英文加權'] +
                                    math_score * row[' 數學加權'] +
                                    special_one_score * row[' 專業(一)加權'] +
                                    special_two_score * row[' 專業(二)加權'])
                    
                    # 計算加權總和
                    total_weight = (row['國文加權'] + row[' 英文加權'] + row[' 數學加權'] + 
                                  row[' 專業(一)加權'] + row[' 專業(二)加權'])
                    
                    # 計算加權平均
                    weighted_average = weighted_total / total_weight

                    # 計算分數差距
                    diff_113 = weighted_average - row['平均']
                    diff_112 = row['平均_112'] - (total_score/5) if pd.notna(row['平均_112']) else None
                    
                    # 計算分數差距的符號
                    diff_symbol_113 = "↑" if diff_113 > 0 else "↓" if diff_113 < 0 else "="
                    diff_symbol_112 = "↑" if diff_112 and diff_112 < 0 else "↓" if diff_112 and diff_112 > 0 else "=" if diff_112 is not None else "N/A"

                    # 格式化加權乘數
                    weight_multipliers = f"國文×{row['國文加權']} 英文×{row[' 英文加權']} 數學×{row[' 數學加權']} 專一×{row[' 專業(一)加權']} 專二×{row[' 專業(二)加權']}"

                    non_recommended_data.append({
                        "學校類型": "公立" if row['學校名稱'].startswith("國立") else "私立",
                        "學校名稱": row['學校名稱'],
                        "科系名稱": row['系科組學程名稱'],
                        "加權乘數": weight_multipliers,
                        "113年平均": f"{row['平均']:.2f} ({diff_symbol_113} {abs(diff_113):.2f})",
                        "加權平均": f"{weighted_average:.2f}",
                        "112年平均": f"{row['平均_112']:.2f} ({diff_symbol_112} {abs(diff_112):.2f})" if pd.notna(row['平均_112']) else "N/A"
                    })
                
                non_recommended_df = pd.DataFrame(non_recommended_data)
                # 根據113年平均分數排序
                non_recommended_df = non_recommended_df.sort_values(by="113年平均", ascending=False)
                non_recommended_df = non_recommended_df.style.set_properties(**{
                    'text-align': 'center',
                    'font-size': '14px',
                    'color': '#666666'  # 使用較淡的顏色
                }).set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#666666'), ('color', 'white')]},
                    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]}
                ])
                
                st.dataframe(non_recommended_df, use_container_width=True)
            
            # 添加學校類型選擇
            st.markdown("#### 🏫 依學校類型篩選")
            school_type = st.radio("學校類型：", ["全部", "公立", "私立"], 
                                 horizontal=True, 
                                 key="school_type_radio",
                                 index=["全部", "公立", "私立"].index(st.session_state.school_type))
            
            # 更新 session state
            st.session_state.school_type = school_type
            
            # 根據學校類型篩選學校
            if school_type == "公立":
                filtered_schools = [school for school in similar_df["學校名稱"].unique() if school.startswith("國立")]
                similar_df = similar_df[similar_df["學校名稱"].isin(filtered_schools)]
            elif school_type == "私立":
                filtered_schools = [school for school in similar_df["學校名稱"].unique() if not school.startswith("國立")]
                similar_df = similar_df[similar_df["學校名稱"].isin(filtered_schools)]
            
            # 添加學校和科系選擇
            st.markdown("#### 🎓 選擇特定學校與科系")
            col1, col2 = st.columns(2)
            with col1:
                # 從表格中獲取學校列表
                available_schools = similar_df["學校名稱"].unique()
                similar_school = st.selectbox("選擇學校", 
                                            available_schools, 
                                            key="similar_school_select",
                                            index=0 if st.session_state.similar_school is None else 
                                                  list(available_schools).index(st.session_state.similar_school))
            
            # 更新 session state
            st.session_state.similar_school = similar_school
            
            with col2:
                # 根據選中的學校篩選科系
                filtered_dept = similar_df[similar_df["學校名稱"] == similar_school]
                available_depts = filtered_dept["系科組學程名稱"].unique()
                
                # 如果之前選擇的科系不在當前學校的科系列表中，重置為第一個選項
                if st.session_state.similar_dept not in available_depts:
                    st.session_state.similar_dept = available_depts[0] if len(available_depts) > 0 else None
                
                similar_dept = st.selectbox("選擇科系", 
                                          available_depts, 
                                          key="similar_dept_select",
                                          index=0 if st.session_state.similar_dept is None else 
                                                list(available_depts).index(st.session_state.similar_dept))
            
            # 更新 session state
            st.session_state.similar_dept = similar_dept
            
            # 顯示選中的學校和科系的詳細資訊
            selected_row = similar_df[(similar_df["學校名稱"] == similar_school) & 
                                    (similar_df["系科組學程名稱"] == similar_dept)].iloc[0]
            
            st.markdown("#### 📌 選中的學校與科系資訊")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"**學校名稱**: {selected_row['學校名稱']}")
                st.write(f"**科系名稱**: {selected_row['系科組學程名稱']}")
                st.write(f"**平均分數**: {selected_row['平均']:.2f} 分")
                st.write(f"**加權公式**: 國文 × {selected_row['國文加權']} + 英文 × {selected_row[' 英文加權']} + 數學 × {selected_row[' 數學加權']} + 專業(一) × {selected_row[' 專業(一)加權']} + 專業(二) × {selected_row[' 專業(二)加權']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 計算使用該學校加權的成績
            selected_chinese_weight = selected_row['國文加權']
            selected_english_weight = selected_row[' 英文加權']
            selected_math_weight = selected_row[' 數學加權']
            selected_special_one_weight = selected_row[' 專業(一)加權']
            selected_special_two_weight = selected_row[' 專業(二)加權']
            
            selected_weighted_total = (chinese_score * selected_chinese_weight +
                                      english_score * selected_english_weight +
                                      math_score * selected_math_weight +
                                      special_one_score * selected_special_one_weight +
                                      special_two_score * selected_special_two_weight)
            
            st.markdown("#### 📊 使用該學校加權的成績計算")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"**加權總分**: {selected_weighted_total:.2f} 分")
                st.write(f"**平均分數**: {selected_row['平均']:.2f} 分")
                
                if selected_weighted_total >= selected_row['錄取總分數(沒加權)']:
                    st.success(f"✅ 您的加權總分 ({selected_weighted_total:.2f}) 達到或超過錄取總分 ({selected_row['錄取總分數(沒加權)']:.2f})！")
                else:
                    st.warning(f"❌ 您的加權總分 ({selected_weighted_total:.2f}) 低於錄取總分 ({selected_row['錄取總分數(沒加權)']:.2f})，差 {selected_row['錄取總分數(沒加權)'] - selected_weighted_total:.2f} 分。")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"沒有找到與您的平均分數 ({total_score/5:.2f}) 相近的學校及科系（上下浮動 {score_range} 分）")
            
            # 提供建議
            st.markdown("### 💡 建議")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if total_score/5 > df_merged["平均"].max():
                    st.success("您的分數很高！您可以考慮申請更高分的學校及科系。")
                elif total_score/5 < df_merged["平均"].min():
                    st.warning("您的分數較低，建議您考慮以下選項：")
                    st.write("1. 提高您的成績")
                    st.write("2. 考慮其他入學管道")
                    st.write("3. 尋找錄取分數較低的學校及科系")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 顯示分數範圍
            st.markdown("### 📈 分數範圍參考")
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"最低平均分數: {df_merged['平均'].min():.2f} 分")
                st.write(f"最高平均分數: {df_merged['平均'].max():.2f} 分")
                st.write(f"平均分數: {df_merged['平均'].mean():.2f} 分")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("無法載入學校資料，請確認 11309a (1).xlsx 檔案是否存在且格式正確。") 