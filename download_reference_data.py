import os
import re
import urllib.request
import ssl

def download_data():
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    BASE_URL = "https://raw.communitydragon.org/pbe/game/characters/"
    # Use absolute path to ensure we write to the correct location
    TARGET_DIR = r"c:\Users\carso\Google Drive\Homework\tftSim\tft_calculator\set18\data_reference"

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created directory: {TARGET_DIR}")

    print(f"Fetching file list from {BASE_URL}...")
    try:
        with urllib.request.urlopen(BASE_URL, context=ctx) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch file list: {e}")
        return

    # Regex to find links. 
    # The raw HTML usually has href="filename".
    # We are looking for tft16_*.cdtb.bin.json
    matches = re.findall(r'href="(tft16_[^"]+\.cdtb\.bin\.json)"', html)
    
    # Remove duplicates
    files_to_download = sorted(list(set(matches)))

    print(f"Found {len(files_to_download)} files to download.")

    for filename in files_to_download:
        file_url = BASE_URL + filename
        local_path = os.path.join(TARGET_DIR, filename)
        

            
        print(f"Downloading {filename}...")
        try:
            with urllib.request.urlopen(file_url, context=ctx) as response:
                content = response.read()
                with open(local_path, 'wb') as f:
                    f.write(content)
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

    print("Download process finished.")

if __name__ == "__main__":
    download_data()
