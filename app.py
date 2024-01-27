
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import matplotlib.pyplot as plt

# Use a pre-installed font by specifying its name
plt.rc('font', family='HYPost')  # This assumes 'Malgun Gothic' is available on your system

# Streamlit app title
st.title('Korean Annual Population')

# Set Korean font for matplotlib in Windows environment
def set_korean_font():
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# Load the data with updated caching
@st.cache_data
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

# Filtering the data
filtered_data = data[data['행정구역'] == region]

# Function to handle conversion to int, considering the possibility of non-string types
def to_int(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(int)
    else:
        return series.str.replace(',', '').fillna(0).astype(int)

# Convert year to string for comparison
year_str = str(year)

# Sort age groups with special handling for "100세 이상"
def sort_age_groups(age_group):
    if age_group == "100세 이상":
        return 100
    else:
        try:
            return int(age_group.split('~')[0].replace('세', ''))
        except ValueError:
            return 0

# Extract and sort age groups from the column names
age_groups = [col.split('_')[-1] for col in filtered_data.columns if '세' in col and year_str in col]
age_groups = sorted(set(age_groups), key=sort_age_groups)

# Convert to integers and remove the total population column
male_data = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(f'{year}년_남_') and '총인구수' not in col]].iloc[0])
female_data = to_int(filtered_data[[col for col in filtered_data.columns if col.startswith(f'{year}년_여_') and '총인구수' not in col]].iloc[0])

# Calculate total population for the legend and format it
total_male_population = "{:,}명".format(male_data.sum())
total_female_population = "{:,}명".format(female_data.sum())

# Plotting bar chart
fig, ax = plt.subplots()

ax.barh(age_groups, -male_data.values, color='blue', label=f'Male: {total_male_population}')
ax.barh(age_groups, female_data.values, color='red', label=f'Female: {total_female_population}')

ax.set_xlabel('Population')
ax.set_title(f'{region} Year{year} M(Blue) & F(Red) Distribution')
plt.legend()
ax.axvline(x=0, color='grey', linewidth=0.8)
st.pyplot(fig)







