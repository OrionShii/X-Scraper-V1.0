# X-Scraper

## 🔍 Twitter Data Harvester V1.0

> ⚠️ **NOTICE:** This tool is still under active development. Some features may not work correctly or as expected. Use at your own risk and feel free to report any issues.

---

## Overview

**X-Scraper** is a powerful tool developed by **OrionShii** for scraping and harvesting tweet data from Twitter (now "X"). Built using Playwright and Python, it automates browser actions to gather tweets based on keywords, date ranges, languages, and more.

---

## 🚀 Features

- 🔍 **Search-based scraping** – Collect tweets based on specific keywords or hashtags  
- 🌐 **Language filtering** – Filter results by language (e.g., English, Indonesian)  
- 📅 **Date range filtering** – Limit collection to specific periods  
- 📄 **Export options** – Save results to CSV or JSON format  
- ⚙️ **Configurable limits** – Choose how many tweets to gather  
- 🔐 **Cookie-based authentication** – Use your own Twitter session cookies  
- 🧪 **Currently under development** – Expect rapid updates and changes  

---

## 🧰 Requirements

- Python 3.7+
- Google Chrome or Chromium
- [Playwright](https://playwright.dev/python/) for browser automation

---

## 📦 Installation

1. Clone this repository:
   ```
   git clone https://github.com/OrionShii/x-scraper.git
   cd x-scraper
   ```

2. Install dependencies:
   ```
   pip install playwright
   playwright install chromium
   ```

3. Install other required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script:
```
python x-scraper.py
```

Follow the interactive prompts to:
1. Enter your Twitter credentials (or use saved credentials)
2. Specify your search keyword(s)
3. Configure optional filters (language, date range)
4. Set the maximum number of tweets to collect
5. Choose your preferred output format

## Known Issues

As this project is still under development, you might encounter some issues:

- **Login failures**: Twitter's UI changes frequently, which can break the login process
- **Element detection issues**: Some tweet elements might not be properly detected
- **Rate limiting**: Twitter may rate-limit scraping activities
- **Anti-automation measures**: Twitter actively tries to prevent automation tools

## Troubleshooting

If you encounter issues:

1. Try running in non-headless mode to see what's happening
2. Check if your search criteria is too specific
3. Try without date or language filters
4. Ensure your Twitter account is in good standing
5. Wait if you've been rate-limited

## Legal Disclaimer

This tool is provided for educational and research purposes only. Please use responsibly and in accordance with Twitter's Terms of Service. The developers are not responsible for any misuse or violations of Twitter's terms.

## Contributing

Contributions are welcome! If you encounter bugs or have suggestions for improvements, please:

1. Open an issue describing the problem or enhancement
2. Submit a pull request with your proposed changes

## License
Feel Free To Use This
