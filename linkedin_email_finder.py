import pandas as pd
import requests
import time
import os
import sys
from typing import Optional, Dict
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Anymail Finder API configuration
API_KEY = os.environ.get('ANYMAIL_API_KEY', '')  # Loaded from .env file
API_BASE_URL = 'https://api.anymailfinder.com/v5.1'

# Counters for statistics
stats = {
    'valid': 0,
    'risky': 0,
    'not_found': 0,
    'blacklisted': 0,
    'errors': 0,
    'total_processed': 0,
    'credits_used': 0
}

def get_email_from_linkedin(linkedin_url: str) -> Dict:
    """
    Fetch email for a LinkedIn profile using Anymail Finder API v5.1
    
    Args:
        linkedin_url: LinkedIn profile URL
        
    Returns:
        Dict containing email data or error information
    """
    if not API_KEY:
        return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'API_KEY_NOT_SET'}
    
    try:
        # Anymail Finder API v5.1 endpoint
        endpoint = f"{API_BASE_URL}/find-email/linkedin-url"
        
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'linkedin_url': linkedin_url
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            email_status = data.get('email_status', '')
            
            if email_status in ['valid', 'risky']:
                # Valid emails cost 2 credits
                if email_status == 'valid':
                    stats['credits_used'] += 2
                return {
                    'email': data.get('email', ''),
                    'email_validation': email_status,
                    'title': data.get('person_job_title', ''),
                    'company': data.get('person_company_name', ''),
                    'email_error': ''
                }
            else:
                return {
                    'email': '',
                    'email_validation': '',
                    'title': data.get('person_job_title', ''),
                    'company': data.get('person_company_name', ''),
                    'email_error': email_status or 'not_found'
                }
        elif response.status_code == 400:
            error_msg = response.json().get("message", "Bad request")
            return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': f'BAD_REQUEST: {error_msg}'}
        elif response.status_code == 401:
            return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'UNAUTHORIZED: Check API key'}
        elif response.status_code == 402:
            return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'PAYMENT_REQUIRED: Insufficient credits'}
        else:
            return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': f'API_ERROR_{response.status_code}'}
            
    except requests.exceptions.Timeout:
        return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': 'TIMEOUT'}
    except Exception as e:
        return {'email': '', 'email_validation': '', 'title': '', 'company': '', 'email_error': f'EXCEPTION: {str(e)}'}

def print_progress_bar(current, total, prefix='', suffix='', length=50):
    """Print a progress bar to console"""
    percent = 100 * (current / float(total))
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}')
    sys.stdout.flush()

