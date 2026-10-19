"""Fill the original TeX, compile it with flask-tex, and show the results."""
import base64
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from flask import Flask, render_template, request
from flask_tex import TexError, run_tex

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "choson": "Groom’s name",
    "kallah": "Bride’s name",
    "avihechoson": "Groom’s father",
    "eimhechoson": "Groom’s mother",
    "avihakallah": "Bride’s father",
    "eimhakallah": "Bride’s mother",
    "chosonpatgrandparents": "Groom’s paternal grandparents",
    "chosonmatgrandparents": "Groom’s maternal grandparents",
    "kallahpatgrandparents": "Bride’s paternal grandparents",
    "kallahmatgrandparents": "Bride’s maternal grandparents",
    "date": "Wedding date",
    "venue": "Venue",
    "address": "Address",
    "kptime": "Reception time",
    "chuppatime": "Chuppah time",
}
REQUIRED = ["choson", "kallah", "date", "venue", "kptime", "chuppatime"]
FONTS = {
    "SBL Hebrew": "SBL_Hbrw.ttf",
    "Keter YG": "KeterYG-Medium.ttf",
    "Shlomo": "Shlomo.ttf",
    "Shofar": "ShofarRegular.ttf",
    "Dyslexia Hebrew": "DyslexiaHebrew-Regular.otf",
    "Dorian CLM": "DorianCLM-Book.ttf",
    "Ktav Yad CLM": "KtavYadCLM-MediumItalic.ttf",
    "Nachlaot": "Nachlaot.ttf",
    "DejaVu Sans": "DejaVuSans.ttf",
}
# These fonts do not include Latin letters; use the included fallback for English.
HEBREW_ONLY_FONTS = {"Dyslexia Hebrew", "Dorian CLM", "Ktav Yad CLM", "Nachlaot"}


def escape_tex(text):
    """Treat typed characters as text, never as TeX commands."""
    replacements = {
        "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$",
        "&": r"\&", "#": r"\#", "%": r"\%", "_": r"\_",
        "^": r"\textasciicircum{}", "~": r"\textasciitilde{}",
    }
    return "\\\\\n".join(
        "".join(replacements.get(char, char) for char in line)
        for line in text.splitlines()
    )


def build_source(data):
    """Fill the template settings; all invitation layout stays in the TeX file."""
    if not hasattr(data, "get"):
        raise ValueError("Please submit the invitation form.")
    font = data.get("font", "SBL Hebrew")
    if not isinstance(font, str) or font not in FONTS:
        raise ValueError("Please select a font from the list.")
    source = (ROOT / "invitation.tex").read_text(encoding="utf-8")
    for name in FIELDS:
        value = data.get(name, "")
        if not isinstance(value, str):
            raise ValueError("Text fields must contain text.")
        value = value.strip()
        if name in REQUIRED and not value:
            raise ValueError("Please fill in the couple, date, venue, and times.")
        if len(value) > (220 if name == "date" else 100):
            raise ValueError("Please shorten the text in the invitation.")
        if font in HEBREW_ONLY_FONTS:
            # Keep ASCII runs (dates, English names, times) together and left-to-right.
            lines = []
            for line in value.splitlines():
                parts = re.split(r"([!-~][ -~]*)", line)
                lines.append("".join(
                    r"\textenglish{" + escape_tex(part) + "}" if part.isascii() and part.strip()
                    else escape_tex(part) for part in parts
                ))
            text = "\\\\\n".join(lines)
        else:
            text = escape_tex(value)
        source = source.replace("\\" + name + "{}", "\\" + name + "{" + text + "}", 1)

    source = source.replace(r"\setmainfont{}", r"\setmainfont{" + FONTS[font] + "}")
    if font in {"Ktav Yad CLM", "Nachlaot"}:
        # These older font files contain Hebrew glyphs but no OpenType Hebrew tag.
        declaration = r"\newfontfamily\hebrewfont[Script=Default]{" + FONTS[font] + "}\n"
        source = source.replace(r"\begin{document}", declaration + r"\begin{document}", 1)
    if font in HEBREW_ONLY_FONTS:
        fallback = r"""\setotherlanguage{english}
\newfontfamily\englishfont{DejaVuSans.ttf}
\newfontfamily\fallbackfont{DejaVuSans.ttf}
"""
        source = source.replace(r"\begin{document}", fallback + r"\begin{document}", 1)
        if font == "Nachlaot":
            for mark in "׳״":
                source = source.replace(mark, r"{\fallbackfont " + mark + "}")
        if font == "Dyslexia Hebrew":
            source = source.replace(r"\@venue, \@address", r"\@venue{\fallbackfont ,} \@address")
    color = data.get("background", "#f9f5f2")
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Please choose a valid paper color.")
    return source.replace(r"\pagecolor[]{}", r"\pagecolor[HTML]{" + color[1:] + "}")


