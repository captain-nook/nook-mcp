param(
    [string]$ImagineUrl = "",
    [string]$ImagineKey = "",
    [ValidateSet("none", "codex")]
    [string]$Agent = "none"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host ""
Write-Host "=== Nook Image MCP setup ==="
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH. Install Python 3.10+ first, then rerun this script."
}

Write-Host "[1/4] Installing Python dependencies..."
python -m pip install -r "$Root\requirements.txt"

$envPath = Join-Path $Root ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Write-Host "[2/4] Creating .env..."
    if ([string]::IsNullOrWhiteSpace($ImagineUrl)) {
        $ImagineUrl = Read-Host "IMAGINE_URL"
    }
    if ([string]::IsNullOrWhiteSpace($ImagineKey)) {
        $secureKey = Read-Host "IMAGINE_KEY" -AsSecureString
        $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
        try {
            $ImagineKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        }
        finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }

    if ([string]::IsNullOrWhiteSpace($ImagineUrl) -or [string]::IsNullOrWhiteSpace($ImagineKey)) {
        throw "IMAGINE_URL and IMAGINE_KEY are required."
    }

    @(
        "IMAGINE_URL=$ImagineUrl"
        "IMAGINE_KEY=$ImagineKey"
    ) | Set-Content -LiteralPath $envPath -Encoding UTF8
    Write-Host "    .env created."
}
else {
    Write-Host "[2/4] .env already exists, keeping it."
}

Write-Host "[3/4] Testing MCP server import..."
python -c "import server; print('    server import ok')"

if ($Agent -eq "codex") {
    Write-Host "[4/4] Registering MCP server in Codex config..."
    $codexDir = Join-Path $HOME ".codex"
    $configPath = Join-Path $codexDir "config.toml"
    New-Item -ItemType Directory -Force -Path $codexDir | Out-Null
    if (-not (Test-Path -LiteralPath $configPath)) {
        New-Item -ItemType File -Force -Path $configPath | Out-Null
    }

    $pythonPath = (Get-Command python).Source
    $serverPath = Join-Path $Root "server.py"
    $existing = Get-Content -Raw -Encoding UTF8 -LiteralPath $configPath

    $block = @"

[mcp_servers.nook-image-mcp]
command = '$pythonPath'
args = ['$serverPath']
"@

    if ($existing -match "(?m)^\[mcp_servers\.nook-image-mcp\]") {
        Write-Host "    nook-image-mcp already exists in Codex config. Leaving config unchanged."
    }
    else {
        Add-Content -LiteralPath $configPath -Encoding UTF8 -Value $block
        Write-Host "    Codex config updated: $configPath"
    }
}
else {
    Write-Host "[4/4] Agent config snippets"
    $pythonPath = (Get-Command python).Source
    $serverPath = Join-Path $Root "server.py"
    $pythonJson = $pythonPath.Replace("\", "\\")
    $serverJson = $serverPath.Replace("\", "\\")

    Write-Host ""
    Write-Host "Claude Code / Cursor:"
    Write-Host @"
{
  "mcpServers": {
    "nook-image-mcp": {
      "command": "$pythonJson",
      "args": ["$serverJson"]
    }
  }
}
"@

    Write-Host ""
    Write-Host "OpenCode:"
    Write-Host @"
{
  "`$schema": "https://opencode.ai/config.json",
  "mcp": {
    "nook-image-mcp": {
      "type": "local",
      "command": ["$pythonJson", "$serverJson"],
      "enabled": true
    }
  }
}
"@

    Write-Host ""
    Write-Host "Codex TOML:"
    Write-Host @"
[mcp_servers.nook-image-mcp]
command = '$pythonPath'
args = ['$serverPath']
"@
}

Write-Host ""
Write-Host "Done. Add the matching snippet to your Agent config, then restart that Agent."

