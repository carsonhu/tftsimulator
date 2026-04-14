import requests

url = "https://raw.communitydragon.org/pbe/game/data/maps/shipping/map22/map22.bin.json"
output_path = "map22.bin.json"

response = requests.get(url)

if response.status_code == 200:
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded to {output_path}")
else:
    print(f"Failed to download. Status code: {response.status_code}")   