def compact_page(source):
    """Fit the generated page around its contents; never edit invitation.tex."""
    source = source.replace(
        r"\geometry{top=1in,left=0.5in, right=0.5in}",
        r"\geometry{paperwidth=110mm,paperheight=210mm,margin=8mm,noheadfoot}",
    )
    source = source.replace(r"\begin{document}", r"\newsavebox{\invitationbox}" + "\n" + r"\begin{document}", 1)
    source = source.replace(r"\begin{center}", r"\begin{lrbox}{\invitationbox}\begin{minipage}{\textwidth}\begin{center}", 1)
    source = source.replace(r"\end{center}", r"""\end{center}\end{minipage}\end{lrbox}
    \setlength{\paperheight}{\dimexpr\ht\invitationbox+\dp\invitationbox+16mm\relax}
    \special{papersize=\the\paperwidth,\the\paperheight}
    \noindent\usebox{\invitationbox}""", 1)
    return source


def render_files(source):
    """Create the PDF with flask-tex, then make images from that same PDF."""
    source = compact_page(source)
    for command in ["xelatex", "pdftoppm", "pdfinfo"]:
        if not shutil.which(command):
            raise RuntimeError(f"Missing {command}. Follow the setup instructions in README.md.")

    # Each submission gets its own temporary folder, removed when this block ends.
    with tempfile.TemporaryDirectory(prefix="invitation-") as folder:
        job = Path(folder)
        for filename in FONTS.values():
            shutil.copy(ROOT / "static/fonts" / filename, job)
        pdf = run_tex(
            source,
            command="xelatex -no-shell-escape -halt-on-error",
            directory=folder,
        )
        pdf_path = job / "invitation.pdf"
        pdf_path.write_bytes(pdf)

        info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True, timeout=15)
        if not any(line.split() == ["Pages:", "1"] for line in info.stdout.splitlines()):
            raise ValueError("The invitation fills more than one page. Shorten the names or date and try again.")
        for flag, extension in [("-png", "png"), ("-jpeg", "jpg")]:
            subprocess.run(
                ["pdftoppm", "-singlefile", "-r", "300", flag, str(pdf_path), str(job / "invitation")],
                check=True, capture_output=True, timeout=30,
            )

        files = {}
        for extension, mime in [("pdf", "application/pdf"), ("png", "image/png"), ("jpg", "image/jpeg"), ("tex", "text/plain;charset=utf-8")]:
            content = source.encode("utf-8") if extension == "tex" else (job / f"invitation.{extension}").read_bytes()
            files[extension] = f"data:{mime};base64," + base64.b64encode(content).decode("ascii")
        return files


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    files = None
    error = None
    status = 200
    if request.method == "POST":
        try:
            files = render_files(build_source(request.form))
        except ValueError as problem:
            error, status = str(problem), 400
        except RuntimeError as problem:
            error, status = str(problem), 503
        except TexError:
            error = "TeX could not render the invitation. Check the TeX packages listed in README.md or try another font."
            status = 422
        except (subprocess.SubprocessError, OSError):
            error = "Could not generate the files. Check the TeX Live and Poppler setup in README.md."
            status = 500
    return render_template("index.html", fields=FIELDS, required=REQUIRED, fonts=FONTS,
                           values=request.form, files=files, error=error), status


@app.errorhandler(413)
def form_too_large(error):
    return "The form is too large. Go back and shorten the invitation text.", 413


@app.after_request
def keep_files_private(response):
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "3001")), threaded=False)
