# Stock Key Executive Image Scraper
## Overview

Welcome to the Stock Key Executive Image Scraper! This Python application utilizes web scraping techniques with Selenium and BeautifulSoup to fetch images of key executives of various stocks from Google. It helps you automate the process of gathering executive images for your stock analysis or research.

## Features

- Automated scraping of executive images for a list of stock symbols.
- Organizes downloaded images into symbol-specific folders.
- Provides screenshot examples of executive images for reference.

## Screenshots

Here are some screenshots of the application:

1. **Root Directory**:
    - The root directory contains folders for each stock symbol, named after their respective symbols.

    ![Root Directory](/Images/root_folder.png)

2. **Symbol Subfolder**:
    - Within each symbol folder, you will find the executive images.

    **AAPL**
    ![Symbol Subfolder](/Images/AAPL.png)

    **GOOG**
    ![Symbol Subfolder](/Images/GOOG.png)

    **JNJ**
    ![Symbol Subfolder](/Images/JNJ.png)

    **MSFT**
    ![Symbol Subfolder](/Images/MSFT.png)

    **NVDA**
    ![Symbol Subfolder](/Images/NVDA.png)

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/YourUsername/Stock-Executive-Scraper.git
   ```

2. Install the required dependencies:

   ```bash
   pip install selenium beautifulsoup4 pandas
   ```

3. Download and install the appropriate WebDriver for your browser (e.g., ChromeDriver for Google Chrome).

4. Configure the application by editing the `config.json` file with your browser driver path, target URLs, and other settings.

5. Run the scraper:

   ```bash
   python main.py
   ```

## Usage

- Modify the `symbol_list.txt` file with the stock symbols you want to scrape.
- Customize the scraping parameters in the `config.json` file.
- Run the application to start scraping the executive images.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to [Selenium](https://selenium.dev/) and [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for making web scraping easier.
- Shoutout to the open-source community for their contributions and support.

## Contributing

Contributions are welcome! Please create an issue or submit a pull request if you have any improvements, bug fixes, or new features to suggest.

## Author

- Your Name
- GitHub: [YourUsername](https://github.com/YourUsername)
```

Make sure to replace placeholders like `YourUsername` with your actual GitHub username, and you can also customize the content to match the specifics of your project.