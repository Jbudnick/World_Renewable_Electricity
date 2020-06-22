import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


class Analysis(object):
    '''
    The analysis class will allow a user to add a list of countries. These will then be converted into proportions and can be plotted and/or used for a hypothesis test of whether the proportions have increased over the years.
    '''
    def __init__(self, data, title='untitled', startcol=1980, end_year = 2017):
        '''
        Parameters:
        data(pandas DataFrame): Electrical Energy Generation dataframe
        title (str): designate a title for plotting the data
        startcol (int): Starting year for analysis
        end_year: Ending year for analysis
        '''
        self.data = data.drop(range(1980, startcol), axis=1)
        self.start_year = startcol
        self.end_year = end_year
        self.year = data.columns[(startcol-1978):]
        self.title = title
        self.analyze_list = []
        self.countries_analyzed = []

    def show_countries(self, for_analysis='T'):
        '''
            Parameters:
                for_analysis (bool): If T, will show only countries in analysis object. If F, will show all countries in dataset
            Returns:
                countries_analyzed or all countries
        '''
        return self.countries_analyzed if for_analysis == 'T' else set(self.data.loc[:, 'Country'])

    
    def check_aggregates(self, country='Norway', start_year=1980, end_year=2017):
        '''
        Check that the aggregated rows equal the sum of the subset rows - used for development only as sanity check, not used in analysis
        '''
        print('Checking Renewable subrows = renewable total row')
        for each in range(start_year, end_year + 1):
            if round(self.data[self.data['Country'] == country].loc[:, each].iloc[4:10].sum(), 3) != round(self.data[self.data['Country'] == country].loc[:, each].iloc[3], 3):
                print(each, ' has unequal values')
                break
        print('Checked Renewable subrows = renewable total row')
        print('Checking all subrows =  total row')
        for each in range(start_year, end_year + 1):
            if round(self.data[self.data['Country'] == country].loc[:, each].iloc[[1, 2, 3, 10]].sum(), 3) != round(self.data[self.data['Country'] == country].loc[:, each].iloc[0], 3):
                print(each, ' has unequal values')
                break
        print('Checked all subrows=total row')

    def add_countries(self, country_list, orderby_latest=True):
        '''
        Add more countries to Analysis class
            Parameters:
                country_list(list): List of countries to add
                orderby_latest(bool): Make latest data appear first
            returns:
                self.propDF(Pandas DataFrame): Revised DataFrame with countries added, with proportions applied
        '''
        self.propDF = calculate_proportions(self.data, self.start_year, self.end_year, country_list, orderby_latest=True)
        if orderby_latest == True:
            self.propDF.sort_values(
                self.year[-1], ascending=False, inplace=True)
        self.analyze_list = self.propDF.to_numpy()
        self.countries_analyzed = list(self.propDF.index)
        return self.propDF

    def plot_data(self, figsize=(14, 8), maxlines=10, include_world=False, include_legend=True):
        '''
        Plot data in class
            Parameters:
                maxlines(int): Maximum number of countries to show
                include_world(bool): Include the aggregated world plot
            Returns:
                self.fig(plot)
        '''
        self.fig, ax = plt.subplots(1, 1, figsize=figsize)
        if include_world == True:
            ax.plot(self.year, calculate_proportions(["World"]).to_numpy().flatten()[
                    (self.year[0] - 1980):], color='blue', ls=(0, (10, 12)), linewidth=0.8, label='World')
        for i, y_data_set in enumerate(self.analyze_list[0: maxlines]):
            ax.plot(self.year, y_data_set[(
                self.year[0] - 1980):], label=self.countries_analyzed[i])
        ax.set_ylabel('Proportion of Total Electrcity Generated')
        ax.set_title(
            'Renewable Electricity Produced from {}'.format(self.title))
        ax.legend(loc='center left', bbox_to_anchor=(
            1, 0.5)) if include_legend == True else None
        return self.fig

    def make_hist(self, figsize=(12, 8)):
        '''
        Create histogram of data in class
        '''
        self.fig, ax = plt.subplots(1, 1, figsize=figsize)
        ax.hist([self.propDF[self.year[0]], self.propDF[self.year[20]],
                 self.propDF[self.year[-1]]], label=[self.year[0], self.year[20], self.year[-1]])
        ax.legend()
        ax.set_xlabel('Proportion of Renewable Electricity Produced')
        ax.set_title('Histogram of {}'.format(self.title))
        return self.fig

    def hypo_test(self, aggregated=True, increase_thres=0.15, alpha=0.05):
        '''
        Run hypothesis test on data to test for improvement over the years
            Parameters:
                aggregated(bool): If true, test for group of countries data as a whole region. If False, test each individual country in the region and determine if the majority of countries show improvement.
                increase_thres(float): The minimum amount of improvement (0.15 = 15%) needed to classify if the country has increased renewable electricity generation or not (only used when aggregated is false)
                alpha (float): The significance level for rejecting the null hypothesis (0.05 = 5%)
            Returns:
                printed statement of test result
        '''
        #Use average of 1980 to 1983 and 2014 to 2017 to account for variability
        n = len(self.countries_analyzed)
        subset1_avgs = []
        subset2_avgs = []

        for prop in self.analyze_list:
            country_subset1 = np.mean([prop[(yr1 - 1980)]
                                       for yr1 in self.year[0:3]])
            subset1_avgs.append(country_subset1)
            country_subset2 = np.mean(
                [prop[list(self.year).index(yr2)] for yr2 in self.year[-3:]])
            subset2_avgs.append(country_subset2)
        if aggregated == True:
            subset1_mean, subset1_stdev = np.mean(
                subset1_avgs), np.std(subset1_avgs)
            subset2_mean = np.mean(subset2_avgs)
            p = 1 - stats.norm(subset1_mean, subset1_stdev).cdf(subset2_mean)
            print('P-value: ', p)
            if p <= alpha:
                print("Reject null hypothesis. Evidence suggests that {} are generating a greater proportion of renewable electricity in {} than in {}".format(
                    self.title, self.year[-1], self.year[0]))
            else:
                print("Fail to reject null hypothesis. Insufficient evidence to suggest that {} are generating a greater proportion of electricity in {} than in {}.". format(
                    self.title, self.year[-1], self.year[0]))
        else:
            counter = 0
            total = 0
            for i in range(n):
                if (subset2_avgs[i] >= 0.9) & (subset1_avgs[i] >= 0.9):
                    continue
                if subset2_avgs[i] >= subset1_avgs[i] + increase_thres:
                    counter += 1
                    total += 1
                elif subset2_avgs[i] <= subset1_avgs[i]:
                    total += 1
            p = 1 - stats.binom(total, p=0.5).cdf(counter)
            print('P-value: ', p)
            if p <= alpha:
                print("Reject null hypothesis. Evidence suggests that more than 50% of countries have increased renewable electricity proportion by at least {} % in the time period.".format(
                    100 * increase_thres))
            else:
                print("Fail to reject null hypothesis. Insufficient evidence to suggest that more than 50% of countries have increased renewable electricity generation by at least {} % in the time period".format(100*increase_thres))


