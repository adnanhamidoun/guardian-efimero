$i = 1
Get-Content -Raw -Path .\scripts\demo_setup.ps1 -ErrorAction Stop | ForEach-Object {
    $lines = $_ -split "\r?\n"
    foreach ($line in $lines) {
        if ($line -match "`\s+$") {
            Write-Host ('Line ' + $i + ': <' + $line + '>')
        }
        $i++
    }
}
Write-Host "Done"
