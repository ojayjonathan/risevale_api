#!/bin/bash
# -------------------------------------------
# PostgreSQL → Google Cloud Storage Backup Script
# -------------------------------------------

set -e  # stop on first error

# === Load environment variables ===
ENV_FILE="/usr/local/bin/.env.backups"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Missing environment file: $ENV_FILE"
  exit 1
fi

echo "🔧 Loading environment from $ENV_FILE"
set -a
source "$ENV_FILE"
set +a

# === Prepare variables ===
TIMESTAMP=$(date +'%Y-%m-%d_%H-%M')
BACKUP_FILE="${BACKUP_DIR}/${BACKUPS_DB}_${TIMESTAMP}.sql"
GCS_BUCKET="gs://${BACKUPS_GCS_BUCKET}"

mkdir -p "$BACKUP_DIR"

echo "📦 Starting PostgreSQL backup for database: $BACKUPS_DB"

# === Dump database from container ===
PGPASSWORD="$BACKUPS_PASSWORD" pg_dump \
  -h "$CONTAINER_NAME" \
  -U "$BACKUPS_USER" \
  -d "$BACKUPS_DB" \
  -F p \
  --no-password \
  > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Backup created: $BACKUP_FILE"
else
  echo "❌ pg_dump failed!"
  exit 1
fi

# === Compress backup ===
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"
echo "🗜️  Compressed: $BACKUP_FILE"

# === Upload to GCS ===
if [ -f "$GCS_KEY_PATH" ]; then
  echo "☁️  Authenticating to Google Cloud..."
  gcloud auth activate-service-account --key-file="$GCS_KEY_PATH"

  echo "⬆️  Uploading to $GCS_BUCKET ..."
  gsutil cp "$BACKUP_FILE" "$GCS_BUCKET"/

  echo "✅ Upload complete."
else
  echo "⚠️  GCS key file not found at $GCS_KEY_PATH — skipping upload."
fi

# === Cleanup old backups (> 7 days) ===
find "$BACKUP_DIR" -type f -name "${BACKUPS_DB}_*.sql.gz" -mtime +7 -delete
echo "🧹 Cleaned backups older than 7 days"

echo "✅ Backup completed at $(date)"
