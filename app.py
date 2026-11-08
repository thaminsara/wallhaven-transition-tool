import os
import json
import ctypes
import random
import requests
import keyboard
import tkinter as tk
from PIL import Image, ImageFilter, ImageOps

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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                selected = random.choice(data)
                return selected.get("path"), selected.get("id")
    except Exception as e:
        print(f"[!] Internet error or API unreachable: {e}")
    return None, None

def get_fallback_wallpaper(download_dir):
    """Retrieves a randomly selected locally saved wallpaper if offline."""
    if not os.path.exists(download_dir):
        return None
    
    valid_exts = (".png", ".jpg", ".jpeg", ".webp")
    local_files = [
        os.path.join(download_dir, f) for f in os.listdir(download_dir)
        if f.lower().endswith(valid_exts) and f != "wallhaven_current.jpg" and not f.startswith("sketch_")
    ]
    
    if local_files:
        chosen = random.choice(local_files)
        print(f"[*] Offline mode: Selected local fallback wallpaper from {chosen}")
        return chosen
    return None

def set_windows_wallpaper(image_path):
    print("[*] Processing sketch outline and setting wallpaper in background...")
    
    try:
        # Open the target wallpaper image
        img = Image.open(image_path).convert("RGB")
        
        # 1. Generate a smooth pencil sketch outline version in the background
        gray = img.convert("L")
        smoothed = gray.filter(ImageFilter.SMOOTH_MORE)
        edges = smoothed.filter(ImageFilter.FIND_EDGES)
        sketch = ImageOps.invert(edges).convert("RGB")
        
        # Save sketch locally for reference
        sketch_path = os.path.join(os.path.dirname(image_path), "wallhaven_sketch_cache.jpg")
        sketch.save(sketch_path, "JPEG")
        
        # 2. Apply directly to Windows desktop background seamlessly without any window popups
        abs_path = os.path.abspath(image_path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        print(f"[+] Wallpaper updated seamlessly in background: {abs_path}")
        
    except Exception as e:
        print(f"[!] Background wallpaper application error: {e}")

def change_wallpaper():
    config = load_config()
    download_dir = config.get("download_dir", "./wallpapers")
    os.makedirs(download_dir, exist_ok=True)
    
    image_url, wallpaper_id = fetch_wallhaven_wallpaper(config)
    target_path = None
    
    if image_url and wallpaper_id:
        try:
            ext = image_url.split(".")[-1].split("?")[0]
            filename = f"wallhaven_{wallpaper_id}.{ext}"
            target_path = os.path.join(download_dir, filename)
            
            if not os.path.exists(target_path):
                print(f"[*] Downloading new wallpaper...")
                img_data = requests.get(image_url, timeout=15).content
                with open(target_path, "wb") as handler:
                    handler.write(img_data)
        except Exception as e:
            print(f"[!] Failed to download online wallpaper: {e}")
            target_path = None
            
    if not target_path:
        print("[*] Switching to offline fallback mode...")
        target_path = get_fallback_wallpaper(download_dir)
        
    if target_path and os.path.exists(target_path):
        set_windows_wallpaper(target_path)
    else:
        print("[!] No wallpapers found online or in your local './wallpapers' folder!")

def main():
    config = load_config()
    hotkey = config.get("hotkey", "ctrl+alt+w")
    download_dir = config.get("download_dir", "./wallpapers")
    os.makedirs(download_dir, exist_ok=True)
    
    print(f"=== Wallhaven Transition Tool Initialized ===")
    print(f"[*] Local wallpaper cache directory: {os.path.abspath(download_dir)}")
    print(f"Press shortcut [{hotkey}] to fetch/rotate wallpapers.")
    print("Press Ctrl+C in terminal to exit.")
    
    keyboard.add_hotkey(hotkey, change_wallpaper)
    keyboard.wait()

if __name__ == "__main__":
    main()
