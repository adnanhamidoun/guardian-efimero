$lines = Get-Content -Path .\scripts\demo_setup.ps1 -ErrorAction Stop -Encoding UTF8
for ($i=0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    for ($j=0; $j -lt $line.Length; $j++) {
        $c = [int][char]$line[$j]
        if ($c -lt 32 -and $c -ne 9) {
            Write-Host "Line $($i+1) Char $($j+1): code $c"
        }
        if ($c -gt 127) {
            Write-Host "Line $($i+1) Char $($j+1): code $c (non-ascii)"
        }
    }
}
Write-Host "Scan complete"
