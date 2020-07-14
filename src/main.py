import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

from src.load_and_clean_data import electricity_generation_data_import, HDI_data_import, population_data_import, continent_data_import
from src.analysis_tools import Analysis, print_analyses

plt.close('all')
plt.style.use('ggplot')

if __name__ == '__main__':
    #Year parameters - must be between 1980 and 2017 (inclusive)
    start_year = 1980
    end_year = 2017
    years_analyzed = range(start_year, end_year + 1)
    countries_to_analyze = 35

    #Countries with a total electricity generation of 0 on end year are assumed to be missing data and are dropped. 
    energy_data, allcountries = electricity_generation_data_import(start_year, end_year)
    HDI_data, developed_countries = HDI_data_import()
    pop_data, high_pop = population_data_import(
        start_year, end_year, countries_to_analyze)
    cont_data = continent_data_import()

    Worldwide_Analysis = Analysis(energy_data, title='Worldwide')
    Development_Analysis = Analysis(energy_data, title='Top Developed Countries', generate_csv = False)
    Development_Analysis.add_countries(developed_countries[:countries_to_analyze], orderby_latest = False)
    Development_Analysis.hypo_test()
    print('------------------------------------------')
    Development_Analysis.hypo_test(aggregated = False)  

    print_analyses(energy_data, cont_data, years_analyzed,
                   developed_countries, allcountries, high_pop, countries_to_analyze)
    #Plots found in notebooks/Capstone1Plots.ipynb
