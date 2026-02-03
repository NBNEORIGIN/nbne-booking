#!/bin/bash
#
# NBNE Booking - Encrypted Database Backup Script
#
# This script creates encrypted PostgreSQL backups using age encryption.
# Backups are stored with timestamp and encrypted before storage.
#
# Requirements:
# - age (https://github.com/FiloSottile/age)
# - PostgreSQL client tools (pg_dump)
# - AGE_PUBLIC_KEY environment variable or key file
#
# Usage:
#   ./backup_database.sh
#
# Environment Variables:
#   AGE_PUBLIC_KEY - Public key for encryption (required)
#   BACKUP_DIR - Directory to store backups (default: /srv/backups)
#   POSTGRES_HOST - Database host (default: localhost)
#   POSTGRES_PORT - Database port (default: 5432)
#   POSTGRES_DB - Database name (default: nbne_main)
#   POSTGRES_USER - Database user (default: nbne_admin)
#   POSTGRES_PASSWORD - Database password (required)
#   RETENTION_DAYS - Days to keep backups (default: 30)

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/srv/backups}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-nbne_main}"
POSTGRES_USER="${POSTGRES_USER:-nbne_admin}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Timestamp for backup file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${POSTGRES_DB}_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.age"

# Check for required tools
if ! command -v pg_dump &> /dev/null; then
    echo "ERROR: pg_dump not found. Install PostgreSQL client tools."
    exit 1
fi

if ! command -v age &> /dev/null; then
    echo "ERROR: age not found. Install from https://github.com/FiloSottile/age"
    exit 1
fi

# Check for encryption key
if [ -z "${AGE_PUBLIC_KEY:-}" ]; then
    if [ -f "/srv/backups/backup_key.pub" ]; then
        AGE_PUBLIC_KEY=$(cat /srv/backups/backup_key.pub)
    else
        echo "ERROR: AGE_PUBLIC_KEY not set and /srv/backups/backup_key.pub not found"
        echo "Generate a key pair with: age-keygen -o backup_key.txt"
        exit 1
    fi
fi

# Check for password
if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    echo "ERROR: POSTGRES_PASSWORD not set"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Set restrictive permissions on backup directory
chmod 700 "${BACKUP_DIR}"

echo "Starting backup of ${POSTGRES_DB}..."
echo "Timestamp: ${TIMESTAMP}"

# Create PostgreSQL dump and encrypt in one pipeline
# This avoids storing unencrypted data on disk
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    2>&1 | tee >(age --encrypt --recipient "${AGE_PUBLIC_KEY}" --output "${BACKUP_DIR}/${ENCRYPTED_FILE}") | grep -v "^--" || true

# Verify encrypted file was created
if [ ! -f "${BACKUP_DIR}/${ENCRYPTED_FILE}" ]; then
    echo "ERROR: Encrypted backup file not created"
    exit 1
fi

# Get file size
FILE_SIZE=$(du -h "${BACKUP_DIR}/${ENCRYPTED_FILE}" | cut -f1)

echo "Backup completed successfully"
echo "File: ${BACKUP_DIR}/${ENCRYPTED_FILE}"
echo "Size: ${FILE_SIZE}"

# Set restrictive permissions on backup file
chmod 600 "${BACKUP_DIR}/${ENCRYPTED_FILE}"

# Clean up old backups (older than RETENTION_DAYS)
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "backup_*.sql.age" -type f -mtime +${RETENTION_DAYS} -delete

# Count remaining backups
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "backup_*.sql.age" -type f | wc -l)
echo "Total backups: ${BACKUP_COUNT}"

# Log backup completion
logger -t nbne-backup "Database backup completed: ${ENCRYPTED_FILE} (${FILE_SIZE})"

echo "Done!"
