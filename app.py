import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import seaborn as sns 
import numpy as np 


# # 폰트 적용
# import matplotlib.font_manager as fm
# import os

# fpath = os.path.join(os.getcwd(), "streamlit-korean-fonts/NanumGothic-Bold.ttf")
# prop = fm.FontProperties(fname=fpath)

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 현재 파일의 위치를 기준으로 폰트 파일의 상대 경로 설정
font_path = os.path.join(os.getcwd(), 'streamlit-korean-fonts', 'NanumGothic-Bold.ttf')

# 폰트 이름 가져오기
font_name = font_manager.FontProperties(fname=font_path).get_name()

# matplotlib의 rcParams에 폰트 설정
rc('font', family=font_name)


# Streamlit app title
st.title('Korean Annual Population')

# Displaying the source attribution
st.markdown('Source: [Statistics Korea](https://jumin.mois.go.kr/ageStatMonth.do)')

# Load the data with updated caching
@st.cache
def load_data():
    data = pd.read_csv('200812_202312_Korean_Annual_Population.csv', encoding='euc-kr')
    return data

data = load_data()

# Extract years from column names using a regular expression
years_pattern = re.compile(r'(\d{4})년')
years = sorted(set(int(years_pattern.search(col).group(1))
                   for col in data.columns if years_pattern.search(col)), reverse=True)
default_year = years[0]  # Default to the most recent year

# Filters on the same line
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox('Select Year', years, index=0)  # Placed in the first column
with col2:
    region = st.selectbox('Select Region', data['행정구역'].unique())  # Placed in the second column

# Filtering the data for selected region
filtered_data = data[data['행정구역'] == region]

# Function to handle conversion to int for a Series, correctly handling strings with commas
def to_int(data):
    if isinstance(data, pd.Series):  # If data is a Series
        if data.dtype == object:  # Check if the Series contains strings
            return data.str.replace(',', '').fillna(0).astype(int)
        else:  # If not object type (string), directly convert
            return data.fillna(0).astype(int)
    elif isinstance(data, pd.DataFrame):  # If data is a DataFrame
        for col in data:  # Iterate through each column in the DataFrame
            if data[col].dtype == object:  # Check if the column contains strings
                data[col] = data[col].str.replace(',', '').fillna(0).astype(int)
            else:  # Directly convert if not string
                data[col] = data[col].fillna(0).astype(int)
        return data

# Applying to_int to each relevant column individually
for col in [col for col in filtered_data.columns if col.startswith(f'{year}년_남_') and '총인구수' not in col]:
    filtered_data[col] = to_int(filtered_data[col])

# Sort age groups with special handling for "100세 이상"
def sort_age_groups(age_group):
    if age_group == "100세 이상":
        return 100
    else:
        try:
            return int(age_group.split('~')[0].replace('세', ''))
        except ValueError:
            return 0

# Extract and sort age groups from the column names for the selected year
age_groups = [col.split('_')[-1] for col in filtered_data.columns if '세' in col and str(year) in col]
age_groups = sorted(set(age_groups), key=sort_age_groups)

# Convert to integers and remove the total population column
male_data = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(f'{year}년_남_') and '총인구수' not in col]].iloc[0])
female_data = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(f'{year}년_여_') and '총인구수' not in col]].iloc[0])

# Plotting the age distribution chart for the selected year and region
fig, ax = plt.subplots()
ax.barh(age_groups, -male_data.values, color='blue', label=f'Male: {male_data.sum():,}명')
ax.barh(age_groups, female_data.values, color='red', label=f'Female: {female_data.sum():,}명')
ax.set_xlabel('Population')
ax.set_title(f'{region} {year} M(Blue) & F(Red) Distribution')
plt.legend()
ax.axvline(x=0, color='grey', linewidth=0.8)
st.pyplot(fig)

# Additional: Plotting the total population change over years for the selected region
total_male_population_by_year = []
total_female_population_by_year = []

for year in years:
    year_str = f'{year}년'
    male_sum = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(year_str + '_남_총인구수')]]).sum().sum()
    female_sum = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(year_str + '_여_총인구수')]]).sum().sum()
    total_male_population_by_year.append(male_sum)
    total_female_population_by_year.append(female_sum)

# Plotting total population change over years
fig2, ax2 = plt.subplots()
ax2.plot(years, total_male_population_by_year, label='Male', color='blue')
ax2.plot(years, total_female_population_by_year, label='Female', color='red')
ax2.set_xlabel('Year')
ax2.set_ylabel('Total Population')
ax2.set_title(f'Total Population Change in {region} Over Years')
ax2.legend()
st.pyplot(fig2)