def calculate_proportions(energy_data, start_year, end_year, country_list, orderby_latest=True):
    '''
    Convert data to proportion of renewable energy to total energy generated
        Parameters:
            energy_data(Pandas DataFrame): Main dataframe imported for electricity generation of all countries
            start_year(int): Starting year for analysis
            end_year(int): Ending year for analysis
            country_list(list): List of countries to include in result
            orderby_latest(bool): Show most recent data first
        Returns:
            RenewDF(Pandas Dataframe): DataFrame of countries in country_list of proportions from start_year to end_year

    '''
    calc_list, countries_calc = [], []
    for country in country_list:
        if country not in set(energy_data['Country']):
            print(country, 'is not in energy data and has been skipped.')
            continue
        if float(energy_data[end_year][(energy_data['Country'] == country) & (energy_data['Energy Type'] == 'Generation (billion Kwh)')]) == 0:
            #print(country, 'has 0 or unknown electricity generation. Skipped')
            continue

        renewable_vals = energy_data[(energy_data['Country'] == country) & (
            energy_data['Energy Type'] == '3.Renewables (billion Kwh)')]

        total_gen = energy_data[(energy_data['Country'] == country) & (
            energy_data['Energy Type'] == 'Generation (billion Kwh)')].iloc[0, 2:].to_numpy()

        hydro_storage = energy_data[(energy_data['Country'] == country) & (
            energy_data['Energy Type'] == '4.Hydroelectric pumped storage (billion Kwh)')].iloc[0, 2:].to_numpy()

        total_generation_vals = total_gen - hydro_storage
        renewable_vals = renewable_vals.iloc[:, 2:].to_numpy().flatten()
        if 0 in total_generation_vals:
            renew_proportions = []
            for i, each in enumerate(total_generation_vals):
                if each != 0:
                    renew_proportions.append(
                        renewable_vals[i] / total_generation_vals[i])
                else:
                    renew_proportions.append(each)
        else:
            renew_proportions = renewable_vals / total_generation_vals
        renew_proportions = np.array([round(each, 3)
                                      for each in renew_proportions])
        calc_list.append(renew_proportions)
        countries_calc.append(country)
        years_analyzed = range(start_year, end_year + 1)
        RenewDF = pd.DataFrame(calc_list, columns=years_analyzed, index=countries_calc)
        if orderby_latest == True:
            RenewDF.sort_values(years_analyzed[-1], ascending=False)
    return RenewDF

