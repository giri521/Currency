# Currency

[Deployed Link](https://currency-2-23fd.onrender.com/)

## Overview

Currency is a web-based currency converter that allows users to convert between different currencies in real-time. It provides an easy-to-use interface where users can select currencies, enter an amount, and instantly view the converted value. The app fetches the latest exchange rates from an external API, ensuring accurate and up-to-date conversions.

## Features

* Real-time currency conversion.
* Easy selection of base and target currencies.
* Instant calculation of conversion results.
* Clean and responsive user interface.
* Error handling for invalid inputs and API issues.

## Technologies Used

* **Python** – Backend logic.
* **Flask** – Web framework for routing and rendering.
* **HTML, CSS, JavaScript** – Frontend design and interactivity.
* **Exchange Rate API** – Fetches live currency data.
* **Requests** – Handles API communication.

## Getting Started

### Prerequisites

* Python 3.x
* pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/giri521/Currency.git
   ```
2. Navigate to the project directory:

   ```bash
   cd Currency
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask application:

   ```bash
   python app.py
   ```
5. Open your browser and visit `http://127.0.0.1:5000/` or use the deployed link.

## Usage

1. Open the application.
2. Select the base currency (the one you have).
3. Select the target currency (the one you want to convert to).
4. Enter the amount to convert.
5. Click **Convert** to see the converted amount and exchange rate.

## File Structure

```
Currency/
│
├── app.py                # Main Flask application
├── templates/            # HTML files
├── static/               # CSS and JS assets
├── requirements.txt      # Project dependencies
└── README.md             # Documentation
```

## Future Enhancements

* Add support for historical exchange rate charts.
* Save favorite currency pairs for quick access.
* Include multi-language and dark mode options.
* Add conversion history tracking for registered users.
* Display percentage change or trends for selected currencies.

## Contributing

Contributions are welcome! Fork this repository, make your improvements, and submit a pull request. Suggested enhancements include API caching, UI improvements, and new feature integrations.

