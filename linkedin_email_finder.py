import pandas as pd
import requests
import time
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anymail Finder API configuration
API_KEY = os.environ.get('ANYMAIL_API_KEY', '')  # Loaded from .env file
API_BASE_URL = 'https://api.anymail.io/v1'

def get_email_from_linkedin(linkedin_url: str) -> Dict:
    """
    Fetch email for a LinkedIn profile using Anymail Finder API
    
    Args:
        linkedin_url: LinkedIn profile URL
        
    Returns:
        Dict containing email data or error information
    """
    if not API_KEY:
        return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'API_KEY_NOT_SET'}
    
    try:
        # Anymail Finder API endpoint for LinkedIn email search
        endpoint = f"{API_BASE_URL}/search/person"
        
        params = {
            'api_key': API_KEY,
            'linkedin_url': linkedin_url
        }
        
        response = requests.get(endpoint, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('email'):
                return {
                    'email': data.get('email', ''),
                    'email_validation': data.get('email_validation', ''),
                    'title': data.get('person_title', ''),
                    'company': data.get('person_company', ''),
                    'email_error': ''
                }
            else:
                return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'NO_EMAIL_FOUND'}
        else:
            return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': f'API_ERROR_{response.status_code}'}
            
    except Exception as e:
        return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': f'EXCEPTION: {str(e)}'}

def process_linkedin_profiles():
    """
    Main function to process LinkedIn profiles and fetch emails
    """
    print("Loading CSV files...")
    
    # Load both CSV files
    katy_df = pd.read_csv('katy-followers.csv')
    sophia_df = pd.read_csv('sophia-followers.csv')
    
    print(f"Loaded {len(katy_df)} records from katy-followers.csv")
    print(f"Loaded {len(sophia_df)} records from sophia-followers.csv")
    
    # Remove duplicates - filter out people in sophia_df from katy_df
    # Using profileLink as the unique identifier
    sophia_profiles = set(sophia_df['profileLink'])
    katy_filtered_df = katy_df[~katy_df['profileLink'].isin(sophia_profiles)]
    
    print(f"After removing duplicates: {len(katy_filtered_df)} unique records remain")
    
    # Add email columns to the filtered dataframe
    katy_filtered_df['email'] = ''
    katy_filtered_df['email_validation'] = ''
    katy_filtered_df['title'] = ''
    katy_filtered_df['company'] = ''
    katy_filtered_df['email_error'] = ''
    
    # Process each profile to get emails
    total_profiles = len(katy_filtered_df)
    
    for idx, row in katy_filtered_df.iterrows():
        profile_link = row['profileLink']
        full_name = row['fullName']
        
        print(f"\nProcessing {idx + 1}/{total_profiles}: {full_name}")
        print(f"LinkedIn URL: {profile_link}")
        
        # Get email data
        email_data = get_email_from_linkedin(profile_link)
        
        # Update the dataframe with email data
        for key, value in email_data.items():
            katy_filtered_df.at[idx, key] = value
        
        if email_data['email']:
            print(f"✓ Found email: {email_data['email']}")
        else:
            print(f"✗ No email found: {email_data['email_error']}")
        
        # Rate limiting - Anymail Finder has rate limits
        # Adjust this based on your API plan
        time.sleep(1)  # 1 second delay between requests
    
    # Save the final output
    output_filename = 'katy-followers-with-emails.csv'
    katy_filtered_df.to_csv(output_filename, index=False)
    print(f"\n✓ Saved final output to {output_filename}")
    print(f"Total records processed: {len(katy_filtered_df)}")
    
    # Summary statistics
    email_found = katy_filtered_df['email'].notna() & (katy_filtered_df['email'] != '')
    print(f"\nSummary:")
    print(f"- Emails found: {email_found.sum()}")
    print(f"- Emails not found: {(~email_found).sum()}")
    
    return katy_filtered_df

if __name__ == "__main__":
    print("=== LinkedIn Email Finder ===")
    print("\nIMPORTANT: Make sure to set the ANYMAIL_API_KEY environment variable")
    print("Example: export ANYMAIL_API_KEY='your_api_key_here'")
    print("\nStarting processing...\n")
    
    result_df = process_linkedin_profiles()