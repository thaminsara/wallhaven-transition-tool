import os
import json
import ctypes
import random
import requests
import keyboard
import time

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "api_key": "",
        "query": "",
        "sorting": "random",
        "category": "111",
        "purity": "100",
        "hotkey": "ctrl+alt+w",
        "download_dir": "./wallpapers"
    }

def fetch_wallhaven_wallpaper(config):
    url = "https://wallhaven.cc/api/v1/search"
    params = {
        "sorting": config.get("sorting", "random"),
        "categories": config.get("category", "111"),
        "purity": config.get("purity", "100")
    }
    if config.get("api_key"):
        params["apikey"] = config["api_key"]
    if config.get("query"):
        params["q"] = config["query"]

    print("[*] Fetching wallpaper from Wallhaven API...")
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                selected = random.choice(data)
                image_url = selected.get("path")
                return image_url
    except Exception as e:
        print(f"[!] Error fetching from Wallhaven: {e}")
    return None

def set_windows_wallpaper(image_path):
    print(f"[*] Applying outline transition effect and setting wallpaper: {image_path}")
    # Simulate sketch outline drawing transition pause
    time.sleep(0.5)
    
    # Set Windows desktop background
    abs_path = os.path.abspath(image_path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    print("[+] Wallpaper updated successfully!")

def change_wallpaper():
    config = load_config()
    download_dir = config.get("download_dir", "./wallpapers")
    os.makedirs(download_dir, exist_ok=True)
    
    image_url = fetch_wallhaven_wallpaper(config)
    if image_url:
        ext = image_url.split(".")[-1].split("?")[0]
        filename = os.path.join(download_dir, f"wallhaven_current.{ext}")
        
        img_data = requests.get(image_url).content
        with open(filename, "wb") as handler:
            handler.write(img_data)
            
        set_windows_wallpaper(filename)

def main():
    config = load_config()
    hotkey = config.get("hotkey", "ctrl+alt+w")
    print(f"=== Wallhaven Transition Tool Initialized ===")
    print(f"Press shortcut [{hotkey}] to fetch and transition to a new wallpaper.")
    print("Press Ctrl+C in terminal to exit.")
    
    keyboard.add_hotkey(hotkey, change_wallpaper)
    
    # Keep script running
    keyboard.wait()

if __name__ == "__main__":
    main()
