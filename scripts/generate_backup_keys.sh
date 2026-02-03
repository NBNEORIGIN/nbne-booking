#!/bin/bash
#
# NBNE Booking - Generate Backup Encryption Keys
#
# This script generates age encryption key pair for database backups.
# Keys are stored securely with restrictive permissions.
#
# Requirements:
# - age (https://github.com/FiloSottile/age)
#
# Usage:
#   ./generate_backup_keys.sh

set -e

KEY_DIR="${1:-/srv/backups}"
SECRET_KEY_FILE="${KEY_DIR}/backup_key.txt"
PUBLIC_KEY_FILE="${KEY_DIR}/backup_key.pub"

# Check for age
if ! command -v age-keygen &> /dev/null; then
    echo "ERROR: age-keygen not found"
    echo "Install age from: https://github.com/FiloSottile/age"
    echo ""
    echo "On Ubuntu/Debian:"
    echo "  sudo apt install age"
    echo ""
    echo "On macOS:"
    echo "  brew install age"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "${KEY_DIR}"
chmod 700 "${KEY_DIR}"

# Check if keys already exist
if [ -f "${SECRET_KEY_FILE}" ]; then
    echo "WARNING: Secret key already exists: ${SECRET_KEY_FILE}"
    read -p "Overwrite? (yes/no): " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
fi

echo "Generating age key pair..."
echo "Location: ${KEY_DIR}"

# Generate key pair
age-keygen -o "${SECRET_KEY_FILE}" 2>&1 | tee /tmp/age_keygen_output.txt

# Extract public key from output
PUBLIC_KEY=$(grep "public key:" /tmp/age_keygen_output.txt | cut -d: -f2 | tr -d ' ')
echo "${PUBLIC_KEY}" > "${PUBLIC_KEY_FILE}"

# Clean up temp file
rm /tmp/age_keygen_output.txt

# Set restrictive permissions
chmod 600 "${SECRET_KEY_FILE}"
chmod 644 "${PUBLIC_KEY_FILE}"

echo ""
echo "✅ Keys generated successfully!"
echo ""
echo "Secret key: ${SECRET_KEY_FILE}"
echo "Public key: ${PUBLIC_KEY_FILE}"
echo ""
echo "Public key value: ${PUBLIC_KEY}"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Store the secret key securely (e.g., password manager, secrets vault)"
echo "2. Back up the secret key to a secure location"
echo "3. Never commit the secret key to version control"
echo "4. The secret key is required to restore backups"
echo ""
echo "To use in backup script:"
echo "  export AGE_PUBLIC_KEY=\"${PUBLIC_KEY}\""
echo ""
echo "To use in restore script:"
echo "  export AGE_SECRET_KEY=\"\$(cat ${SECRET_KEY_FILE})\""
