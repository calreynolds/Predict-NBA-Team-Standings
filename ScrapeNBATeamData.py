"""
ScrapeNBATeamData.py
Cal Reynolds


This script will be scraping and compiling all team data from years X-Y (given by our controller / main function).
End result will be a CSV for modularity (maybe ability to return dataframe based on flag).

Goal for this project is to use it periodically through the season and compare results versus actual performances
to evaluate model.
"""
import pandas as pd
import numpy as np
from urllib.request import urlopen

from bs4 import BeautifulSoup
from bs4 import Comment
import re


class NBATeamDataScraper:
    def perform_scrape_all_seasons_in_range(self, first_year, last_year):
        """ This will be our 'master' function, will take in which years you want to scrape.
            Will return the data either as CSV or pandas Dataframe.
            * Years are inclusive *                                                     """

        cumulative_dataframe = pd.DataFrame()
        for i in range(first_year, last_year+1):
            print(i)
        pass

    def perform_scrape_one_season(self, year):
        """ Scrape a single season based on season-specific URL from basketball-reference """
        base_url = "https://www.basketball-reference.com/leagues/NBA_"
        end_of_url = ".html"
        full_season_url = base_url + str(year) + end_of_url

        webpage_htmml = urlopen(full_season_url)
        webpage_soup = BeautifulSoup(webpage_htmml, 'html.parser')

        offense_data = self.gather_offense_data(self, webpage_soup)
        defense_data = self.gather_defense_data(self, webpage_soup)

        merged_data = self.merge_team_opponent_data(self, offense_data, defense_data)

        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_html.html

    def gather_offense_data(self, raw_data):
        """ Gather all data from that team's offense """
        pass

    def gather_defense_data(self, webpage_soup):
        """ Gather all data from that team's defense """
        # As our initial HTML for our table was wrapped in a comment, we perform two Beautiful soup calls.
        #  The first grabs the relavent comment HTML snippet. The second grabs the relevant table data.
        soup = webpage_soup.find_all(string=lambda text: isinstance(text, Comment) and "opponent" in text)
        soup2 = BeautifulSoup(soup[0], 'html.parser')

        # Runs a function to return a parsed table from HTML using BeautifulSoup.
        cleaned_data = self.clean_data_with_beautifulsoup(self, soup2)

        # This line gets rid of a "League Averages" row which doesn't contribute to data.
        cleaned_data = cleaned_data[:-1]

        print(cleaned_data)
        pass

    def merge_team_opponent_data(self, offense_data, defense_data):
        """ Merge the results of gather_offense_data and gather_defense_data into a single dataframe """
        pass

    def clean_data_with_beautifulsoup(self, soup_to_scrape):
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

        pass


def main():
    # Everything currently "passed" by compiler for testing.
    nbaTeamDataScraper = NBATeamDataScraper.perform_scrape_one_season(NBATeamDataScraper, 2008)

main()