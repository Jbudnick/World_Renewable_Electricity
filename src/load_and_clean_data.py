import pandas as pd
import numpy as np

def years_to_int(first_year, last_year):
    '''
    Converts years (stored as string) into integers
    '''
    years_to_int = {str(year): year for year in range(
        first_year, last_year + 1)}
    return years_to_int

def indent_replace(a_series):
    '''
    Original Data in dataframe is organized by indentations as opposed to separate columns for categories. This function converts the indentations.
        Parameters:
            a_series (Pandas Series): Series that consists of the column that should be divided based on indentations
        Returns:
            Series with only data in the proper category for countries
    '''
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
            new_series.append('{}'.format(type1) + '.' +
                              '{}'.format(type2) + '.' + no_indent)
        else:
            print('error, ommitted {}'.format(string))
    return new_series


def combine_countries(df, years_analyzed, combine_list, into_country):
    '''
    Combines countries into one
        Parameters:
            df(Pandas DataFrame): Main dataframe with country info
            years_analyzed(Range)
            combine_list(list of strings): List of countries to combine with into_country (and then to remove from df)
            into_country(str): Country to combine countries into
        Returns:
            df (Pandas Dataframe): DataFrame with countries combined
    '''
    into_data = df[df['Country'] == into_country].loc[:, years_analyzed]
    into_rows = into_data.index
    into_country_data = into_data.to_numpy()
    for country in combine_list:
        into_country_data += df[df['Country'] ==
                                country].loc[:, years_analyzed].to_numpy()
        row_indexes = df[df['Country'] == country].loc[:, years_analyzed].index
        df.loc[row_indexes, years_analyzed] = 0
    df.loc[into_rows, years_analyzed] = into_country_data
    return df

def electricity_generation_data_import(start_year, end_year):
    '''
    Import electricity generation data and clean it
    The original energy data is formatted with leading spaces to identify subgroups of each type. This function iterates through and replaces these using numerical indexing for readbility in DataFrames.
    Assumptions - "--" or NaN means that no data is available for the time period. These will be replaced with 0.

        Parameters:
            start_year(int): Starting year for analysis
            end_year(int): Ending year for analysis
        Returns:
            energy_data (Pandas DataFrame): Dataframe with electrical generation data over years for all countries
            allcountries(list): All countries included in dataset
    '''

    energy_data = pd.read_csv(
        'data/INT-Export-04-05-2020_00-10-38.csv', header=1)
    energy_data.rename(
        columns={'Unnamed: 1': 'Energy Type', 'API': 'Country Code'}, inplace=True)
    energy_data.rename(columns=years_to_int(
        first_year=start_year, last_year=end_year), inplace=True)
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
    energy_data.reset_index(drop=True, inplace=True)

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
    energy_data.replace('--', 0, inplace=True)
    energy_data.iloc[:, 2:] = energy_data.iloc[:, 2:].astype('float')

    #Countries provides another dataframe to translate country codes into Country Names
    countries.reset_index(drop=True, inplace=True)
    country_code = energy_data['Country Code'].copy()
    country_code.drop_duplicates(inplace=True)
    country_code.reset_index(drop=True, inplace=True)
    countries = pd.DataFrame(country_code).join(countries)
    countries.rename(columns={'Energy Type': 'Country'}, inplace=True)
    energy_data.merge(countries)

    #Replace Country codes with country names, combines split countries
    energy_data = energy_data.iloc[:, :1].merge(
        countries).join(energy_data.iloc[:, 1:])
    energy_data.drop('Country Code', axis=1, inplace=True)
    years_analyzed = range(start_year, end_year + 1)
    combine_countries(
        energy_data, years_analyzed, ['Germany, East', 'Germany, West'], 'Germany')
    combine_countries(energy_data, years_analyzed, ['Former Czechoslovakia'], 'Czech Republic')
    combine_countries(energy_data, years_analyzed, ['Former U.S.S.R.'], 'Russia')

    allcountries = set(energy_data['Country'][1:])
    allcountries.remove("World")
    return energy_data, allcountries

def HDI_data_import():
    '''
    Returns:
        Cleaned UN HDI data for all countries
    '''
    HDI_data = pd.read_csv('data/HDI.csv', nrows=190)
    HDI_data.rename(columns=years_to_int(1990, 2018), inplace=True)
    HDI_data.drop(0, inplace=True)
    HDI_data['Country'] = HDI_data['Country'].str.lstrip()
    HDI_data.drop([HDI_data.columns[x] for x in range(
        3, len(HDI_data.columns), 2)], axis=1, inplace=True)
    HDI_data.iloc[:, 0] = HDI_data.iloc[:, 0].astype('int')
    HDI_data['Country'].replace(
        'Hong Kong, China (SAR)', "Hong Kong", inplace=True)
    HDI_data['Country'].replace(
        'Korea (Republic of)', "South Korea", inplace=True)
    HDI_data['Country'].replace(
        'Czechia', "Czech Republic", inplace=True)
    HDI_data['Country'].replace(
        'Russian Federation', "Russia", inplace=True)
    HDI_data['Country'].replace(
        'Congo (Democratic Republic of the)', "Congo-Kinshasa", inplace=True)
    HDI_data['Country'].replace(
        'Gambia', "Gambia, The", inplace=True)
    HDI_data['Country'].replace(
        "Côte d'Ivoire", "Cote dIvoire", inplace=True)
    HDI_data['Country'].replace(
        'Tanzania (United Republic of)', "Tanzania", inplace=True)
    developed_data = HDI_data.sort_values(
        'HDI Rank')['Country'].reset_index(drop=True)
    developed_countries = list(developed_data)
    return HDI_data, developed_countries


