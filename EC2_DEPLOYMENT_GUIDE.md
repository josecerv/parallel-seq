# EC2 Deployment Guide for LinkedIn Email Finder

## Quick Start (AWS EC2)

### 1. Launch EC2 Instance
- **Instance Type**: t2.micro (free tier) or t3.micro
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 8-10 GB (default is fine)
- **Security Group**: Allow SSH (port 22) from your IP

### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Transfer Files
From your local machine:
```bash
scp -i your-key.pem linkedin_email_finder.py requirements.txt .env katy-followers.csv sophia-followers.csv ubuntu@your-ec2-ip:~/
```

### 4. Run Deployment Script
```bash
wget https://raw.githubusercontent.com/YOUR_REPO/deploy_to_ec2.sh
chmod +x deploy_to_ec2.sh
./deploy_to_ec2.sh
```

### 5. Start Processing in tmux
```bash
tmux new -s email-finder
source venv/bin/activate
python linkedin_email_finder.py
# Press Ctrl+B then D to detach
```

### 6. Monitor Progress
```bash
tmux attach -t email-finder  # Reattach to see progress
```

### 7. Download Results
```bash
scp -i your-key.pem ubuntu@your-ec2-ip:~/katy-followers-with-emails.csv ./
```

## Cost Optimization

### AWS EC2 Costs
- **t2.micro**: ~$0.0116/hour ($8.35/month)
- **64 hours runtime**: ~$0.74

### Alternative Cloud Providers

#### 1. **Google Cloud (Free Tier)**
- e2-micro: Free for 720 hours/month
- Perfect for this use case!

#### 2. **DigitalOcean**
- Basic Droplet: $6/month
- Simpler interface than AWS

#### 3. **Vultr**
- $3.50/month for basic VPS
- Good performance/price ratio

#### 4. **Oracle Cloud (Always Free)**
- 2 AMD-based VMs free forever
- Best free option!

## Performance Optimization

### 1. Use Parallel Processing
Modify the script to process multiple profiles concurrently (respecting API limits):
```python
# Add concurrent processing with threading
from concurrent.futures import ThreadPoolExecutor
import threading

# Process 6 profiles per minute in parallel
```

### 2. Use Spot Instances (70-90% cheaper)
```bash
# AWS CLI command for spot instance
aws ec2 request-spot-instances --spot-price "0.003" --instance-count 1 --type "one-time" --launch-specification file://spot-spec.json
```

### 3. Auto-shutdown Script
Add to your script to avoid forgotten instances:
```python
import subprocess
# After completion
subprocess.run(['sudo', 'shutdown', '-h', 'now'])
```

## Monitoring

### Check Progress Remotely
```bash
# SSH and check
ssh -i your-key.pem ubuntu@your-ec2-ip "tail -f ~/linkedin-email-finder.log"
```

### Set Up Email Notifications
```python
# Add to script
import smtplib
def send_completion_email():
    # Send email when done
```

## Troubleshooting

### If Instance Stops
- Check if using spot instance (may be terminated)
- Verify checkpoint.csv was saved
- Resume from checkpoint when restarting

### Memory Issues
- Upgrade to t3.small if needed
- Process in smaller batches

### Connection Issues
- Use elastic IP for consistent access
- Configure security group properly

## Best Practices

1. **Always use tmux/screen** for long-running processes
2. **Set up auto-shutdown** to avoid surprise bills
3. **Use checkpoint system** for resilience
4. **Monitor API credits** to avoid overspending
5. **Download results regularly** in case of issues

## Quick Commands Reference

```bash
# Start processing
tmux new -s email-finder
python linkedin_email_finder.py

# Check progress
tmux attach -t email-finder

# Download results
scp -i key.pem ubuntu@ip:~/katy-followers-with-emails.csv ./

# Stop instance (save money)
aws ec2 stop-instances --instance-ids i-xxxxx
```