
# PowerShell script to repair Python 3.13 installation
Write-Host "Attempting to repair Python 3.13 installation..." -ForegroundColor Cyan

# Search for Python 3.13 in registry
$pythonReg = Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | 
    Where-Object { $_.GetValue("DisplayName") -like "*Python 3.13*" }

if (-not $pythonReg) {
    $pythonReg = Get-ChildItem "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | 
        Where-Object { $_.GetValue("DisplayName") -like "*Python 3.13*" }
}

if (-not $pythonReg) {
    Write-Host "Python 3.13 not found in registry" -ForegroundColor Red
    Write-Host "Please reinstall Python 3.13 from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$pythonPath = $pythonReg.GetValue("InstallLocation")
if (-not $pythonPath) {
    $pythonPath = "C:\Program Files\Python313"
}

Write-Host "Found Python at: $pythonPath" -ForegroundColor Green

# Try to run repair using the Python installer
Write-Host "Attempting Windows repair..." -ForegroundColor Yellow

# Get the installer from registry
$pythonReg = Get-ChildItem "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | 
    Where-Object { $_.GetValue("DisplayName") -like "*Python*3.13*" }

if ($pythonReg) {
    Write-Host "Found Python 3.13 in registry" -ForegroundColor Green
    
    # Try online repair (most thorough)
    Write-Host "Running Python 3.13 repair (this may take a minute)..." -ForegroundColor Cyan
    
    # Use msiexec to repair (works for MSI installations)
    $uninstallString = $pythonReg.GetValue("UninstallString")
    Write-Host "Uninstall string: $uninstallString" -ForegroundColor Gray
    
    if ($uninstallString -like "*msiexec*") {
        # Extract the product code
        $productCode = ($uninstallString | Select-String -Pattern '{[A-F0-9\-]+}' -AllMatches).Matches[0].Value
        
        if ($productCode) {
            Write-Host "Repairing Python using product code: $productCode" -ForegroundColor Yellow
            
            # Run repair
            Start-Process msiexec.exe -ArgumentList "/f $productCode" -Wait -NoNewWindow
            
            Write-Host "Repair completed!" -ForegroundColor Green
        }
    }
}

# Test if Tcl/Tkinter now works
Write-Host "`nTesting Tcl/Tkinter installation..." -ForegroundColor Cyan
$testResult = python -c "import tkinter; print('Tcl/Tkinter is working!')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! Tkinter is now available." -ForegroundColor Green
} else {
    Write-Host "Tcl/Tkinter still not working. Please reinstall Python manually." -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Green
