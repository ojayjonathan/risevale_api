# /backup/Dockerfile
FROM google/cloud-sdk:slim

# Install bash, postgres client (pg_dump), and cron
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget gnupg lsb-release curl tzdata bash cron && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y postgresql-client-17 && \
    rm -rf /var/lib/apt/lists/*

# Set timezone (optional)
ENV TZ=Africa/Nairobi

# Copy service account key and scripts
COPY ./service-account.json /usr/local/bin/service-account.json
COPY ./backup_postgres.sh /usr/local/bin/backup_postgres.sh
COPY ./.env.backups /usr/local/bin/.env.backups
COPY crontab /etc/cron.d/db-backup

# Permissions
RUN chmod +x /usr/local/bin/backup_postgres.sh && chmod 0644 /etc/cron.d/db-backup

# Register cron job
RUN crontab /etc/cron.d/db-backup

# Create backup directory
RUN mkdir -p /var/backups/postgres

# Working directory
WORKDIR /app

# Run cron in foreground (keeps container alive)
CMD ["cron", "-f"]
