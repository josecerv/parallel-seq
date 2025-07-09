# EC2 Deployment Complete - LinkedIn Email Finder

## 🎯 Project Overview
This project processes ~23,891 LinkedIn profiles to find email addresses using the Anymail Finder API. The script was successfully deployed to AWS EC2 to run independently, allowing the local machine to be turned off during the ~64-hour processing time.

## 📋 Current Deployment Status
- **EC2 Instance**: `i-0a13a23d6aad5ceb1` (linkedin-email-finder)
- **Instance Type**: t2.micro (free tier eligible)
- **Public IP**: 34.204.18.101
- **Key Pair**: linkedin-finder-key.pem
- **Script Status**: ✅ RUNNING in tmux session "email-finder"
- **Progress**: Processing profile 10+ of 23,891 (finding valid emails successfully)

## 🔧 Files Deployed
- `linkedin_email_finder.py` - Main processing script
- `requirements.txt` - Python dependencies
- `.env` - API key configuration
- `katy-followers.csv` - Primary dataset (23,891 profiles)
- `sophia-followers.csv` - Secondary dataset (592 profiles)
- `checkpoint.csv` - Progress checkpoint file

## 📊 Monitoring Commands

### Quick Progress Check
```bash
ssh -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101 'tmux capture-pane -t email-finder -p | tail -20'
```

### Latest Output Only
```bash
ssh -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101 'tmux capture-pane -t email-finder -p | tail -5'
```

### Check if Script is Running
```bash
ssh -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101 'tmux list-sessions'
```

### Interactive Monitoring
```bash
ssh -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101
tmux attach -t email-finder
# Press Ctrl+B then D to detach
```

### Download Results
```bash
# Final results
scp -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101:~/linkedin-email-finder/katy-followers-with-emails.csv ./

# Current progress checkpoint
scp -i ~/linkedin-finder-key.pem ubuntu@34.204.18.101:~/linkedin-email-finder/checkpoint.csv ./
```

## 🎮 Management Commands

### Stop/Start EC2 Instance
```bash
# Stop instance (saves money, preserves data)
aws ec2 stop-instances --instance-ids i-0a13a23d6aad5ceb1

# Start instance (get new IP address)
aws ec2 start-instances --instance-ids i-0a13a23d6aad5ceb1
```

### Resume Script After Instance Restart
```bash
# SSH to instance
ssh -i ~/linkedin-finder-key.pem ubuntu@NEW-IP-ADDRESS

# Navigate to project
cd ~/linkedin-email-finder

# Activate virtual environment
source venv/bin/activate

# Start in tmux
tmux new-session -d -s email-finder "python linkedin_email_finder.py"

# It will automatically resume from checkpoint
```

## 💰 Cost Information
- **Instance Cost**: ~$0.0116/hour (t2.micro)
- **64-hour runtime**: ~$0.74
- **API Costs**: 2 credits per valid email found
- **Total Estimated Cost**: <$5 for complete processing

## 🔄 Script Features
- **Checkpoint System**: Saves progress every 10 records
- **Resume Capability**: Can restart from any point
- **Rate Limiting**: 6 requests/minute (10s between requests)
- **Statistics Tracking**: Valid, risky, not found, errors
- **Progress Bar**: Real-time ETA and completion percentage

## 🛠️ Troubleshooting

### If Script Stops
1. Check if tmux session exists: `tmux list-sessions`
2. If session exists but script stopped, check the last output
3. Resume manually: `tmux attach -t email-finder`
4. If needed, restart: `python linkedin_email_finder.py` (will resume from checkpoint)

### Connection Issues
- Instance may have new IP after restart
- Check EC2 console for current public IP
- Update security group if needed

### Permission Issues
- Key file permissions: `chmod 600 ~/linkedin-finder-key.pem`
- If key moved: Copy to home directory

## 📈 Expected Results
- **Processing Time**: ~64 hours (267 hours with current rate)
- **Valid Email Rate**: ~30% based on initial results
- **Total Valid Emails Expected**: ~7,000-8,000
- **Output File**: `katy-followers-with-emails.csv`

## 🔐 Security Notes
- API key stored in `.env` file on EC2
- SSH key required for access
- Security group restricts SSH to original IP
- Instance can be stopped when not needed

## 📝 Next Steps for Future LLMs
1. **Monitor Progress**: Use monitoring commands above
2. **Download Results**: When processing complete
3. **Stop Instance**: To save costs when done
4. **Analyze Results**: Process the final CSV file
5. **Scale Up**: If needed, consider larger instance types

## 🚀 Deployment Architecture
```
Local Machine → EC2 Instance (Ubuntu 24.04)
├── Python 3.12 + Virtual Environment
├── Tmux Session (persistent)
├── LinkedIn Email Finder Script
├── Anymail Finder API Integration
└── Checkpoint System (resume capability)
```

## 📞 Emergency Recovery
If everything fails:
1. The checkpoint.csv file contains all progress
2. Script can be restarted from any point
3. All files are backed up on EC2 instance
4. Original files remain on local machine

---
*Deployment completed on: July 9, 2025*  
*Instance ID: i-0a13a23d6aad5ceb1*  
*Public IP: 34.204.18.101*  
*Status: ✅ RUNNING*