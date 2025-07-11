# LinkedIn Email Finder

This project processes LinkedIn follower data to find email addresses using the Anymail Finder API.

## Features

- Loads LinkedIn follower data from CSV files
- Removes duplicate profiles between two follower lists
- Fetches email addresses using Anymail Finder API for LinkedIn URLs
- Exports results with email data appended to the original CSV

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file with your Anymail Finder API key:
```
ANYMAIL_API_KEY=your_api_key_here
```

## Usage

Run the script:
```bash
poetry run python linkedin_email_finder.py
```

This will:
1. Load `katy-followers.csv` and `sophia-followers.csv`
2. Remove any profiles from katy-followers that exist in sophia-followers
3. Fetch emails for the remaining profiles
4. Save results to `katy-followers-with-emails.csv`

## Files

- `katy-followers.csv` - Input file with LinkedIn follower data
- `sophia-followers.csv` - Comparison file to filter out duplicates
- `linkedin_email_finder.py` - Main script for processing
- `katy-followers-with-emails.csv` - Output file (created after running)