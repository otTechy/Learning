# OneNote Excel Updater

This Python script automates the process of updating OneNote pages with data from Excel files. It uses Playwright for web automation and pandas for data processing.

## Features

- Read data from Excel files using pandas
- Automate interactions with OneNote web interface using Playwright
- Dynamically create new sections for different dates
- Update content in a structured format

## Requirements

- Python 3.8+
- Playwright
- Pandas
- openpyxl (for Excel file handling)

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

## Usage

1. Place your Excel file in the `data` folder or update the path in the config file
2. Update the configuration in `config.py` with your OneNote details
3. Run the script:

```bash
python main.py
```

## Project Structure

- `main.py`: Entry point of the application
- `excel_reader.py`: Module for reading and processing Excel data
- `onenote_updater.py`: Module for automating OneNote interactions
- `config.py`: Configuration settings
- `data/`: Directory for Excel files
- `utils/`: Utility functions

## License

MIT
