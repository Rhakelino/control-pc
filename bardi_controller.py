"""
Bardi IoT Controller Module
Mengontrol Smart Plug Bardi menggunakan tinytuya untuk kontrol lokal
"""

import tinytuya
import time

# Bardi Device Configuration
BARDI_CONFIG = {
    'device_id': 'a3c7d26023600ff7b37fye',
    'local_key': 'F&F=g9<J-AOmN]iI',
    'ip_address': '192.168.1.8',
    'version': 3.4
}


class BardiController:
    """Controller untuk Bardi Smart Plug EU02A"""
    
    def __init__(self):
        """Initialize Bardi device connection"""
        self.device = tinytuya.OutletDevice(
            dev_id=BARDI_CONFIG['device_id'],
            address=BARDI_CONFIG['ip_address'],
            local_key=BARDI_CONFIG['local_key'],
            version=BARDI_CONFIG['version']
        )
        self.device.set_socketTimeout(5)  # 5 second timeout
        print("🔌 Bardi Controller initialized")
    
    def turn_on(self):
        """Menyalakan aliran listrik Bardi Smart Plug"""
        try:
            result = self.device.turn_on()
            if result and 'Error' not in str(result):
                return True, "✅ Bardi Smart Plug berhasil dinyalakan!"
            else:
                return False, f"❌ Gagal menyalakan Bardi: {result}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def turn_off(self):
        """Mematikan aliran listrik Bardi Smart Plug"""
        try:
            result = self.device.turn_off()
            if result and 'Error' not in str(result):
                return True, "✅ Bardi Smart Plug berhasil dimatikan!"
            else:
                return False, f"❌ Gagal mematikan Bardi: {result}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def get_status(self):
        """Mendapatkan status Bardi Smart Plug"""
        try:
            status = self.device.status()
            if status and 'dps' in status:
                is_on = status['dps'].get('1', False)
                return True, {
                    'is_on': is_on,
                    'status': 'ON' if is_on else 'OFF',
                    'raw': status
                }
            else:
                return False, {'error': f"Status tidak tersedia: {status}"}
        except Exception as e:
            return False, {'error': str(e)}


class SafeShutdown:
    """
    Safe Shutdown Module
    Mematikan laptop dengan prosedur aman untuk mencegah stack di logo Lenovo
    """
    
    def __init__(self, bardi_controller: BardiController):
        self.bardi = bardi_controller
    
    def execute(self, shutdown_delay=20, bardi_delay=25):
        """
        Prosedur Safe Shutdown:
        1. Kirim perintah shutdown ke Windows dengan delay 20 detik
        2. Setelah shutdown dimulai, matikan Bardi untuk memutus daya total
        
        Args:
            shutdown_delay: Waktu tunggu sebelum Windows shutdown (default 20 detik)
            bardi_delay: Waktu tunggu sebelum Bardi dimatikan (default 25 detik)
        """
        import os
        import threading
        
        # Step 1: Kirim perintah shutdown Windows
        os.system(f"shutdown /s /t {shutdown_delay}")
        message = f"🔄 Safe Shutdown dimulai!\n"
        message += f"⏳ Windows akan mati dalam {shutdown_delay} detik\n"
        message += f"🔌 Bardi akan dimatikan dalam {bardi_delay} detik"
        
        # Step 2: Schedule Bardi off setelah delay
        def delayed_bardi_off():
            time.sleep(bardi_delay)
            try:
                self.bardi.turn_off()
            except:
                pass  # Laptop mungkin sudah mati
        
        # Jalankan di background thread
        thread = threading.Thread(target=delayed_bardi_off)
        thread.daemon = True
        thread.start()
        
        return True, message


# Singleton instance
_bardi_controller = None
_safe_shutdown = None


def get_bardi_controller():
    """Get singleton instance of BardiController"""
    global _bardi_controller
    if _bardi_controller is None:
        try:
            _bardi_controller = BardiController()
        except Exception as e:
            print(f"⚠️ Failed to initialize Bardi: {e}")
            return None
    return _bardi_controller


def get_safe_shutdown():
    """Get singleton instance of SafeShutdown"""
    global _safe_shutdown
    if _safe_shutdown is None:
        bardi = get_bardi_controller()
        if bardi:
            _safe_shutdown = SafeShutdown(bardi)
    return _safe_shutdown
