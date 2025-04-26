# Facebook Marketplace Scraper

A Python-based web scraper for Facebook Marketplace that monitors listings based on specific search queries and notifies users about new listings that match their criteria.

https://github.com/user-attachments/assets/c6c6bb56-29c9-44b8-92e0-d1fe4d82569f

## Features

- Automated scraping of Facebook Marketplace listings every 30 minutes
- Configurable search queries with price range filters
- Real-time notifications for new listings
- Google Sheets integration for data storage and management
- Detailed listing information including:
  - Title
  - Price
  - Creation time
  - Location (with coordinates)
  - Listing URL

## Prerequisites

- Python 3.x
- Google Cloud Platform account with Google Sheets API enabled

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Syzygianinfern0/Facebook-Marketplace-Scraper.git
cd Facebook-Marketplace-Scraper
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Set up Google Sheets API:
   - Follow the instructions from [Gspread](https://docs.gspread.org/en/latest/oauth2.html) to set up the Google Sheets API
   - Save the credentials file as `credentials.json` in the project root

4. Configure the project:
   - Copy `config.example.yaml` to `config.yaml` and fill in your notification settings. More info [here](https://github.com/caronc/apprise/wiki).
   - Set up a Google Sheet named "Marketplace Scraper" with a worksheet named "Queries". You can find mine [here]([/](https://docs.google.com/spreadsheets/d/1MjUY5WidP5zUQ6ysvar66stE31HD1KgB5t1S4Dg_wCY/edit?usp=sharing)). 
   - Add your search queries and price ranges in the "Queries" worksheet. 

## Usage

1. Run the scraper:
```bash
./run.sh
```

Or run directly:
```bash
python main.py
```

The scraper will:
- Read search queries from Google Sheets
- Scrape Facebook Marketplace for new listings
- Store new listings in Google Sheets
- Send notifications for listings that match your criteria

## Project Structure

- `main.py`: Main scraper logic and orchestration
- `sheets.py`: Google Sheets integration
- `get_listing_info.py`: Standalone script for extracting listing details
- `credentials.json`: Google API credentials
- `config.yaml`: Configuration file
- `run.sh`: Shell script to run main.py file every 30 minutes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Or if you have any suggestions, please open an issue.

This project is not for any serious use. It is a simple scraper that I made for my own use. I do not take any responsibility for any issues that may occur.
