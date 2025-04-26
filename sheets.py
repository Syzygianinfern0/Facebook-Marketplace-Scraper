from datetime import datetime

import gspread


class Sheets:
    def __init__(self):
        self.gc = gspread.service_account(filename="credentials.json")
        self.sheet = self.gc.open("Marketplace Scraper")

    def get_queries(self):
        queries = self.sheet.worksheet("Queries")
        # queries = queries.col_values(1)

        # Retrieve all rows of data from the sheet
        data = queries.get_all_values()

        # Extract the first column as queries, second as min prices, and third as max prices
        queries = [row[0] for row in data[1:]]  # Skip the header row
        min_prices = [int(row[1]) if row[1].isdigit() else 0 for row in data[1:]]  # Default to 0
        max_prices = [int(row[2]) if row[2].isdigit() else float("inf") for row in data[1:]]  # Default to inf

        # Combine the results into a list of dictionaries for easier handling
        results = {
            query: {"min_price": min_price, "max_price": max_price}
            for query, min_price, max_price in zip(queries, min_prices, max_prices)
        }

        return results

    def create_worksheet(self, title):
        worksheet = self.sheet.add_worksheet(title, 1000, 26)
        # Add headers for detailed info
        worksheet.update("A1:F1", [["Link", "Price", "Creation Time", "Location", "Latitude", "Longitude"]])

    def get_links(self, title):
        try:
            worksheet = self.sheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            self.create_worksheet(title)
            worksheet = self.sheet.worksheet(title)

        links = worksheet.col_values(1)
        return links

    def update_links(self, title, new_links, prices, listing_info):
        worksheet = self.sheet.worksheet(title)
        old_links = self.get_links(title)
        start_row = len(old_links) + 1

        # Prepare data for update
        update_data = []
        for link in new_links:
            info = listing_info.get(link, {})
            row = [
                link,
                prices[link],
                info.get("creation_time", "").strftime("%Y-%m-%d %H:%M:%S") if info.get("creation_time") else "",
                info.get("location", ""),
                info.get("latitude", ""),
                info.get("longitude", ""),
            ]
            update_data.append(row)

        # Update the sheet
        update_range = f"A{start_row}:F{start_row + len(update_data) - 1}"
        worksheet.update(update_data, update_range)
