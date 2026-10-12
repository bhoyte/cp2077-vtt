param(
  [Parameter(Mandatory = $true)][int]$X,
  [Parameter(Mandatory = $true)][int]$Y
)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ClickAt {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$game = Get-Process -Name Cyberpunk2077 | Select-Object -First 1
$script:hwnd = [IntPtr]::Zero
$script:area = 0
$script:left = 0
$script:top = 0
[ClickAt]::EnumWindows({
  param($h, $l)
  $proc = 0
  [void][ClickAt]::GetWindowThreadProcessId($h, [ref]$proc)
  if ($proc -eq $game.Id -and [ClickAt]::IsWindowVisible($h)) {
    $r = New-Object ClickAt+RECT
    [void][ClickAt]::GetWindowRect($h, [ref]$r)
    $area = ($r.Right - $r.Left) * ($r.Bottom - $r.Top)
    if ($area -gt $script:area) {
      $script:area = $area
      $script:hwnd = $h
      $script:left = $r.Left
      $script:top = $r.Top
    }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
[ClickAt]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
[ClickAt]::ShowWindow($script:hwnd, 9) | Out-Null
[ClickAt]::SetForegroundWindow($script:hwnd) | Out-Null
Start-Sleep -Milliseconds 80
[ClickAt]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 120
$sx = $script:left + $X
$sy = $script:top + $Y
[ClickAt]::SetCursorPos($sx, $sy) | Out-Null
Start-Sleep -Milliseconds 60
[ClickAt]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 40
[ClickAt]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Write-Output "clicked $sx,$sy"
