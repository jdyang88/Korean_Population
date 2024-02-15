# 남성과 여성 인구의 총합 계산
total_population = male_data.sum() + female_data.sum()

# Plotting the age distribution chart for the selected year and region with total population in legend
fig, ax = plt.subplots()
ax.barh(age_groups, -male_data.values, color='blue', label=f'Male: {male_data.sum():,}명')
ax.barh(age_groups, female_data.values, color='red', label=f'Female: {female_data.sum():,}명')
ax.set_xlabel('Population')
ax.set_title(f'{region} {year} M(Blue) & F(Red) Distribution')

# 총 인구수를 범례에 추가
ax.legend(title=f'Total: {total_population:,}명')

ax.axvline(x=0, color='grey', linewidth=0.8)
st.pyplot(fig)







