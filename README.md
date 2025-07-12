# Password Strength Analyzer and Wordlist Generator Telegram Bot

This is a Telegram bot that provides two main functions:
1.  **Password Strength Analysis:** Analyzes the strength of a given password and provides feedback.
2.  **Wordlist Generation:** Generates a wordlist based on a given set of words.

## Features

*   **Password Strength Analysis:**
    *   Uses `zxcvbn` to estimate password strength.
    *   Provides a score from 0 to 4, where 4 is the strongest.
    *   Gives suggestions for improving password strength.
*   **Wordlist Generation:**
    *   Generates a wordlist from a given text.
    *   Filters words by length.
    *   Limits the size of the generated wordlist.

## How to Use

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NIZBAN786/Pwgen.git
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up your environment variables:**
    *   Create a `.env` file in the root directory.
    *   Add your Telegram bot token to the `.env` file:
        ```
        TELEGRAM_BOT_TOKEN=your-telegram-bot-token
        ```
4.  **Run the bot:**
    ```bash
    python run.py
    ```

## Dependencies

*   [python-telegram-bot](https://python-telegram-bot.org/)
*   [zxcvbn](https://pypi.org/project/zxcvbn/)
*   [nltk](https://www.nltk.org/)
*   [python-dotenv](https://pypi.org/project/python-dotenv/)
