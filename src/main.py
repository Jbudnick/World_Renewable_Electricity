#Objects: Countries
#Functions : Plot graphs

'''
To Do:
CLean Unnamed Column - Create Country Column, extract names


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

#Import electricity generation data and clean it
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

#Countries provides another database to translate country codes into Country Names
country_code = energy_data['Country Code'].copy()
country_code.index -= 1
countries = pd.DataFrame(countries).join(country_code)
countries.rename(columns ={'Energy Type': 'Country'})


#Import population data and clean it
population_data = pd.read_csv('data/API_SP.POP.csv', header=4)
population_data.drop(['Unnamed: 64', 'Indicator Name',
                      'Indicator Code', '2018', '2019'], axis=1, inplace=True)

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
