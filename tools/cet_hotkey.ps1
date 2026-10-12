# Open or close the CET overlay (Ctrl+`). Does not move V.
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class CetKey {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$game = Get-Process -Name Cyberpunk2077 | Select-Object -First 1
$script:hwnd = [IntPtr]::Zero
$script:area = 0
[CetKey]::EnumWindows({
  param($h, $l)
  $proc = 0
  [void][CetKey]::GetWindowThreadProcessId($h, [ref]$proc)
  if ($proc -eq $game.Id -and [CetKey]::IsWindowVisible($h)) {
    $r = New-Object CetKey+RECT
    [void][CetKey]::GetWindowRect($h, [ref]$r)
    $area = ($r.Right - $r.Left) * ($r.Bottom - $r.Top)
    if ($area -gt $script:area) { $script:area = $area; $script:hwnd = $h }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
[CetKey]::ShowWindow($script:hwnd, 9) | Out-Null
$fgPid = 0
$fgThread = [CetKey]::GetWindowThreadProcessId([CetKey]::GetForegroundWindow(), [ref]$fgPid)
$thisThread = [CetKey]::GetCurrentThreadId()
[CetKey]::AttachThreadInput($fgThread, $thisThread, $true) | Out-Null
[CetKey]::SetForegroundWindow($script:hwnd) | Out-Null
[CetKey]::AttachThreadInput($fgThread, $thisThread, $false) | Out-Null
# Alt-down lets a background process take the foreground, then Ctrl+` (VK_OEM_3 / scan 0x29).
[CetKey]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
[CetKey]::SetForegroundWindow($script:hwnd) | Out-Null
Start-Sleep -Milliseconds 80
[CetKey]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 120
$fgPid = 0
$fg = [CetKey]::GetForegroundWindow()
[void][CetKey]::GetWindowThreadProcessId($fg, [ref]$fgPid)
# VK_CONTROL=0x11, VK_OEM_3=0xC0, scan=0x29, KEYEVENTF_KEYUP=2, KEYEVENTF_SCANCODE=8
[CetKey]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
[CetKey]::keybd_event(0xC0, 0x29, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 50
[CetKey]::keybd_event(0xC0, 0x29, 2, [UIntPtr]::Zero)
[CetKey]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
Write-Output "sent ctrl+oem3 hwnd=$($script:hwnd) foregroundPid=$fgPid gamePid=$($game.Id)"
