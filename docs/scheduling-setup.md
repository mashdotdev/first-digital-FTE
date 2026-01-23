# Scheduling Setup for Digital FTE

This document explains how to set up OS-level scheduling for the Digital FTE to run automatically.

## Windows Task Scheduler

### 1. Create Basic Task

1. Open Task Scheduler (search "Task Scheduler" in Start menu)
2. Click "Create Basic Task" in the right panel
3. Name: "Digital FTE Orchestrator"
4. Description: "Runs the AI Employee orchestrator"

### 2. Trigger Configuration

**For Always-On Operation:**
- Trigger: "When the computer starts"
- Also add: "At log on" as backup trigger

**For Scheduled Checks:**
- Trigger: "Daily"
- Start time: 8:00 AM
- Recur every: 1 day

### 3. Action Configuration

- Action: "Start a program"
- Program/script: `C:\path\to\python.exe` (or `uv.exe`)
- Arguments: `-m digital_fte start`
- Start in: `A:\Desktop\first-digital-FTE`

**Full command example:**
```
Program: C:\Users\YourName\.local\bin\uv.exe
Arguments: run digital-fte start
Start in: A:\Desktop\first-digital-FTE
```

### 4. Conditions

- [ ] Start only if computer is on AC power (uncheck for laptops)
- [x] Wake the computer to run this task (optional)
- [ ] Start only if network connection is available (recommended)

### 5. Settings

- [x] Allow task to be run on demand
- [x] Run task as soon as possible after scheduled start is missed
- [x] If task fails, restart every: 5 minutes
- [x] Attempt to restart up to: 3 times
- [x] Stop task if it runs longer than: 3 days (set high or disable)

---

## Linux/macOS (cron)

### Basic Crontab Setup

```bash
# Edit crontab
crontab -e

# Add these lines:

# Run orchestrator every 5 minutes (checks if running)
*/5 * * * * cd /path/to/first-digital-FTE && /usr/bin/uv run digital-fte start >> /var/log/digital-fte.log 2>&1

# CEO Briefing every Monday at 6 AM
0 6 * * 1 cd /path/to/first-digital-FTE && /usr/bin/uv run digital-fte briefing >> /var/log/digital-fte-briefing.log 2>&1
```

### Using systemd (Recommended for Linux)

Create `/etc/systemd/system/digital-fte.service`:

```ini
[Unit]
Description=Digital FTE AI Employee
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/first-digital-FTE
ExecStart=/usr/bin/uv run digital-fte start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable digital-fte
sudo systemctl start digital-fte
sudo systemctl status digital-fte
```

---

## PM2 (Cross-Platform)

### Installation

```bash
npm install -g pm2
```

### Start Digital FTE

```bash
cd A:\Desktop\first-digital-FTE

# Start with PM2
pm2 start "uv run digital-fte start" --name digital-fte

# Save process list
pm2 save

# Set up startup script (run on boot)
pm2 startup
```

### PM2 Commands

```bash
pm2 status          # Check status
pm2 logs digital-fte  # View logs
pm2 restart digital-fte  # Restart
pm2 stop digital-fte    # Stop
pm2 delete digital-fte  # Remove
```

---

## Scheduled Tasks Overview

| Task | Schedule | Command |
|------|----------|---------|
| Orchestrator | Always running | `digital-fte start` |
| CEO Briefing | Monday 6 AM | `digital-fte briefing` |
| Health Check | Every 5 min | `digital-fte status` |
| LinkedIn Post | Tue/Wed/Thu 9 AM | Handled by orchestrator |

---

## Verification

After setting up scheduling:

1. **Check Task is Running**
   ```bash
   digital-fte status
   ```

2. **Check Logs**
   - Windows: `AI_Employee_Valut\Logs\`
   - Linux: `/var/log/digital-fte.log`

3. **Test Manual Trigger**
   - Windows: Right-click task → Run
   - Linux: `systemctl start digital-fte`

4. **Verify Auto-Start**
   - Reboot computer
   - Check if orchestrator starts automatically
   - Check Dashboard.md for activity
