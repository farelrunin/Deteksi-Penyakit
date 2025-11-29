# Script untuk membuat ZIP file untuk submission tugas
# Gunakan script ini untuk membuat Deteksi-Penyakit.zip

# Cara penggunaan:
# 1. Buka PowerShell
# 2. Pindah ke folder SEMESTER 5:
#    cd 'C:\Users\ASUS\Documents\SEMESTER 5\Sistem Pendukung Keputusan'
# 3. Jalankan script:
#    powershell -ExecutionPolicy Bypass -File create_submission_zip.ps1
# 4. File ZIP akan dibuat: Deteksi-Penyakit.zip

# Define paths
$sourceFolder = 'C:\Users\ASUS\Documents\SEMESTER 5\Sistem Pendukung Keputusan\project'
$zipPath = 'C:\Users\ASUS\Documents\SEMESTER 5\Sistem Pendukung Keputusan\Deteksi-Penyakit.zip'

# Remove old ZIP if exists
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
    Write-Host "Old ZIP file removed."
}

# Create ZIP
Write-Host "Creating ZIP file: $zipPath"
Write-Host "Source folder: $sourceFolder"

Compress-Archive -Path $sourceFolder -DestinationPath $zipPath -Force

# Get file size
$fileSize = (Get-Item $zipPath).Length / 1MB
Write-Host "✅ ZIP created successfully!"
Write-Host "File size: $([Math]::Round($fileSize, 2)) MB"
Write-Host "Location: $zipPath"
Write-Host ""
Write-Host "Ready to upload to assignment submission page!"
