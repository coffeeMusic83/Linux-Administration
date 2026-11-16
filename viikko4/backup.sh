#!/usr/bin/env bash
# Week 4 – Hourly backup of server A's /var/www/html to server B
set -euo pipefail

REMOTE_USER="webbackup"
REMOTE_HOST="192.168.1.64"          # server B, private network
REMOTE_DIR="/srv/backups/server-a"
SSH_KEY="/home/ubuntu/.ssh/backup_to_b"
KEEP=48                              # keep the newest 48 backups (2 days)
LOG_FILE="/home/ubuntu/backup-logs/backup.log"

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
ARCHIVE="html-$TIMESTAMP.tar.gz"
SSH="ssh -i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=10 $REMOTE_USER@$REMOTE_HOST"

mkdir -p "$(dirname "$LOG_FILE")"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"; }

# Pack /var/www/html and stream it to B over SSH.
# The file is first written as .part and renamed only if the transfer succeeds.
if tar -czf - -C /var/www --exclude='.index.*' --warning=no-file-changed html 2>>"$LOG_FILE" \
   | $SSH "umask 077; cat > '$REMOTE_DIR/$ARCHIVE.part' && mv '$REMOTE_DIR/$ARCHIVE.part' '$REMOTE_DIR/$ARCHIVE'"
then
    log "SUCCESS $ARCHIVE"
    # Remove old backups, keep the newest $KEEP
    $SSH "cd '$REMOTE_DIR' && ls -1t html-*.tar.gz | tail -n +$((KEEP + 1)) | xargs -r rm --"
else
    log "FAILED  $ARCHIVE"
    exit 1
fi


