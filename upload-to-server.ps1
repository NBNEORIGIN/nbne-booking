# Upload files to server
# Run this from your local machine

$SERVER = "YOUR_SERVER_IP_HERE"  # Replace with your server IP
$USER = "root"
$DEST = "/srv/booking"

Write-Host "Uploading files to server..." -ForegroundColor Yellow

# Create directory on server
ssh ${USER}@${SERVER} "mkdir -p ${DEST}"

# Upload application files
Write-Host "Uploading application code..." -ForegroundColor Green
scp -r api/ ${USER}@${SERVER}:${DEST}/
scp -r alembic/ ${USER}@${SERVER}:${DEST}/
scp -r scripts/ ${USER}@${SERVER}:${DEST}/

# Upload configuration files
Write-Host "Uploading configuration..." -ForegroundColor Green
scp Dockerfile ${USER}@${SERVER}:${DEST}/
scp docker-compose.prod.yml ${USER}@${SERVER}:${DEST}/docker-compose.yml
scp Caddyfile ${USER}@${SERVER}:${DEST}/
scp alembic.ini ${USER}@${SERVER}:${DEST}/
scp .env.production ${USER}@${SERVER}:${DEST}/.env.example

Write-Host "Upload complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. SSH to server: ssh ${USER}@${SERVER}"
Write-Host "2. cd /srv/booking"
Write-Host "3. cp .env.example .env"
Write-Host "4. nano .env (edit with your values)"
Write-Host "5. docker compose up -d"
