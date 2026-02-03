#!/bin/bash
#
# NBNE Booking - Encrypted Database Restore Script
#
# This script restores a PostgreSQL database from an encrypted backup.
# WARNING: This will DROP and recreate the database!
#
# Requirements:
# - age (https://github.com/FiloSottile/age)
# - PostgreSQL client tools (psql, dropdb, createdb)
# - AGE_SECRET_KEY environment variable or key file
#
# Usage:
#   ./restore_database.sh <backup_file.sql.age>
#
# Environment Variables:
#   AGE_SECRET_KEY - Secret key for decryption (required)
#   POSTGRES_HOST - Database host (default: localhost)
#   POSTGRES_PORT - Database port (default: 5432)
#   POSTGRES_DB - Database name (default: nbne_main)
#   POSTGRES_USER - Database user (default: nbne_admin)
#   POSTGRES_PASSWORD - Database password (required)

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-nbne_main}"
POSTGRES_USER="${POSTGRES_USER:-nbne_admin}"

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file.sql.age>"
    echo ""
    echo "Example:"
    echo "  $0 /srv/backups/backup_nbne_main_20260203_120000.sql.age"
    exit 1
fi

BACKUP_FILE="$1"

# Check for required tools
if ! command -v psql &> /dev/null; then
    echo "ERROR: psql not found. Install PostgreSQL client tools."
    exit 1
fi

if ! command -v age &> /dev/null; then
    echo "ERROR: age not found. Install from https://github.com/FiloSottile/age"
    exit 1
fi

# Check backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Check for decryption key
if [ -z "${AGE_SECRET_KEY:-}" ]; then
    if [ -f "/srv/backups/backup_key.txt" ]; then
        AGE_SECRET_KEY_FILE="/srv/backups/backup_key.txt"
    else
        echo "ERROR: AGE_SECRET_KEY not set and /srv/backups/backup_key.txt not found"
        exit 1
    fi
fi

# Check for password
if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    echo "ERROR: POSTGRES_PASSWORD not set"
    exit 1
fi

# Confirm restore
echo "WARNING: This will DROP and recreate the database: ${POSTGRES_DB}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "Starting restore..."

# Drop existing database
echo "Dropping existing database..."
PGPASSWORD="${POSTGRES_PASSWORD}" dropdb \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --if-exists \
    "${POSTGRES_DB}" || true

# Create new database
echo "Creating new database..."
PGPASSWORD="${POSTGRES_PASSWORD}" createdb \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --owner="${POSTGRES_USER}" \
    "${POSTGRES_DB}"

# Decrypt and restore in one pipeline
echo "Decrypting and restoring backup..."
if [ -n "${AGE_SECRET_KEY:-}" ]; then
    # Use secret key from environment
    echo "${AGE_SECRET_KEY}" | age --decrypt --identity - "${BACKUP_FILE}" | \
        PGPASSWORD="${POSTGRES_PASSWORD}" psql \
            --host="${POSTGRES_HOST}" \
            --port="${POSTGRES_PORT}" \
            --username="${POSTGRES_USER}" \
            --dbname="${POSTGRES_DB}" \
            --quiet
else
    # Use secret key from file
    age --decrypt --identity "${AGE_SECRET_KEY_FILE}" "${BACKUP_FILE}" | \
        PGPASSWORD="${POSTGRES_PASSWORD}" psql \
            --host="${POSTGRES_HOST}" \
            --port="${POSTGRES_PORT}" \
            --username="${POSTGRES_USER}" \
            --dbname="${POSTGRES_DB}" \
            --quiet
fi

# Verify restore
echo "Verifying restore..."
TABLE_COUNT=$(PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --tuples-only \
    --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

echo "Restore completed successfully"
echo "Tables restored: ${TABLE_COUNT}"

# Log restore completion
logger -t nbne-restore "Database restore completed from: ${BACKUP_FILE}"

echo "Done!"
