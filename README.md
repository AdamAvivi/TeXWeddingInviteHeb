# Hebrew wedding invitation

This website will be deployed on Render. The public link will be added here once it is live. You will be able to create and download an invitation in your browser without installing anything.

The invitation uses **Max Greenberg's TeX design** and [flask-tex](https://github.com/weinbusch/flask-tex).

## How it works

1. Enter the couple's names, family details, date, venue, and times.
2. Type normally, or select a text field and click letters on the Hebrew keyboard.
3. Choose a font and paper color, then click **Create invitation**.
4. The Flask server fills the settings in Max Greenberg's TeX template. XeLaTeX compiles it into a PDF, and Poppler converts that PDF into PNG and JPG images.
5. View the invitation and download **PDF, PNG, JPG, or TeX**.

The original `invitation.tex` file remains unchanged. The generated document uses a compact page with smaller margins; its height fits the content. The preview and image downloads come from the same PDF. Temporary files are deleted after generation, and there is no database or account system.

The font selector includes **SBL Hebrew, Keter YG, Shlomo, Shofar, Dyslexia Hebrew, Dorian CLM, Ktav Yad CLM, Nachlaot, and DejaVu Sans**. All font files are bundled and loaded directly, so neither the server operator nor visitors need to install them separately. SBL Hebrew gives the original typeface. Ktav Yad CLM and Nachlaot have limited vowel-mark support; English entries use a fallback where needed.

SBL Hebrew is free for non-commercial use; commercial use requires a separate license. Font sources, copyright notices, and licenses are documented in [static/fonts/README.md](static/fonts/README.md).

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the template, font, and dependency credits and license references. The existing LPPL text is in [LICENSE](LICENSE); a separate copy of GPL v3 is in [GPL-3.0.txt](GPL-3.0.txt). Each third-party component retains its own license.

The two main application files are `app.py` (form handling and generation) and `templates/index.html` (the page, its styling, and the keyboard).

## Run it locally

If you want to run the website on your own computer, follow the instructions for your operating system, then the shared steps below. You need Python 3.10 or newer, Git, XeLaTeX, and Poppler.

### macOS

Install [Homebrew](https://brew.sh/) if you do not already have it, then run:

```sh
brew install python git poppler
brew install --cask mactex-no-gui
```

[MacTeX without GUI applications](https://formulae.brew.sh/cask/mactex-no-gui) includes XeLaTeX and the required TeX packages. It is a large download. Close and reopen your terminal after installation so it can find the TeX commands.

### Ubuntu

```sh
sudo apt update
sudo apt install python3 python3-venv git poppler-utils \
    texlive-xetex texlive-lang-other texlive-pictures
```

### Fedora

```sh
sudo dnf install python3 python3-pip git poppler-utils \
    texlive-xetex texlive-polyglossia texlive-bidi texlive-fontspec \
    texlive-pgf texlive-geometry texlive-xcolor
```

### Start the website (all three systems)

Download the project and open its folder in your terminal. Then run:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://localhost:3001** in your browser. Press **Ctrl+C** in the terminal to stop the server. If that port is occupied, use `PORT=3002 python app.py` and open http://localhost:3002 instead.

Select any font in the form. SBL Hebrew is the default and is included; there is no separate font-installation step.

When returning to the project later, you only need:

```sh
source .venv/bin/activate
python app.py
```

To compile a downloaded TeX file separately, place the selected font file from `static/fonts/` beside it. Also include `DejaVuSans.ttf` when the selected font uses an English/punctuation fallback.

### Checks

With the virtual environment active:

```sh
python -m unittest discover -s tests -v
```

The tests check the form, input handling, actual generated downloads, compact page dimensions, text bounds, preview consistency, and temporary-file cleanup. `static/sample.png` shows a compact invitation generated with fictional details and SBL Hebrew.

## Deployment

The Dockerfile packages Python, XeLaTeX, Poppler, and Gunicorn together. On [Render](https://render.com/docs/docker), create a **Web Service** from this repository, choose **Docker**, use `./Dockerfile`, and leave the Docker Command override empty.

The image copies all bundled fonts and their notices from `static/fonts/`. All font choices work without system font installation. Observe the font licenses, especially SBL's non-commercial terms, when deploying. The Docker build and hosted deployment have not yet been verified.
