"""
System Commands Module
Handles executing system commands like opening applications, volume control, and power
"""

import subprocess
import webbrowser
import os
import psutil
from datetime import datetime
from config import APP_MAPPINGS, WEBSITE_MAPPINGS


class SystemCommands:
    """Handles system command execution"""
    
    def __init__(self):
        self.app_mappings = APP_MAPPINGS
        self.website_mappings = WEBSITE_MAPPINGS
    
    def open_application(self, app_name: str) -> tuple[bool, str]:
        """
        Open an application by name.
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            tuple: (success, message)
        """
        app_name_lower = app_name.lower().strip()
        
        # Check if we have a mapping for this app
        if app_name_lower in self.app_mappings:
            app_command = self.app_mappings[app_name_lower]
        else:
            # Try to run it directly
            app_command = app_name_lower
        
        try:
            # Use shell=True for Windows to find apps in PATH
            subprocess.Popen(
                app_command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True, f"Membuka {app_name}"
        except Exception as e:
            return False, f"Gagal membuka {app_name}: {e}"
    
    def close_application(self, app_name: str) -> tuple[bool, str]:
        """
        Close an application by name using taskkill.
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            tuple: (success, message)
        """
        # Map app names to process names
        process_mappings = {
            "notepad": "notepad.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "browser": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "calculator": "CalculatorApp.exe",
            "kalkulator": "CalculatorApp.exe",
            "spotify": "Spotify.exe",
            "discord": "Discord.exe",
            "vscode": "Code.exe",
            "visual studio code": "Code.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "telegram": "Telegram.exe",
            "whatsapp": "WhatsApp.exe",
            "steam": "steam.exe",
            "youtube": "chrome.exe",  # YouTube runs in browser
        }
        
        app_name_lower = app_name.lower().strip()
        
        # Get process name
        if app_name_lower in process_mappings:
            process_name = process_mappings[app_name_lower]
        else:
            # Try to guess process name
            process_name = f"{app_name_lower}.exe"
        
        try:
            # Use taskkill to close the application
            result = subprocess.run(
                ["taskkill", "/IM", process_name, "/F"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return True, f"Menutup {app_name}"
            else:
                return False, f"Tidak dapat menutup {app_name}. Mungkin tidak sedang berjalan."
        except Exception as e:
            return False, f"Gagal menutup {app_name}: {e}"
    
    def close_browser_tab(self) -> tuple[bool, str]:
        """
        Close the current browser tab using Ctrl+W keyboard shortcut.
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Use PowerShell to send Ctrl+W to close current tab
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^w")
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Menutup tab browser"
        except Exception as e:
            return False, f"Gagal menutup tab: {e}"
    
    def close_all_browser_tabs(self) -> tuple[bool, str]:
        """
        Close all browser tabs/window using Ctrl+Shift+W.
        
        Returns:
            tuple: (success, message)
        """
        try:
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^+w")
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Menutup semua tab browser"
        except Exception as e:
            return False, f"Gagal menutup tab: {e}"
    
    def open_website(self, site_name: str) -> tuple[bool, str]:
        """
        Open a website in the default browser.
        
        Args:
            site_name: Name or URL of the website
            
        Returns:
            tuple: (success, message)
        """
        site_name_lower = site_name.lower().strip()
        
        # Check if we have a mapping
        if site_name_lower in self.website_mappings:
            url = self.website_mappings[site_name_lower]
        elif site_name_lower.startswith(('http://', 'https://')):
            url = site_name_lower
        else:
            # Try to construct URL
            url = f"https://www.{site_name_lower}.com"
        
        try:
            webbrowser.open(url)
            return True, f"Membuka {site_name}"
        except Exception as e:
            return False, f"Gagal membuka {site_name}: {e}"
    
    def search_youtube(self, query: str) -> tuple[bool, str]:
        """
        Search for a video on YouTube.
        
        Args:
            query: Search query for YouTube
            
        Returns:
            tuple: (success, message)
        """
        if not query:
            return False, "Apa yang ingin dicari di YouTube?"
        
        try:
            # URL encode the query
            from urllib.parse import quote
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            webbrowser.open(search_url)
            return True, f"Mencari {query} di YouTube"
        except Exception as e:
            return False, f"Gagal mencari di YouTube: {e}"
    
    def play_youtube(self, query: str) -> tuple[bool, str]:
        """
        Search YouTube and play the first video result directly.
        
        Args:
            query: What to play on YouTube
            
        Returns:
            tuple: (success, message)
        """
        if not query:
            return False, "Apa yang ingin diputar?"
        
        try:
            import requests
            import re
            from urllib.parse import quote
            
            # Search YouTube
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            # Find video ID from response
            video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)
            
            if video_ids:
                video_id = video_ids[0]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(video_url)
                return True, f"Memutar {query}"
            
            # Fallback to search
            return self.search_youtube(query)
            
        except Exception as e:
            print(f"⚠️ YouTube play error: {e}")
            return self.search_youtube(query)
    
    def search_google(self, query: str) -> tuple[bool, str]:
        """
        Search something on Google.
        
        Args:
            query: Search query
            
        Returns:
            tuple: (success, message)
        """
        if not query:
            return False, "Apa yang ingin dicari di Google?"
        
        try:
            from urllib.parse import quote
            search_url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(search_url)
            return True, f"Mencari {query} di Google"
        except Exception as e:
            return False, f"Gagal mencari di Google: {e}"
    
    def open_url(self, url: str) -> tuple[bool, str]:
        """
        Open a custom URL directly in the default browser.
        
        Args:
            url: The URL to open (can be with or without http/https)
            
        Returns:
            tuple: (success, message)
        """
        if not url:
            return False, "URL tidak diberikan"
        
        url = url.strip()
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        try:
            webbrowser.open(url)
            return True, f"Membuka {url}"
        except Exception as e:
            return False, f"Gagal membuka URL: {e}"
    
    def get_current_time(self) -> str:
        """Get the current time in a readable format"""
        now = datetime.now()
        
        # Format: "Sekarang jam 10 lebih 30 menit"
        hour = now.hour
        minute = now.minute
        
        if minute == 0:
            return f"Sekarang jam {hour} tepat"
        elif minute == 30:
            return f"Sekarang jam {hour} setengah"
        elif minute < 30:
            return f"Sekarang jam {hour} lebih {minute} menit"
        else:
            next_hour = (hour + 1) % 24
            mins_to = 60 - minute
            return f"Sekarang jam {next_hour} kurang {mins_to} menit"
    
    def get_current_date(self) -> str:
        """Get the current date in a readable format"""
        now = datetime.now()
        
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        day_name = days[now.weekday()]
        month_name = months[now.month - 1]
        
        return f"Hari ini {day_name}, tanggal {now.day} {month_name} {now.year}"
    
    # ============ Volume Control ============
    
    def volume_up(self, amount: int = 10) -> tuple[bool, str]:
        """Increase system volume"""
        try:
            # Use PowerShell to control volume
            ps_script = f'''
            $obj = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt {amount // 2}; $i++) {{
                $obj.SendKeys([char]175)
            }}
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, f"Volume dinaikkan"
        except Exception as e:
            return False, f"Gagal menaikkan volume: {e}"
    
    def volume_down(self, amount: int = 10) -> tuple[bool, str]:
        """Decrease system volume"""
        try:
            ps_script = f'''
            $obj = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt {amount // 2}; $i++) {{
                $obj.SendKeys([char]174)
            }}
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, f"Volume diturunkan"
        except Exception as e:
            return False, f"Gagal menurunkan volume: {e}"
    
    def volume_mute(self) -> tuple[bool, str]:
        """Toggle mute"""
        try:
            ps_script = '''
            $obj = New-Object -ComObject WScript.Shell
            $obj.SendKeys([char]173)
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Volume di-mute atau unmute"
        except Exception as e:
            return False, f"Gagal mute volume: {e}"
    
    def volume_max(self) -> tuple[bool, str]:
        """Set volume to maximum"""
        try:
            ps_script = '''
            $obj = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt 50; $i++) {
                $obj.SendKeys([char]175)
            }
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Volume dimaksimalkan"
        except Exception as e:
            return False, f"Gagal memaksimalkan volume: {e}"
    
    # ============ Power Control ============
    
    def shutdown(self, delay: int = 5) -> tuple[bool, str]:
        """Shutdown the computer"""
        try:
            subprocess.run(
                ["shutdown", "/s", "/t", str(delay)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, f"Komputer akan mati dalam {delay} detik"
        except Exception as e:
            return False, f"Gagal mematikan komputer: {e}"
    
    def restart(self, delay: int = 5) -> tuple[bool, str]:
        """Restart the computer"""
        try:
            subprocess.run(
                ["shutdown", "/r", "/t", str(delay)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, f"Komputer akan restart dalam {delay} detik"
        except Exception as e:
            return False, f"Gagal restart komputer: {e}"
    
    def cancel_shutdown(self) -> tuple[bool, str]:
        """Cancel a pending shutdown/restart"""
        try:
            subprocess.run(
                ["shutdown", "/a"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Shutdown dibatalkan"
        except Exception as e:
            return False, f"Gagal membatalkan shutdown: {e}"
    
    def sleep(self) -> tuple[bool, str]:
        """Put computer to sleep"""
        try:
            subprocess.run(
                ["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Komputer akan sleep"
        except Exception as e:
            return False, f"Gagal sleep: {e}"
    
    def lock_screen(self) -> tuple[bool, str]:
        """Lock the screen"""
        try:
            subprocess.run(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Layar dikunci"
        except Exception as e:
            return False, f"Gagal mengunci layar: {e}"
    
    # ============ Task Manager ============
    
    def list_processes(self, sort_by: str = "memory", limit: int = 25) -> list[dict]:
        """
        List running processes sorted by memory or CPU usage.
        
        Args:
            sort_by: "memory" or "cpu"
            limit: Max number of processes to return
            
        Returns:
            list of dicts with process info
        """
        # System/background processes to hide
        hidden_processes = {
            "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
            "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe",
            "winlogon.exe", "dwm.exe", "conhost.exe", "sihost.exe",
            "taskhostw.exe", "ctfmon.exe", "dllhost.exe", "wudfhost.exe",
            "searchhost.exe", "runtimebroker.exe", "shellexperiencehost.exe",
            "startmenuexperiencehost.exe", "textinputhost.exe",
            "systemsettings.exe", "applicationframehost.exe",
            "windowsinternal.composableshell.experiences.textinput.inputapp.exe",
            "securityhealthservice.exe", "securityhealthsystray.exe",
            "sgrmbroker.exe", "spoolsv.exe", "msdtc.exe", "dashost.exe",
            "gamebarpresencewriter.exe", "lockapp.exe", "searchindexer.exe",
            "searchprotocolhost.exe", "searchfilterhost.exe", "audiodg.exe",
            "system idle process", "idle", "memory compression",
        }
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
            try:
                info = proc.info
                name = info['name'].lower()
                
                # Skip hidden system processes
                if name in hidden_processes:
                    continue
                
                # Skip processes with no memory usage
                mem = info['memory_info']
                if mem is None or mem.rss < 1024 * 1024:  # Less than 1MB
                    continue
                
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu': info['cpu_percent'] or 0,
                    'memory_mb': round(mem.rss / (1024 * 1024), 1),
                    'status': info['status'],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort
        if sort_by == "cpu":
            processes.sort(key=lambda p: p['cpu'], reverse=True)
        else:
            processes.sort(key=lambda p: p['memory_mb'], reverse=True)
        
        return processes[:limit]
