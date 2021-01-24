"""
ScrapeNBATeamData.py
Cal Reynolds


This script will be scraping and compiling all team data from years X-Y (given by our controller / main function).
End result will be a CSV for modularity (maybe ability to return dataframe based on flag).

Goal for this project is to use it periodically through the season and compare results versus actual performances
to evaluate model.
"""

import re
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import Comment


class NBATeamDataScraper:
    def perform_scrape_all_seasons_in_range(self, first_year, last_year):
        """ This will be our 'master' function, will take in which years you want to scrape.
            Will return the data either as CSV or pandas Dataframe.
            * Years are inclusive *                                                     """

        if first_year < 1971 and last_year < 1971:
            print("Error: Queries must be in range of 1971 - 2021. Returning NULL.")
            return pd.DataFrame()
        elif first_year < 1971:
            print("WARNING: Year must be greater than 1971. Returning your query from 1971 until last_year.")
            first_year = 1971
        if last_year > 2021:
            print("WARNING: We are in the year 2021. We cannot see stats from the future.")
            last_year = 2021
        if first_year > last_year:
            print("ERROR: First year in query must be less than or equal to the last year in the query. Returning NULL.")
            return pd.DataFrame()

        cumulative_dataframe = self.perform_scrape_one_season(self, first_year)
        for i in range(first_year+1, last_year+1):
            cumulative_dataframe = cumulative_dataframe.append(self.perform_scrape_one_season(self, i))

        # Create a true scaling index value for all appended rows, then remove previously incorrect one.
        cumulative_dataframe = cumulative_dataframe.reset_index().drop(["index"], axis=1)
        return cumulative_dataframe

    def perform_scrape_one_season(self, year):
        """ Scrape a single season based on season-specific URL from basketball-reference """
        base_url = "https://www.basketball-reference.com/leagues/NBA_"
        end_of_url = ".html"
        full_season_url = base_url + str(year) + end_of_url

        webpage_htmml = urlopen(full_season_url)
        webpage_soup = BeautifulSoup(webpage_htmml, 'html.parser')

        offense_data = self.gather_offense_data(self, webpage_soup)
        defense_data = self.gather_defense_data(self, webpage_soup)
        merged_data = self.merge_team_tables(self, offense_data, defense_data)

        all_teams_number_wins_df = self.grab_team_wins_df(self, webpage_soup)
        merged_data_with_wins = self.merge_team_tables(self, all_teams_number_wins_df, merged_data)
        return merged_data_with_wins

    def process_cleaned_data(self, cleaned_data, offense):
        """ 'Meat and Potatoes' operation here. It takes in an untamed dataframe and makes sure it's good to go."""

        # This line gets rid of a "League Averages" row which doesn't contribute to data.
        cleaned_data = cleaned_data[:-1]

        for i in range(len(cleaned_data)):
            cleaned_data[i] = cleaned_data[i][:-2]
            cleaned_data[i] = cleaned_data[i][2:]

            if not offense:
                # In this code snippet, we check if the team is a playoff team (denoted by the star character after
                #  the team title). I add dummy variable if in playoff, and remove the star after team name for cleaning.
                if 'Rk' in cleaned_data[i]:
                    cleaned_data[i] += ', PLYF'

                elif '*' in cleaned_data[i]:
                    cleaned_data[i] += ', 1'
                    cleaned_data[i] = cleaned_data[i].replace("*", "")

                else:
                    cleaned_data[i] += ', 0'
            elif offense:
                cleaned_data[i] = cleaned_data[i].replace("*", "")

            # Convert each row into a list so that eventual 2d list can be easily converted to dataframe.
            cleaned_data[i] = cleaned_data[i].split(', ')

        # List -> Dataframe.
        cleaned_data_df = pd.DataFrame(cleaned_data)

        # Grab labels from data, drop that row from our actual dataset, then set the labels as our dataframe col names.
        labels_df = cleaned_data[cleaned_data[1] == 'Team']

        # Add an OPP to the end of all labeled values for data's sake to understand diff of offense vs defense.
        if not offense:
            for i in range(len(labels_df)):
                if labels_df[i] != "Team" and labels_df[i] != "PLYF":
                    labels_df[i] = str(labels_df[i]) + "_OPP"

        cleaned_data_df = cleaned_data_df.drop(0, axis=0)
        cleaned_data_df.columns = labels_df

        # Order the teams alphabetically for merging.
        cleaned_data_revised = cleaned_data_df.sort_values('Team')

        return cleaned_data_revised

    def grab_team_wins_df(self, webpage_soup):

        # Grabs wins table HTML parsed info from webpage (east and west are stored separately by bball reference).
        soup = webpage_soup.find_all(lambda tag: tag.name =='table' and tag.has_attr('id')
                                    and (tag['id'] == "divs_standings_E" or tag['id'] == "divs_standings_W"))

        # Workaround solution where we concatonate the two tables as strings to be recompiled by BS.
        soup = str(soup[0]) + str(soup[1])
        wins_soup = BeautifulSoup(soup, 'html.parser')

        # Get our rows from wins table
        cleaned_data = self.clean_data_with_beautifulsoup(self, wins_soup)

        for i in range(len(cleaned_data)):

            # Perform parsing operations to clean data. Remove [[, ]], and convert strings into list format.
            cleaned_data[i] = cleaned_data[i][:-2]
            cleaned_data[i] = cleaned_data[i][2:]
            cleaned_data[i] = cleaned_data[i].split(", ")

            # Remove * so that merging with main dataframe is easy.
            if "*" in cleaned_data[i][0]:
                cleaned_data[i][0] = cleaned_data[i][0][:-1]

        cleaned_data_df = pd.DataFrame(cleaned_data).drop([2, 3, 4, 5, 6, 7], axis=1)

        # Labels for our wins DF. Unstacking switches column into row for proper labels.
        cleaned_data_df.columns = pd.DataFrame(["Team", "WINS"]).unstack()

        # Remove rows that contain division or conference information.
        cleaned_data_df = cleaned_data_df[~cleaned_data_df["Team"].str.contains("Conference")]
        cleaned_data_df = cleaned_data_df[~cleaned_data_df["Team"].str.contains("Division")]

        return cleaned_data_df

    def gather_offense_data(self, webpage_soup):
        """ Gather all data from that team's offense """

        # As our initial HTML for our table was wrapped in a comment, we perform two Beautiful soup calls.
        #  The first grabs the relavent comment HTML snippet. The second grabs the relevant table data.
        soup = webpage_soup.find_all(string=lambda text: isinstance(text, Comment) and "div_team-stats-per_game" in text)
        soup2 = BeautifulSoup(soup[0], 'html.parser')

        # Runs a function to return a parsed table from HTML using BeautifulSoup.
        cleaned_data = self.clean_data_with_beautifulsoup(self, soup2)

        cleaned_data_df = self.process_cleaned_data(self, cleaned_data, True)
        return cleaned_data_df

    def gather_defense_data(self, webpage_soup):
        """ Gather all data from that team's defense """

        # As our initial HTML for our table was wrapped in a comment, we perform two Beautiful soup calls.
        #  The first grabs the relavent comment HTML snippet. The second grabs the relevant table data.
        soup = webpage_soup.find_all(string=lambda text: isinstance(text, Comment) and "opponent" in text)
        soup2 = BeautifulSoup(soup[0], 'html.parser')

        # Runs a function to return a parsed table from HTML using BeautifulSoup.
        cleaned_data = self.clean_data_with_beautifulsoup(self, soup2)

        cleaned_data_df = self.process_cleaned_data(self, cleaned_data, False)

        # return the cleaned dataframe
        return cleaned_data_df

    def merge_team_tables(self, offense_data, defense_data):
        """ Merge the results of gather_offense_data and gather_defense_data into a single dataframe """
        return pd.merge(offense_data, defense_data, on="Team")

    def clean_data_with_beautifulsoup(self, soup_to_scrape):
        """ Extract table from HTML using beautiful soup """
        table = soup_to_scrape.find_all('tr')
        cleaned_data = []

        for elem in table:
            newcells = elem.find_all('th')
            newcells2 = elem.find_all('td')
            newcells3 = [newcells + newcells2]
            str_newcells3 = str(newcells3)
            clean5 = re.compile('<.*?>')
            clean4 = (re.sub(clean5, '', str_newcells3))
            cleaned_data.append(clean4)

        return cleaned_data


"""def main():
    nba_2020_data = NBATeamDataScraper.perform_scrape_all_seasons_in_range(NBATeamDataScraper, 1971, 2021)
    if not nba_2020_data.empty:
        print(str(nba_2020_data))
        nba_2020_data.to_csv("out.csv")
    else:
        print("it was empty")
main()"""