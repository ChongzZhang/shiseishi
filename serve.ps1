$Port = 8766
$Public = $args[0] -eq "-Public"
$Root = $PSScriptRoot
Set-Location $Root

Write-Host ""
Write-Host "  色谱寻诗 - Local Server"
Write-Host "  http://127.0.0.1:${Port}/"
Write-Host ""

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback" -and $_.PrefixOrigin -ne "WellKnown" } | Select-Object -First 1).IPAddress
if ($ip) {
    Write-Host "  局域网访问: http://${ip}:${Port}/"
    Write-Host ""
}

if ($Public) {
    python _serve_public.py
    exit
}

Write-Host "Press Ctrl+C to stop"
python _serve.py
