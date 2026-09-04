[CmdletBinding()]
param (
    [Parameter(Mandatory=$true, HelpMessage="Your Alpaca API Key ID (e.g. PK...)")]
    [string]$ApiKey,

    [Parameter(Mandatory=$true, HelpMessage="Your Alpaca Secret Key")]
    [string]$SecretKey,

    [Parameter(Mandatory=$false)]
    [switch]$Live = $false
)

$isPaper = (-not $Live).ToString().ToLower()
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURING ALPACA CREDENTIALS ACROSS ALL SYSTEMS   " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Live) { 'LIVE TRADING' } else { 'PAPER TRADING (Safe)' })" -ForegroundColor Yellow

# 1. Update mcp_config.json
$mcpConfigPath = "$env:USERPROFILE\.gemini\config\mcp_config.json"
if (Test-Path $mcpConfigPath) {
    try {
        $json = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
        if (-not $json.mcpServers) { $json | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value ([PSCustomObject]@{}) }
        
        $json.mcpServers.alpaca = [PSCustomObject]@{
            command = "C:\Users\sysyo\go\bin\uvx.exe"
            args = @("alpaca-mcp-server")
            env = [PSCustomObject]@{
                ALPACA_API_KEY = $ApiKey
                ALPACA_SECRET_KEY = $SecretKey
                ALPACA_PAPER_TRADE = $isPaper
            }
        }
        $json | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath -Encoding UTF8
        Write-Host "  [1/3] Updated MCP config at: $mcpConfigPath" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Failed to update mcp_config.json: $_" -ForegroundColor Red
    }
}

# 2. Update User Environment Variables
try {
    [System.Environment]::SetEnvironmentVariable('ALPACA_API_KEY', $ApiKey, 'User')
    [System.Environment]::SetEnvironmentVariable('ALPACA_SECRET_KEY', $SecretKey, 'User')
    [System.Environment]::SetEnvironmentVariable('APCA_API_KEY_ID', $ApiKey, 'User')
    [System.Environment]::SetEnvironmentVariable('APCA_API_SECRET_KEY', $SecretKey, 'User')
    [System.Environment]::SetEnvironmentVariable('ALPACA_PAPER_TRADE', $isPaper, 'User')
    Write-Host "  [2/3] Saved Windows User environment variables." -ForegroundColor Green
} catch {
    Write-Host "  [!] Failed to set environment variables: $_" -ForegroundColor Red
}

# 3. Configure Alpaca CLI Profile
$alpacaCli = "C:\Users\sysyo\go\bin\alpaca.exe"
if (Test-Path $alpacaCli) {
    try {
        if ($Live) {
            & $alpacaCli profile login --api-key --live --name live --key $ApiKey --secret $SecretKey
            Write-Host "  [3/3] Configured Alpaca CLI 'live' profile." -ForegroundColor Green
        } else {
            & $alpacaCli profile login --api-key --paper --name paper --key $ApiKey --secret $SecretKey
            Write-Host "  [3/3] Configured Alpaca CLI 'paper' profile." -ForegroundColor Green
        }
    } catch {
        Write-Host "  [!] Failed to configure CLI profile: $_" -ForegroundColor Red
    }
}

Write-Host "`nAll credentials synchronized successfully!" -ForegroundColor Cyan
Write-Host "Testing account connectivity..." -ForegroundColor Yellow
& $alpacaCli account get --quiet
