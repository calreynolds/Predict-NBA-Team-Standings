"""
ScrapeNBATeamData.py
Cal Reynolds


This script will be scraping and compiling all team data from years X-Y (given by our controller / main function).
End result will be a CSV for modularity (maybe ability to return dataframe based on flag).

Goal for this project is to use it periodically through the season and compare results versus actual performances
to evaluate model.
"""


class NBATeamDataScraper:
    def perform_scrape_all_seasons_in_range(self, range_of_years):
        """ This will be our 'master' function, will take in which years you want to scrape.
            Will return the data either as CSV or pandas Dataframe. """
        pass

    def perform_scrape_one_season(self, year):
        """ Scrape a single season based on season-specific URL from basketball-reference """
        pass

    def gather_offense_data(self, raw_data):
        """ Gather all data from that team's offense """
        pass

    def gather_defense_data(self, raw_data):
        """ Gather all data from that team's defense """
        pass

    def merge_team_opponent_data(self, offense_data, defense_data):
        """ Merge the results of gather_offense_data and gather_defense_data into a single dataframe """
        pass



def main():
    pass

main()