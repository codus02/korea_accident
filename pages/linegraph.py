#######################
# 라이브러리 불러오기
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

#######################
# 페이지 설정
st.set_page_config(
    page_title="대한민국 교통사고 추이 대시보드",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################

# 데이터 불러오기
file_path="음주운전교통사고비율_시도_시_군_구__20241204193205.csv"
df = pd.read_csv(file_path,  encoding='UTF-8')

korea_geojson = json.load(open('SIDO_MAP_2022_geoJSON.json', encoding="UTF-8")) # json 파일 불러오기



#######################
#######################
# 데이터 전처리
def preprocess_data(data):
    data.rename(columns={'행정구역별(1)': '행정구역'}, inplace=True)
    data = data[data['행정구역'] != '전국']
    data = data.iloc[1:].reset_index(drop=True)
    data['행정구역'] = data['행정구역'].replace({
        '강원특별자치도': '강원도', 
        '전북특별자치도': '전라북도'
    })
    return data

df = preprocess_data(df)

# GeoJSON CTPRVN_CD 값과 데이터프레임 행정구역 매핑
region_mapping = {
    '서울특별시': '11',
    '부산광역시': '26',
    '대구광역시': '27',
    '인천광역시': '28',
    '광주광역시': '29',
    '대전광역시': '30',
    '울산광역시': '31',
    '세종특별자치시': '36',
    '경기도': '41',
    '강원도': '42',
    '충청북도': '43',
    '충청남도': '44',
    '전라북도': '45',
    '전라남도': '46',
    '경상북도': '47',
    '경상남도': '48',
    '제주특별자치도': '50'
}

# 행정구역 열을 CTPRVN_CD와 매핑
df['code'] = df['행정구역'].map(region_mapping)


# 열 이름 변환
def rename_columns(columns):
    new_columns = []
    for col in columns:
        if col.endswith('.1'):
            new_columns.append(f"{col.split('.')[0]}_음주사고수")
        elif col.endswith('.2'):
            new_columns.append(f"{col.split('.')[0]}_교통사고수")
        elif col.isdigit():
            new_columns.append(f"{col}_음주사고비율")
        else:
            new_columns.append(col)
    return new_columns

df.columns = rename_columns(df.columns)

# 데이터 변환
df = df.melt(
    id_vars=['행정구역','code'],
    var_name='prop',
    value_name='accident'
)

if 'prop' in df.columns:
    df[['year', 'category']] = df['prop'].str.split('_', expand=True)

df.drop('prop', axis=1, inplace=True)
df['year'] = df['year'].astype(int)
df['accident'] = pd.to_numeric(df['accident'], errors='coerce')
df = df.dropna(subset=['accident'])





#######################
# 행정구역 및 카테고리 선택
st.markdown('#### 선택한 행정구역의 연도별 추이')

# 행정구역 선택 박스
region_list = df['행정구역'].unique()  # 유일한 행정구역 리스트
selected_region = st.selectbox('행정구역 선택', region_list, key='region_selectbox')

# 카테고리 선택 (라디오 버튼)
category_list = list(df['category'].unique())  # 카테고리 리스트
selected_category = st.radio(
    "카테고리 선택", 
    category_list, 
    index=0,  # 기본 선택 (첫 번째 항목)
    key="category_radio"
)

# 선택한 행정구역의 데이터 필터링
df_selected_region = df.query('행정구역 == @selected_region & category == @selected_category')

if not df_selected_region.empty:
    # 꺾은선 그래프 생성
    line_chart = alt.Chart(df_selected_region).mark_line().encode(
        x=alt.X('year:O', axis=alt.Axis(title='연도', titleFontSize=14, labelFontSize=12)),
        y=alt.Y('accident:Q', axis=alt.Axis(title=selected_category, titleFontSize=14, labelFontSize=12)),
        color=alt.value('#29b5e8')  # 선 색깔
    ).properties(
        width=700,
        height=400
    )

    # 꺾은선 그래프 출력
    st.altair_chart(line_chart, use_container_width=True)
else:
    # 데이터가 없는 경우 메시지 출력
    st.info("선택한 행정구역의 데이터가 없습니다.")
