# Sample script to install Python and pip under Windows
# Authors: Olivier Grisel, Jonathan Helmus and Kyle Kastner
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/

$BASE_URL = "https://www.python.org/ftp/python/"


function DownloadPython ($python_version, $platform_suffix) {
    $webclient = New-Object System.Net.WebClient
    $filename = "python-" + $python_version + $platform_suffix + ".msi"
    $url = $BASE_URL + $python_version + "/" + $filename

    $basedir = $pwd.Path + "\"
    $filepath = $basedir + $filename
    if (Test-Path $filename) {
        Write-Host "Reusing" $filepath
        return $filepath
    }

    # Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading" $filename "from" $url
    $retry_attempts = 2
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
   }
   if (Test-Path $filepath) {
       Write-Host "File saved at" $filepath
   } else {
       # Retry once to get the error message if any at the last try
       $webclient.DownloadFile($url, $filepath)
   }
   return $filepath
}


function InstallPython ($python_version, $architecture, $python_home) {
    Write-Host "Installing Python" $python_version "for" $architecture "bit architecture to" $python_home
    if (Test-Path $python_home) {
        Write-Host $python_home "already exists, skipping."
        return $false
    }
    if ($architecture -eq "32") {
        $platform_suffix = ""
    } else {
        $platform_suffix = ".amd64"
    }
    $msipath = DownloadPython $python_version $platform_suffix
    Write-Host "Installing" $msipath "to" $python_home
    $install_log = $python_home + ".log"
    $install_args = "/qn /log $install_log /i $msipath TARGETDIR=$python_home"
    $uninstall_args = "/qn /x $msipath"
    RunCommand "msiexec.exe" $install_args
    if (-not(Test-Path $python_home)) {
        Write-Host "Python seems to be installed else-where, reinstalling."
        RunCommand "msiexec.exe" $uninstall_args
        RunCommand "msiexec.exe" $install_args
    }
    if (Test-Path $python_home) {
        Write-Host "Python $python_version ($architecture) installation complete"
    } else {
        Write-Host "Failed to install Python in $python_home"
        Get-Content -Path $install_log
        Exit 1
    }
}

function RunCommand ($command, $command_args) {
    Write-Host $command $command_args
    Start-Process -FilePath $command -ArgumentList $command_args -Wait -Passthru
}


function main () {
    InstallPython $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON_DIR
}

main