def process_linkedin_profiles():
    """
    Main function to process LinkedIn profiles and fetch emails
    """
    print("\n" + "="*70)
    print("🚀 LinkedIn Email Finder - Using Anymail Finder API v5.1")
    print("="*70 + "\n")
    
    if not API_KEY:
        print("❌ ERROR: API key not found!")
        print("Please set your API key in the .env file:")
        print("ANYMAIL_API_KEY=your_api_key_here")
        return None
    
    print("📁 Loading CSV files...")
    
    # Load both CSV files
    katy_df = pd.read_csv('katy-followers.csv')
    sophia_df = pd.read_csv('sophia-followers.csv')
    
    print(f"✓ Loaded {len(katy_df):,} records from katy-followers.csv")
    print(f"✓ Loaded {len(sophia_df):,} records from sophia-followers.csv")
    
    # Remove duplicates - filter out people in sophia_df from katy_df
    sophia_profiles = set(sophia_df['profileLink'])
    katy_filtered_df = katy_df[~katy_df['profileLink'].isin(sophia_profiles)].copy()
    print(f"\n📊 After removing duplicates: {len(katy_filtered_df):,} unique records remain")
    
    # Add email columns
    katy_filtered_df['email'] = ''
    katy_filtered_df['email_validation'] = ''
    katy_filtered_df['title'] = ''
    katy_filtered_df['company'] = ''
    katy_filtered_df['email_error'] = ''
    
    # Process each profile to get emails
    total_profiles = len(katy_filtered_df)
    
    print(f"\n🎯 Processing {total_profiles:,} profiles...")
    print(f"⏱️  Rate limit: 6 requests/minute (10 seconds between requests)")
    print(f"💰 Credits: 2 per valid email found (free for not found/risky)\n")
    
    start_time = datetime.now()
    
    for idx in range(total_profiles):
        row = katy_filtered_df.iloc[idx]
        profile_link = row['profileLink']
        full_name = row['fullName']
        
        # Update stats
        stats['total_processed'] += 1
        
        # Calculate progress
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = stats['total_processed'] / (elapsed / 60) if elapsed > 0 else 0
        eta = (total_profiles - idx - 1) / rate if rate > 0 else 0
        
        # Clear previous lines and show current profile
        print(f"\n[{idx + 1:,}/{total_profiles:,}] 👤 {full_name}")
        print(f"🔗 {profile_link}")
        
        # Progress bar
        print_progress_bar(idx + 1, total_profiles, 
                         prefix='Progress:', 
                         suffix=f'ETA: {eta:.0f}m | Rate: {rate:.1f}/min | Credits: {stats["credits_used"]}')
        print()  # New line after progress bar
        
        # Get email data
        email_data = get_email_from_linkedin(profile_link)
        
        # Update the dataframe with email data
        for key, value in email_data.items():
            katy_filtered_df.at[idx, key] = value
        
        # Update statistics and show result
        if email_data['email']:
            if email_data['email_validation'] == 'valid':
                stats['valid'] += 1
                print(f"✅ Valid email: {email_data['email']} ({email_data['company']})")
            elif email_data['email_validation'] == 'risky':
                stats['risky'] += 1
                print(f"⚠️  Risky email: {email_data['email']} ({email_data['company']})")
        else:
            error = email_data['email_error']
            if 'not_found' in error.lower():
                stats['not_found'] += 1
                print(f"❌ No email found")
            elif 'blacklisted' in error.lower():
                stats['blacklisted'] += 1
                print(f"🚫 Blacklisted domain/email")
            else:
                stats['errors'] += 1
                print(f"⚠️  Error: {error}")
        
        # Show statistics every 50 records
        if stats['total_processed'] % 50 == 0:
            print(f"\n📈 Statistics Update:")
            print(f"   ✅ Valid: {stats['valid']} | ⚠️  Risky: {stats['risky']} | ❌ Not found: {stats['not_found']}")
            print(f"   🚫 Blacklisted: {stats['blacklisted']} | ⚠️  Errors: {stats['errors']}")
            print(f"   💰 Credits used: {stats['credits_used']} | 📊 Total processed: {stats['total_processed']}")
        
        # Rate limiting - 6 requests per minute (10 seconds between)
        if idx < total_profiles - 1:  # Don't sleep after last record
            time.sleep(10)
    
    # Save the final output
    output_filename = 'katy-followers-with-emails.csv'
    katy_filtered_df.to_csv(output_filename, index=False)
    
    # Final statistics
    total_time = (datetime.now() - start_time).total_seconds() / 60
    success_rate = (stats['valid'] + stats['risky']) / stats['total_processed'] * 100 if stats['total_processed'] > 0 else 0
    
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    print(f"✅ Valid emails found: {stats['valid']:,}")
    print(f"⚠️  Risky emails found: {stats['risky']:,}")
    print(f"❌ Emails not found: {stats['not_found']:,}")
    print(f"🚫 Blacklisted: {stats['blacklisted']:,}")
    print(f"⚠️  Errors: {stats['errors']:,}")
    print(f"📊 Total processed: {stats['total_processed']:,}")
    print(f"💰 Credits used: {stats['credits_used']:,}")
    print(f"📈 Success rate: {success_rate:.1f}%")
    print(f"⏱️  Total time: {total_time:.1f} minutes")
    print(f"\n✅ Results saved to: {output_filename}")
    
    return katy_filtered_df

if __name__ == "__main__":
    try:
        result_df = process_linkedin_profiles()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("Run the script again to start from the beginning")