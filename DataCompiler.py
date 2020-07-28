import csv
import pycountry
from datetime import datetime


class DataCompiler:
    def __init__(self):
        self.OWID_DATA_FILE_NAME = "dates-data(OWID-data).csv"
        self.DATAHUB_DATA_FILE_NAME = "dates-data(datahub-data).csv"
        self.COMMON_DATES_FILE_NAME = "dates-data(common).csv"
        self.get_common_dates()

    def get_country_sets(self, file):
        """Returns a set of the countries."""
        countries_list = []
        with open(file, "r") as data_file:
            data = data_file.read().strip()
            data = data.split("\n")
            del data[0]

        for country_data in data:
            country_data = country_data[1:-1]
            country = country_data.split('","')[0]
            countries_list.append(country)

        countries_set = set(countries_list)
        return countries_set

    def remove_uncommon_countries(self, file, common_countries):
        """Removes the uncommon countries data."""
        with open(file, "r") as data_file:
            data = list(csv.DictReader(data_file))

        for country_num, country_data in enumerate(data):
            if country_data["Country"] not in common_countries:
                del data[country_num]

        return data

    def get_common_countries_dates_data(self):
        """Gets the common countries data from the 2 data sources."""
        owid_countries = self.get_country_sets(self.OWID_DATA_FILE_NAME)
        datahub_countries = self.get_country_sets(self.DATAHUB_DATA_FILE_NAME)
        common_countries = sorted(owid_countries.intersection(datahub_countries))

        # print(f"Number of countries in datahub: {len(datahub_countries)}")
        # print(f"Number of countries in owid: {len(owid_countries)}\n\n")

        self.datahub_dates_data = self.remove_uncommon_countries(self.DATAHUB_DATA_FILE_NAME, common_countries)
        self.owid_dates_data = self.remove_uncommon_countries(self.OWID_DATA_FILE_NAME, common_countries)

        # print(f"Number of common countries: {len(common_countries)}")
        # print(f"Number of countries data in datahub: {len(datahub_data)}")
        # print(f"Number of countries data in owid: {len(owid_data)}")

    def find_oldest_newest_date(self, comparing_dates):
        """Identifies and returns the oldest and newest date."""

        for index, date in enumerate(comparing_dates):
            year = int(date.split("-")[0])
            month = int(date.split("-")[1])
            day = int(date.split("-")[2])

            date = datetime(year, month, day)
            comparing_dates[index] = date

        newer_date = str(max(comparing_dates).date())
        older_date = str(min(comparing_dates).date())

        return {
            "newer": newer_date,
            "older": older_date,
        }

    def get_common_dates(self):
        """Calls the get_common_countries_data() and changes the start and end dates do that they are common."""

        self.get_common_countries_dates_data()

        self.common_dates_data = []

        for data_num in range(len(self.owid_dates_data)):
            owid_start_date = self.owid_dates_data[data_num]["Start Date"]
            datahub_start_date = self.datahub_dates_data[data_num]["Start Date"]

            owid_end_date = self.owid_dates_data[data_num]["End Date"]
            datahub_end_date = self.datahub_dates_data[data_num]["End Date"]

            start_date = self.find_oldest_newest_date([owid_start_date, datahub_start_date])["newer"]
            end_date = self.find_oldest_newest_date([owid_end_date, datahub_end_date])["older"]

            # print(f"Start Date: {start_date.date()} from {owid_start_date} and {datahub_start_date}")
            # print(f"End Date: {end_date.date()} from {owid_end_date} and {datahub_end_date}")

            country = self.owid_dates_data[data_num]["Country"]

            date_data = {
                "Country": country,
                "Start Date": start_date,
                "End Date": end_date,
            }

            self.common_dates_data.append(date_data)

    def get_all_countries_start_end_date(self):
        """Returns a start and end date which is true for all countries."""
        with open(self.COMMON_DATES_FILE_NAME, "r") as csv_dates_file:
            dates_data = list(csv.DictReader(csv_dates_file))

        start_dates, end_dates = [], []
        for country_date in self.common_dates_data:
            start_dates.append(country_date["Start Date"])
            end_dates.append(country_date["End Date"])

        self.start_date = self.find_oldest_newest_date(start_dates)["newer"]
        self.end_date = self.find_oldest_newest_date(end_dates)["older"]

    def make_csv(self):
        """Makes csv file of the common dates."""
        with open(self.COMMON_DATES_FILE_NAME, "w") as csv_write_file:
            csv_write_file.write('"Country","Start Date","End Date"\n')
            for country_date in self.common_dates_data:
                country = country_date["Country"]
                start_date = country_date["Start Date"]
                end_date = country_date["End Date"]
                line = f'"{country}","{start_date}","{end_date}"\n'
                csv_write_file.write(line)


if __name__ == "__main__":
    Compiler = DataCompiler()
    Compiler.make_csv()
