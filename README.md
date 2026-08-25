https://tftsimulator.app/

The site is a static page: it runs this repo's simulator directly in the
browser under Pyodide, with no packages to install on load. `stlite.html` is
the previous Streamlit-in-the-browser build, kept for the pages the static one
does not cover yet (Mana Generation). Both fetch the same `.py` files from this
repo, so neither can drift from the simulator the tests exercise.

# About the Project

This is a simulator for Teamfight Tactics. The intent of this project is to develop a way to mathematically determine the value that different items, buffs, augments, anomalies provide to different units in TFT, allowing the user to make more educated decisions during the game.

![image](https://github.com/user-attachments/assets/56edc83a-2873-4f85-a2f2-9e9a15f721d0)

The sidebar allows you to configure the base settings, and the user can then plot the marginal DPS increase of adding an extra item / buff / augment / anomaly.

![image](https://github.com/user-attachments/assets/5539655f-31f1-4207-bf69-ffaa3f401577)

# Getting Started

## Prerequisites
1.  **Install Python 3.12 or newer**.
    *   **Recommended**: [Download Python 3.12 Installer](https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe) (Direct Link)
    *   Or visit [python.org downloads](https://www.python.org/downloads/).
    *   Tick **"Add python.exe to PATH"** in the installer.
2.  **Download Code**: Download this repository to your local machine.

## Quick Start (Windows)

**Double-click `run_app.bat`.** That is the whole thing.

On the first launch it creates the virtual environment (`.venv`) and installs
everything; after that it goes straight to starting the app. It also notices
when `requirements.txt` changes and reinstalls on its own, so you never have
to remember to. The **TFT Simulator** then opens in your browser.

### Contributing / running the tests

Double-click `setup.bat` instead. It does everything above, plus installs the
development extras (pytest, matplotlib) and runs the test suite. After that:

```sh
.venv\Scripts\python -m pytest
```

## Manual Setup

If you prefer to run commands manually:

1.  Create a virtual environment and install dependencies:
    ```sh
    py -3.12 -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    ```
    Add `-r requirements-dev.txt` instead if you want the test tooling too.

2.  Run the Streamlit app:
    ```sh
    .venv\Scripts\python -m streamlit run app.py
    ```

Then navigate to the 'ChampionSelector' page in the app.

## Running the static site locally

The site at the repo root is plain HTML/JS and fetches its Python sources over
HTTP, so it needs a server rather than opening `index.html` from disk:

```sh
.venv\Scripts\python serve.py
```

Then open <http://127.0.0.1:8618/>. Use this rather than
`python -m http.server`: that one sends no `Cache-Control`, so browsers invent
their own expiry and keep serving the files they already have — an edit to a
`.py` file then doesn't show up no matter how many times you reload or restart
the server, because the browser never asks. `serve.py` says "revalidate",
which costs a `304` per file and nothing else.
