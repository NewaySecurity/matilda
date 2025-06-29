# PowerShell script to update the model name in .env file
$envPath = ".\.env"

# Check if .env exists
if (Test-Path $envPath) {
    # Read the current content
    $content = Get-Content $envPath

    # Replace the model line while preserving everything else
    $newContent = $content -replace "TOGETHER_MODEL=.*", "TOGETHER_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1"

    # Write the updated content back to the file
    $newContent | Set-Content $envPath

    Write-Host "✅ Updated model in .env file to: mistralai/Mixtral-8x7B-Instruct-v0.1"
} else {
    Write-Host "❌ .env file not found. Please run setup.py to create it."
}

