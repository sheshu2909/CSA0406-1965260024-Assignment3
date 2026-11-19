param(
    [Parameter(Mandatory=$true)][string]$Title,
    [Parameter(Mandatory=$true)][string]$Script,      # Windows path to a .sh file
    [Parameter(Mandatory=$true)][string]$OutPath,     # Windows path to the .png
    [int]$WaitSeconds = 9,
    [int]$Cols = 126,
    [int]$Lines = 38,
    [string]$HideTitle = "Freebuff"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }

    public static IntPtr FindByTitle(string needle) {
        IntPtr found = IntPtr.Zero;
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (!IsWindowVisible(h)) return true;
            StringBuilder sb = new StringBuilder(512);
            GetWindowText(h, sb, 512);
            if (sb.ToString().IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) {
                found = h;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@

$base = "C:\Users\shesh\.config\freebuff-desktop\local-projects\360c0549-7338-4a84-9f3f-4d020779388d"
$bash = "D:\FREEBUFF\tools\msys64\usr\bin\bash.exe"
$conhost = Join-Path $env:WINDIR "System32\conhost.exe"

# --- make console windows opaque for the duration of the capture ---
$themeKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
$oldTransparency = $null
try {
    $oldTransparency = (Get-ItemProperty -Path $themeKey -Name EnableTransparency -ErrorAction Stop).EnableTransparency
    Set-ItemProperty -Path $themeKey -Name EnableTransparency -Value 0
    Start-Sleep -Milliseconds 700
} catch { $oldTransparency = $null }

try {
    $inner = 'mode con: cols=' + $Cols + ' lines=' + $Lines + ' >nul & title ' + $Title + ' & "' + $bash + '" -l "' + $Script + '"'
    $proc = Start-Process -FilePath $conhost -ArgumentList $env:COMSPEC, "/k", $inner -PassThru

    $hwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 300
        $hwnd = [Win32]::FindByTitle($Title)
        if ($hwnd -ne [IntPtr]::Zero) { break }
    }
    if ($hwnd -eq [IntPtr]::Zero) { throw "no visible window titled '$Title'" }

    Start-Sleep -Seconds $WaitSeconds
    # the app window overlaps the console; minimise it for the shot, restore after
    $bg = [IntPtr]::Zero
    if ($HideTitle) { $bg = [Win32]::FindByTitle($HideTitle) }
    if ($bg -ne [IntPtr]::Zero) { [Win32]::ShowWindow($bg, 6) | Out-Null; Start-Sleep -Milliseconds 1000 }

    [Win32]::ShowWindow($hwnd, 9) | Out-Null
    [Win32]::MoveWindow($hwnd, 150, 90, 1180, 720, $true) | Out-Null
    Start-Sleep -Milliseconds 800
    [Win32]::BringWindowToTop($hwnd) | Out-Null
    [Win32]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 1500

    $rect = New-Object Win32+RECT
    [Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    # Render the window's own surface: unaffected by anything drawn on top of it.
    $bmp = New-Object System.Drawing.Bitmap($width, $height)
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $gfx.GetHdc()
    $ok = [Win32]::PrintWindow($hwnd, $hdc, 2)     # PW_RENDERFULLCONTENT
    $gfx.ReleaseHdc($hdc)
    if (-not $ok) {
        $gfx.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($width, $height)))
    }
    $bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $gfx.Dispose()
    $bmp.Dispose()

    Write-Output ("captured {0} ({1}x{2})" -f (Split-Path $OutPath -Leaf), $width, $height)
}
finally {
    if ($bg -and $bg -ne [IntPtr]::Zero) { [Win32]::ShowWindow($bg, 9) | Out-Null }
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
    if ($oldTransparency -ne $null) {
        Set-ItemProperty -Path $themeKey -Name EnableTransparency -Value $oldTransparency
        Write-Output ("transparency restored to " + $oldTransparency)
    }
}
