import os
import json
import ctypes
import random
import time
import requests
import keyboard
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter

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
        if f.lower().endswith(valid_exts) and f != "wallhaven_current.jpg"
    ]
    
    if local_files:
        chosen = random.choice(local_files)
        print(f"[*] Offline mode: Selected local fallback wallpaper from {chosen}")
        return chosen
    return None

def play_outline_transition(image_path):
    print("[*] Rendering pencil sketch outline transition...")
    
    try:
        img = Image.open(image_path)
        sketch_img = img.filter(ImageFilter.FIND_EDGES).convert("L")
        
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.configure(bg='black')
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        sketch_resized = sketch_img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        tk_sketch = ImageTk.PhotoImage(sketch_resized)
        
        label = tk.Label(root, image=tk_sketch, bg='black', highlightthickness=0)
        label.pack(fill=tk.BOTH, expand=True)
        
        root.update()
        time.sleep(1.2)
        root.destroy()
    except Exception as e:
        print(f"[!] Transition animation skipped: {e}")

def set_windows_wallpaper(image_path):
    play_outline_transition(image_path)
    
    abs_path = os.path.abspath(image_path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    print(f"[+] Wallpaper set successfully: {abs_path}")

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
            
            # Download and save permanently to local cache if not already saved
            if not os.path.exists(target_path):
                print(f"[*] Downloading new wallpaper and saving to local cache...")
                img_data = requests.get(image_url, timeout=15).content
                with open(target_path, "wb") as handler:
                    handler.write(img_data)
            else:
                print("[*] Wallpaper already exists in local cache.")
        except Exception as e:
            print(f"[!] Failed to download online wallpaper: {e}")
            target_path = None
            
    # Fallback to local cache if offline or fetch failed
    if not target_path:
        print("[*] Switching to offline fallback mode...")
        target_path = get_fallback_wallpaper(download_dir)
        
    if target_path and os.path.exists(target_path):
        current_active = os.path.join(download_dir, "wallhaven_current.jpg")
        try:
            img = Image.open(target_path)
            img.convert("RGB").save(current_active, "JPEG")
            set_windows_wallpaper(current_active)
        except Exception:
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
