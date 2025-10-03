"""
Configuration settings for Privacy Guard System
"""
import json
import os

class Config:
    def __init__(self):
        self.config_file = "config/settings.json"
        self.default_settings = {
            "camera_index": 1,  # 0 = laptop, 1+ = phone/external
            "motion_sensitivity": 1500,
            "detection_delay": 5,  # seconds between detections
            "auto_close_apps": True,
            "show_camera_feed": True,
            "enable_notifications": True,
            "log_level": "INFO",
            "protected_processes": [
                "explorer.exe", "winlogon.exe", "csrss.exe", 
                "wininit.exe", "services.exe", "lsass.exe", 
                "dwm.exe", "svchost.exe", "system", "registry", 
                "python.exe", "pythonw.exe", "privacy_guard.py"
            ],
            "target_applications": [
                "chrome.exe", "firefox.exe", "msedge.exe", "notepad.exe",
                "calc.exe", "mspaint.exe", "winword.exe", "excel.exe",
                "powerpnt.exe", "outlook.exe", "teams.exe", "discord.exe",
                "spotify.exe", "vlc.exe", "steam.exe", "code.exe",
                "whatsapp.exe", "telegram.exe", "zoom.exe", "brave.exe"
            ],
            "force_close_list": [  # <--- NEW! List of apps to always close
                "brave.exe", "iw5sp.exe", "AC4BFSP.exe"
            ]
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file or create default"""
        if not os.path.exists("config"):
            os.makedirs("config")
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_settings
        else:
            self.save_settings(self.default_settings)
            return self.default_settings
    
    def save_settings(self, settings=None):
        """Save current settings to JSON file"""
        if settings is None:
            settings = self.settings
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=4)
    
    def get(self, key):
        """Get configuration value"""
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        """Set configuration value and save"""
        self.settings[key] = value
        self.save_settings()