def population_data_import(start_year, end_year, countries_to_analyze):
    '''
    Import population data and clean it
        Parameters:
            start_year(int): Starting year for analysis
            end_year(int): Ending year for analysis
            countries_to_analyze(int): Maximum number of countries to analyze
        Returns:
            pop_data (Pandas DataFrame): DataFrame sorted by countries with highest populations
            high_pop (List): List of countries with highest populations
    '''
    pop_data = pd.read_csv('data/API_SP.POP.csv', header=4)
    pop_data_min_year = 1960
    pop_data.rename(columns=years_to_int(
        first_year=pop_data_min_year, last_year=end_year), inplace=True)

    pop_data.drop(['Unnamed: 64', 'Indicator Name',
                   'Indicator Code', '2018', '2019'], axis=1, inplace=True)

    #Removing aggregated regions to avoid double counting
    regions_to_remove = (
        'Arab World', 'Caribbean small states', 'Central Europe and the Baltics', 'Early-demographic dividend', 'East Asia & Pacific', 'East Asia & Pacific (excluding high income)', 'East Asia & Pacific (IDA & IBRD countries)', 'Europe & Central Asia (IDA & IBRD countries)', 'Euro area', 'Europe & Central Asia', 'Europe & Central Asia (excluding high income)', 'European Union', 'Fragile and conflict affected situations', 'Heavily indebted poor countries (HIPC)', 'IBRD only', 'IDA & IBRD total', 'IDA total', 'IDA blend', 'IDA only', 'Latin America & Caribbean', 'Latin America & the Caribbean (IDA & IBRD countries)', 'IDA only', 'Late-demographic dividend', 'Latin America & Caribbean (excluding high income)',
        'Least developed countries: UN classification', 'Middle East & North Africa', 'Middle East & North Africa (excluding high income)', 'Middle East & North Africa (IDA & IBRD countries)', 'North America', 'Not classified', 'OECD members', 'Other small states', 'Pacific island small states', 'Pre-demographic dividend', 'Post-demographic dividend', 'Small states', 'South Asia', 'South Asia (IDA & IBRD)', 'Sub-Saharan Africa (IDA & IBRD countries)', 'Sub-Saharan Africa', 'Sub-Saharan Africa (excluding high income)', 'High income', 'Low & middle income', 'Low income', 'Lower middle income', 'Middle income', 'Upper middle income')

    pop_data.drop(pop_data[pop_data['Country Name'].isin(
        regions_to_remove)].index, inplace=True)

    #Modifying index so that aggregated World row is placed on top, rest are alphabetical order, removing invalid entries

    pop_data.sort_values('Country Name', inplace=True)
    pop_data.fillna(0, inplace=True)
    pop_data.reset_index(drop=True, inplace=True)
    pop_data.index += 1
    pop_data.loc[0] = pop_data.loc[215]
    pop_data.drop(215, inplace=True)
    pop_data.sort_index(inplace=True)
    pop_data.reset_index(drop=True, inplace=True)
    pop_data.rename(columns={'Country Name': 'Country'}, inplace=True)
    pop_data['Country'].replace(
        'Russian Federation', "Russia", inplace=True)
    pop_data['Country'].replace(
        'Egypt, Arab Rep.', "Egypt", inplace=True)
    pop_data['Country'].replace(
        'Iran, Islamic Rep.', "Iran", inplace=True)
    pop_data['Country'].replace(
        'Korea, Rep.', "South Korea", inplace=True)
    pop_data['Country'].replace(
        'Congo, Dem. Rep.', "Congo-Kinshasa", inplace=True)
    '''
    --------------------------------------------
    Highest population dataset determined here
    --------------------------------------------
    '''
    high_pop = pop_data.sort_values(start_year, ascending=False).copy()[
        1: countries_to_analyze]
    return pop_data, high_pop


def continent_data_import():
    '''
    Returns:
        cont_data(Pandas DataFrame): Dataframe grouping all countries into the respective continent.
    '''
    cont_data = pd.read_csv('data/CountryContent.csv', header=4)
    cont_data.drop(['4203.93645368'],
                   axis=1, inplace=True)
    cont_data.rename(columns={
        'INTL.2-12-USA-BKWH.A': 'Continent', '        United States': 'Country'}, inplace=True)
    cont_data['Continent'].iloc[0:58] = 'Africa'
    cont_data['Continent'].iloc[58:106] = 'Asia & Oceania'
    cont_data['Continent'].iloc[106:152] = 'Central & South America'
    cont_data['Continent'].iloc[152:160] = 'North America'
    cont_data['Continent'].iloc[160:175] = 'Middle East'
    cont_data['Continent'].iloc[175:221] = 'Europe'
    cont_data['Continent'].iloc[221:] = 'Eurasia'
    cont_data['Country'] = cont_data['Country'].str.lstrip()
    cont_data.drop([0, 58, 106, 152, 160, 175, 221], inplace=True)
    cont_data.reset_index(drop=True)

    cont_data['Country'].replace("Côte d’Ivoire", "Cote dIvoire", inplace=True)
    return cont_data
