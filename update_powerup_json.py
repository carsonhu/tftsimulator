from powerup_aliases import aliases
import json


def updateJson():
    # Load JSON file
    with open("map22.bin.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter entries with mName starting with "TFT15_MechanicTrait_"
    filtered = {
        key: value
        for key, value in data.items()
        if isinstance(value, dict)
        and isinstance(value.get("mName"), str)
        and value["mName"].startswith("TFT15_MechanicTrait")
    }

    # Save filtered data to output.json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)

    print(f"Extracted {len(filtered)} entries to output.json")


def getChamps(output_file):
    # Load the previously filtered JSON
    with open("output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter for mName starting with "TFT15_MechanicTraits_TFT15_"
    filtered = {
        key: value
        for key, value in data.items()
        if isinstance(value, dict)
        and isinstance(value.get("mName"), str)
        and value["mName"].startswith("TFT15_MechanicTraits_TFT15_")
    }
    champ_powerups = {}
    for champ, value in filtered.items():
        parts = value["mName"].split("_")
        champ_name = (
            "".join((parts[-2], parts[-1])) if parts[-1] == "HERO" else parts[-1]
        )

        champ_powerups[champ_name] = []
        print(value["mName"])
        # primary_traits = value.get("mConstants", {}).get("Primary", {}).get("traits")
        # secondary_traits = value.get("mConstants", {}).get("Secondary", {}).get("traits")

        for section in ("Primary", "Secondary"):
            traits = value.get("mConstants", {}).get(section, {}).get("traits", [])
            if isinstance(traits, list):
                for key in traits:
                    if key in data:
                        powerup_name = (
                            data[key]
                            .get("mName", "")
                            .removeprefix("TFT15_MechanicTrait_")
                        )
                        powerup_name = aliases.get(powerup_name, powerup_name)
                        # expensive, but it's a cheap operation overall
                        if powerup_name not in champ_powerups[champ_name]:
                            champ_powerups[champ_name].append(powerup_name)

    # Suppose `data` is a Python dict or list you got from json.load / json.loads
    pretty = json.dumps(
        champ_powerups, indent=2, ensure_ascii=False
    )  # indent=2 gives two-space indents
    print(pretty)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(champ_powerups, f, indent=2, ensure_ascii=False)


updateJson()
getChamps("champ_powerups.json")
