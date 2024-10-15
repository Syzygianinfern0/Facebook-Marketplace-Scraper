import gspread


class Sheets:
    def __init__(self):
        self.gc = gspread.service_account(filename="credentials.json")
        self.sheet = self.gc.open("Marketplace Scraper")

    def get_queries(self):
        queries = self.sheet.worksheet("Queries")
        queries = queries.col_values(1)

        return queries

    def create_worksheet(self, title):
        self.sheet.add_worksheet(title, 1000, 26)

    def get_links(self, title):
        try:
            worksheet = self.sheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            self.create_worksheet(title)
            worksheet = self.sheet.worksheet(title)

        links = worksheet.col_values(1)

        return links

    def update_links(self, title, new_links):
        worksheet = self.sheet.worksheet(title)
        old_links = self.get_links(title)
        update_range = f"A{len(old_links) + 1}:A{len(old_links) + len(new_links)}"

        worksheet.update([[link] for link in new_links], update_range)
