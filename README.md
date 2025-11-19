https://tftsimulator.app/ChampionSelector

# About the Project

This is a simulator for Teamfight Tactics. The intent of this project is to develop a way to mathematically determine the value that different items, buffs, augments, anomalies provide to different units in TFT, allowing the user to make more educated decisions during the game.

![image](https://github.com/user-attachments/assets/56edc83a-2873-4f85-a2f2-9e9a15f721d0)

The sidebar allows you to configure the base settings, and the user can then plot the marginal DPS increase of adding an extra item / buff / augment / anomaly.

![image](https://github.com/user-attachments/assets/5539655f-31f1-4207-bf69-ffaa3f401577)

# Getting Started

## Prerequisites
1.  **Install Python**: Ensure you have a stable version of Python installed (**3.10, 3.11, or 3.12**).
    *   *Note: Do not use Python 3.13 or 3.14 yet, as some libraries are not compatible.*
    *   **Recommended**: [Download Python 3.12 Installer](https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe) (Direct Link)
    *   Or visit [python.org downloads](https://www.python.org/downloads/).
2.  **Download Code**: Download this repository to your local machine.

## Quick Start (Windows)

1.  **One-time Setup**:
    *   Double-click `setup.bat`.
    *   This will create a virtual environment (`.venv`) and install all necessary libraries. You only need to do this once.

2.  **Run the App**:
    *   Double-click `run_app.bat`.
    *   This will launch the **TFT Simulator** in your web browser.

## Manual Setup

If you prefer to run commands manually:

1.  Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2.  Run the Streamlit app:
    ```sh
    streamlit run app.py
    ```

Then navigate to the 'ChampionSelector' page in the app.
