param(
  [Parameter(Mandatory = $true)][string]$OutPath,
  [switch]$Focus
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinCap {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$game = Get-Process -Name Cyberpunk2077 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $game) { Write-Output "NO_PROCESS"; exit 2 }
$script:hwnd = [IntPtr]::Zero
$script:area = 0
$script:rect = $null
[WinCap]::EnumWindows({
  param($h, $l)
  $proc = 0
  [void][WinCap]::GetWindowThreadProcessId($h, [ref]$proc)
  if ($proc -eq $game.Id -and [WinCap]::IsWindowVisible($h)) {
    $r = New-Object WinCap+RECT
    [void][WinCap]::GetWindowRect($h, [ref]$r)
    $w = $r.Right - $r.Left
    $hgt = $r.Bottom - $r.Top
    if (($w * $hgt) -gt $script:area) {
      $script:area = $w * $hgt
      $script:hwnd = $h
      $script:rect = $r
    }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
if ($script:hwnd -eq [IntPtr]::Zero) { Write-Output "NO_WINDOW"; exit 3 }
if ($Focus) {
  [WinCap]::ShowWindow($script:hwnd, 9) | Out-Null
  $fg = [WinCap]::GetForegroundWindow()
  $fgPid = 0
  $fgThread = [WinCap]::GetWindowThreadProcessId($fg, [ref]$fgPid)
  $thisThread = [WinCap]::GetCurrentThreadId()
  [WinCap]::AttachThreadInput($fgThread, $thisThread, $true) | Out-Null
  [WinCap]::SetForegroundWindow($script:hwnd) | Out-Null
  [WinCap]::AttachThreadInput($fgThread, $thisThread, $false) | Out-Null
  Start-Sleep -Milliseconds 400
  $r2 = New-Object WinCap+RECT
  [void][WinCap]::GetWindowRect($script:hwnd, [ref]$r2)
  $script:rect = $r2
}
$r = $script:rect
$w = $r.Right - $r.Left
$hgt = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $hgt
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $hgt))
$bmp.Save($OutPath)
$g.Dispose()
$bmp.Dispose()
Write-Output ("OK hwnd={0} {1}x{2} @{3},{4}" -f $script:hwnd, $w, $hgt, $r.Left, $r.Top)