def get_improved_countries(energy_data, countries, years, improvement_perc=.274, include_early_0s=False):
    '''
    Get list of countries that have shown a certain percentage of improvement over the years in renewable electrical energy generation
        Parameters:
            energy_data(Pandas DataFrame): Main dataframe of all electrical generation data
            countries(list): All countries to consider
            years (range/list): Starting year to ending year
            improvement_perc (float): Minimum amount of improvement needed to include in final dataset from countries (0.274 = 27.4%)
            include_early_0s(bool): Eliminates data with 0 electrical generation values in starting year - assumed to be missing
        Returns:
            prop_DF (Pandas DataFrame): DataFrame of countries that have met the improvement_perc improvement over the years.

    '''
    propDF = calculate_proportions(energy_data, start_year = years[0], end_year = years[-1], country_list = countries)
    propDF['Improvement'] = propDF[years[-1]] - propDF[years[0]]
    propDF = propDF[propDF['Improvement'] >= improvement_perc]
    if include_early_0s == False:
        propDF = propDF[propDF[years[0]] != 0]
    propDF.sort_values('Improvement', ascending=False, inplace=True)
    return propDF

def print_analyses(energy_data, cont_data, years_analyzed, developed_countries, allcountries, high_pop, countries_to_analyze):
    '''
    Prints hypothesis test results for all subgroups of data
        Parameters:
            energy_data (Pandas DataFrame)
            cont_data(Pandas DataFrame)
            years_analyzed(range): Range from minimum to maximum year of analysis
            developed_countries(Pandas DataFrame): DataFrame sorted based on level HDI
            allcountries(list): All countries
            high_pop(Pandas DataFrame): DataFrame sorted based on population
            countries_to_analyze(int): Maximum number of countries in each category to include in analysis
        Returns:
            Printed hypothesis results
    '''
    print('------------------------------------------')

    Least_Dev_Analysis = Analysis(
        energy_data, title='Least Developed Countries')
    Least_Dev_Analysis.add_countries(
        developed_countries[-1: -1 * countries_to_analyze: -1], orderby_latest=False)
    Least_Dev_Analysis.hypo_test()

    print('------------------------------------------')

    HighPop_Analysis = Analysis(
        energy_data, 'Countries with Largest Population')
    HighPop_Analysis.add_countries(
        list(high_pop['Country']), orderby_latest=False)
    HighPop_Analysis.hypo_test()

    print('------------------------------------------')

    North_America_Analysis = Analysis(energy_data, 'North American Countries')
    North_America_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'North America'].loc[:, 'Country'])
    North_America_Analysis.hypo_test()

    print('------------------------------------------')

    South_America_Analysis = Analysis(
        energy_data, 'Central & South American Countries')
    South_America_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Central & South America'].loc[:, 'Country'])
    South_America_Analysis.hypo_test()

    print('------------------------------------------')

    Europe_Analysis = Analysis(energy_data, 'European Top Countries')
    Europe_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Europe'].loc[:, 'Country'])
    Europe_Analysis.hypo_test()

    print('------------------------------------------')

    #These countries split from USSR in 1992 - using that column instead of 1980
    Eurasia_Analysis = Analysis(
        energy_data, title='Eurasia Top Countries', startcol=1992)
    Eurasia_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Eurasia'].loc[:, 'Country'])
    Eurasia_Analysis.hypo_test()

    print('------------------------------------------')

    Asia_Analysis = Analysis(
        energy_data, 'Asia & Oceania Countries')
    Asia_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Asia & Oceania'].loc[:, 'Country'])
    Asia_Analysis.hypo_test()

    print('------------------------------------------')

    MidEast_Analysis = Analysis(
        energy_data, 'Middle East Countries')
    MidEast_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Middle East'].loc[:, 'Country'])
    MidEast_Analysis.hypo_test()

    print('------------------------------------------')

    Africa_Analysis = Analysis(
        energy_data, 'African Countries')
    Africa_Analysis.add_countries(
        cont_data[cont_data['Continent'] == 'Africa'].loc[:, 'Country'])
    Africa_Analysis.hypo_test()

    print('------------------------------------------')

    Improved_Analysis = Analysis(energy_data, 'Largest Increase Countries')
    Improved_Analysis.add_countries(get_improved_countries(
        energy_data, allcountries, years=years_analyzed, improvement_perc=.27).index)
    Improved_Analysis.hypo_test()

    print('------------------------------------------')

    highest_prop_countries = list(calculate_proportions(energy_data, start_year=1980, end_year=2017, country_list = allcountries).sort_values(
        2017, ascending=False).loc[:, 2017].iloc[:20].index)

    AllCountries_hist = Analysis(energy_data, 'All Countries in the World')
    AllCountries_hist.add_countries(allcountries)
