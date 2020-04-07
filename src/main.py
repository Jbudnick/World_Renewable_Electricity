#Objects: Countries
#Functions : Plot graphs

'''
To get year columns mapped as int:
    dtype in read csv, import dictionary with column names

Bring in list of developed vs developing countries
color code 

To Do ++ :
Left Justify Energy Type column
Tuesday:
Finish Hypo Test
plots

Wednesday
MVP+ Stuff

Thursday:
Clean Code, Work on readme

To Do:
Make separate DataFrame for energy use - only data for renewable vs non renewable, add to highest population table
hypo test
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

""" 
class analysis(object):
    def __init__(self, title, data_x, data_ylist):
        self.title = title
        self.data_x = data_x
        self.data_ylist = data_ylist

    def plot_data() 
    
"""


#The original energy data is formatted with leading spaces to identify subgroups of each type. This function iterates through and replaces these using numerical indexing for readbility in DataFrames.

#Assumptions - "--" or NaN means that no data is available for the time period. These will be replaced with 0. 
def indent_replace(a_series):
    new_series = []
    for string in a_series:
        no_indent = string.lstrip()
        space_count = len(string) - len(no_indent)
        if space_count == 4:
            type1, type2 = 0, 0
            new_series.append(no_indent)
        elif space_count == 8:
            type1 += 1
            new_series.append('{}'.format(type1) + '.' + no_indent)
        elif space_count >= 12:
            type2 += 1
            new_series.append('{}'.format(type1) + '.' + '{}'.format(type2) + '.' + no_indent)
        else:
            print('error, ommitted {}'.format(string))
    return new_series

def col_to_num(df, col1, col2 = None):
    for col in df.iloc[:, col1:col2]:
        pd.to_numeric(df[col])
    return df

# import functools
# def left_justify(df, col):
#     formatters= {}
#     max_val = df[col].str.len().max()
#     form = '{{:<{}s}}'.format(max_val)
#     formatters[col] = functools.partial(str.format, form)
#     return df.to_string(formatters = formatters, index = False)

def make_plots(data, subpltrows = 1, subpltcols = 1):
    fig, axes = plt.subplots(subpltrows, subpltcols, figsize=(14, 6))
    x = data.index
    y = [float(data[val]) for val in x]
    axes.scatter(x, y)
    fig.tight_layout(pad = 3)
    axes.grid(True)
    return fig, axes

plt.style.use('ggplot')

#Set parameters
start_year = '1980'
end_year = '2017'
years_to_int = {str(year): int(year) for year in range(
    int(start_year), int(end_year) + 1)}

#This number sets the number of countries to analyze per top in each category.
countries_to_analyze = 20 + 1



'''
-----------------------------------------------------------------
Import electricity generation data and clean it
-----------------------------------------------------------------
'''
energy_data = pd.read_csv('data/INT-Export-04-05-2020_00-10-38.csv', header=1)
energy_data.rename(columns={'Unnamed: 1': 'Energy Type', 'API': 'Country Code'}, inplace = True)
# 2018 has a lot of missing data
energy_data.drop('2018', axis=1, inplace=True)

#Original dataset has several rows that are totals of other forms of energy. This section drops the rows of totals so that only renewable energy has subgroups. Several countries are missing a country code and these are specified manually.
energy_data['Country Code'].loc[1981:1994] = 'Micronesia'
energy_data['Country Code'].loc[2297:2309] = 'MNP'
energy_data['Country Code'].loc[3181:3194] = 'Tuvalu'
energy_data['Country Code'].loc[3211:3224] = 'U.S. Territories'
countries = energy_data['Energy Type'][0::15]
energy_data.drop(energy_data.loc[0::15].index, inplace=True)
energy_data.drop(energy_data.loc[6::14].index, inplace=True)
energy_data.drop(energy_data.loc[8::13].index, inplace=True)
energy_data.drop(energy_data.loc[9::12].index, inplace=True)
energy_data.reset_index(drop = True, inplace = True)

energy_data.drop(
    energy_data[energy_data['Country Code'] == 'none'].index, inplace=True)

country_code = []
for code in energy_data['Country Code']:
    if code != 'none' and type(code) == str and code.count('-') >= 3:
        country_code.append(code.split('-')[2])
    else:
        country_code.append(code)

energy_data['Country Code'] = country_code
energy_data['Country Code'][energy_data['Country Code'] == 'WORL'] = 'WLD'
energy_data['Energy Type'] = indent_replace(energy_data['Energy Type'])
energy_data.fillna(0, inplace=True)
energy_data.replace('--', 0, inplace = True)
energy_data.iloc[:, 2:] = energy_data.iloc[:, 2:].astype('float')

#Countries provides another dataframe to translate country codes into Country Names
countries.reset_index(drop=True, inplace=True)
country_code = energy_data['Country Code'].copy()
country_code.drop_duplicates(inplace=True)
country_code.reset_index(drop = True, inplace = True)
countries = pd.DataFrame(country_code).join(countries)
countries.rename(columns ={'Energy Type': 'Country'}, inplace = True)
energy_data.merge(countries)

#Replace Country codes with country names
energy_data = energy_data.iloc[:, :1].merge(countries).join(energy_data.iloc[:, 1:])
energy_data.drop('Country Code', axis=1, inplace = True)
'''
-----------------------------------------------------------------
Import UN HDI data
-----------------------------------------------------------------
'''
HDI_data = pd.read_csv('data/HDI.csv', nrows=190)
HDI_data.drop(0, inplace = True)
HDI_data['Country'] = HDI_data['Country'].str.lstrip()
HDI_data.drop([HDI_data.columns[x] for x in range(
    3, len(HDI_data.columns), 2)], axis=1, inplace=True)
developed = HDI_data.sort_values('2017', ascending=False)['Country'][:20].reset_index(drop = True)
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
    'Arab World', 'Caribbean small states', 'Central Europe and the Baltics', 'Early-demographic dividend', 'East Asia & Pacific', 'East Asia & Pacific (excluding high income)', 'East Asia & Pacific (IDA & IBRD countries)','Europe & Central Asia (IDA & IBRD countries)', 'Euro area', 'Europe & Central Asia', 'Europe & Central Asia (excluding high income)', 'European Union', 'Fragile and conflict affected situations', 'Heavily indebted poor countries (HIPC)', 'IBRD only', 'IDA & IBRD total', 'IDA total', 'IDA blend', 'IDA only', 'Latin America & Caribbean', 'Latin America & the Caribbean (IDA & IBRD countries)', 'IDA only', 'Late-demographic dividend', 'Latin America & Caribbean (excluding high income)',
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
'''
--------------------------------------------
Highest population dataset determined here
--------------------------------------------
'''
high_pop = pop_data.sort_values('1980',ascending = False).copy()[1: countries_to_analyze]

#Percentage of renewable electricity of whole world
percentage = energy_data.iloc[4][2:].astype(
    np.float) / energy_data.iloc[0][2:].astype(np.float)
plt.scatter(percentage.index, percentage)

#Worldwide use of renewable energy
show_plot = 'F'
if show_plot == 'T':
    world_fig, world_axes = make_plots(energy_data.iloc[4].iloc[2:])
    world_axes.set_xlabel('Year')
    world_axes.xaxis.set_ticks(np.arange(0,int(end_year)-int(start_year), 2))
    world_axes.set_xlim(-1, 38)
    world_axes.set_ylabel('Billion Kwh produced')
    world_axes.set_title('Worldwide Renewable Electricity Production')
    world_fig.show()

#World Population
make_plots(pop_data.sum().iloc[2:])


# Plot of top 20 most developed countries renewable energies
developed = pd.DataFrame(developed).merge(energy_data)
fig, ax = plt.subplots(1,1, figsize = (12,6))

# Norway_reuse = developed_energy.
# ax.plot(developed_energy.columns, )

#lt.plot(developed_energy.iloc[3, 1:].index[1:], developed_energy.iloc[3, 1:].values[1:])
#if __name__ == '__main__':
#    print(energy_data)
