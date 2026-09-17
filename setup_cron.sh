#!/bin/bash
# Sets up cron jobs for CareerBot reminders.
# Run once: bash setup_cron.sh

PYTHON="$HOME/career-bot/.venv/bin/python"
BOT="$HOME/career-bot/bot.py"

# Remove old CareerBot cron entries if any
crontab -l 2>/dev/null | grep -v "career-bot" > /tmp/crontab_clean.txt

# Add new entries
cat >> /tmp/crontab_clean.txt << EOF
# CareerBot — DSA reminder at 6:00 AM every day
0 6 * * * $PYTHON $BOT remind morning >> $HOME/.career-bot/cron.log 2>&1

# CareerBot — evening study reminder at 8:00 PM every day
0 20 * * * $PYTHON $BOT remind evening >> $HOME/.career-bot/cron.log 2>&1

# CareerBot — Sunday weekly review at 7:00 PM
0 19 * * 0 $PYTHON $BOT remind weekly >> $HOME/.career-bot/cron.log 2>&1
EOF

crontab /tmp/crontab_clean.txt
rm /tmp/crontab_clean.txt

echo "Cron jobs installed:"
crontab -l | grep "career-bot"
echo ""
echo "Reminders will fire at:"
echo "  6:00 AM daily  — morning DSA reminder"
echo "  8:00 PM daily  — evening study reminder"
echo "  7:00 PM Sunday — weekly review reminder"
echo ""
echo "Logs at: ~/.career-bot/cron.log"
