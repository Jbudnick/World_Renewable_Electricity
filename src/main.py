#Objects: Countries
#Functions : Plot graphs

'''
To Do:
Make separate DataFrame for energy use - only data for renewable vs non renewable
Gitignore scripts - start
Get population threshold to narrow down hypothesis test
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

def make_plots(data, subpltrows = 1, subpltcols = 1):
    fig, axes = plt.subplots(subpltrows, subpltcols, figsize=(12, 6))
    x = data.index
    y = [float(data[val]) for val in x]
    axes.scatter(x, y)
    fig.tight_layout(pad=1)
    axes.grid(True)
    fig.show()

plt.style.use('ggplot')

#Set parameters
start_year = 2000
end_year = 2017

population_cutoff = 20000000
'''
-----------------------------------------------------------------
Import electricity generation data and clean it
-----------------------------------------------------------------
'''
energy_data = pd.read_csv('data/INT-Export-04-05-2020_00-10-38.csv', header=1)
energy_data.rename(columns={'Unnamed: 1': 'Energy Type', 'API': 'Country Code'}, inplace = True)
countries = energy_data['Energy Type'][0::15]
energy_data.drop(energy_data.iloc[0::15].index, inplace=True) 
energy_data.drop('2018', axis=1, inplace=True)  # 2018 has a lot of missing data
country_code = []
for code in energy_data['Country Code']:
    if type(code) == str and code.count('-') >= 3:
        country_code.append(code.split('-')[2])
    else:
        country_code.append(code)
energy_data['Country Code'] = country_code
energy_data['Country Code'][energy_data['Country Code'] == 'WORL'] = 'WLD'

#Countries provides another dataframe to translate country codes into Country Names
country_code = energy_data['Country Code'].copy()
country_code.index -= 1
countries = pd.DataFrame(countries).join(country_code)
countries.rename(columns ={'Energy Type': 'Country'})


'''
-----------------------------------------------------------------
Import population data and clean it
-----------------------------------------------------------------
'''

pop_data = pd.read_csv('data/API_SP.POP.csv', header=4)

pop_data.drop(['Unnamed: 64', 'Indicator Name',
                      'Indicator Code', '2018', '2019'], axis=1, inplace=True)

#Removing aggregated regions to avoid double counting
regions_to_remove = (
    'Arab World', 'Caribbean small states', 'Central Europe and the Baltics', 'Early-demographic dividend', 'East Asia & Pacific', 'East Asia & Pacific (excluding high income)', 'East Asia & Pacific (IDA & IBRD countries)',
    'Europe & Central Asia (IDA & IBRD countries)', 'Euro area', 'Europe & Central Asia', 'Europe & Central Asia (excluding high income)', 'European Union', 'Fragile and conflict affected situations', 'Heavily indebted poor countries (HIPC)', 'IBRD only', 'IDA & IBRD total', 'IDA total', 'IDA blend', 'IDA only', 'Latin America & Caribbean', 'Latin America & the Caribbean (IDA & IBRD countries)', 'IDA only', 'Late-demographic dividend', 'Latin America & Caribbean (excluding high income)',
    'Least developed countries: UN classification', 'Middle East & North Africa', 'Middle East & North Africa (excluding high income)', 'Middle East & North Africa (IDA & IBRD countries)', 'North America', 'Not classified', 'OECD members', 'Other small states', 'Pacific island small states', 'Pre-demographic dividend', 'Post-demographic dividend', 'Small states', 'South Asia', 'South Asia (IDA & IBRD)','Sub-Saharan Africa (IDA & IBRD countries)', 'Sub-Saharan Africa', 'Sub-Saharan Africa (excluding high income)', 'High income', 'Low & middle income', 'Low income', 'Lower middle income', 'Middle income', 'Upper middle income')

pop_data.drop(pop_data[pop_data['Country Name'].isin(regions_to_remove)].index, inplace=True)

#Modifying index so that aggregated World row is placed on top, rest are alphabetical order, removing invalid entries

pop_data.sort_values('Country Name', inplace=True)
pop_data.fillna(0, inplace=True)
pop_data.reset_index(drop = True, inplace = True)
pop_data.index += 1
pop_data.loc[0] = pop_data.loc[215]
pop_data.drop(215, inplace = True)
pop_data.sort_index(inplace=True)
pop_data.reset_index(drop=True, inplace=True)

#pop_data[pop_data['Country Name'] == 'United States']

#Percentage of renewable electricity of whole world
percentage = energy_data.iloc[4][2:].astype(
    np.float) / energy_data.iloc[0][2:].astype(np.float)
plt.scatter(percentage.index, percentage)

#Worldwide use of renewable energy
#make_plots(energy_data.iloc[4].iloc[2:-1])

#World Population
#make_plots(population_data.sum().iloc[2:])

#if __name__ == '__main__':
#    print(energy_data)
