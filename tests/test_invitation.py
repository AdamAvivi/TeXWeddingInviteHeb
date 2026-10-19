"""Run with: .venv/bin/python -m unittest discover -s tests -v"""
import base64
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from app import app, ROOT, FIELDS, FONTS, build_source, escape_tex, run_tex


def example_data():
    """Fictional sample details, also used to generate the website's sample image."""
    return {
        "choson": "פלוני", "kallah": "פלונית",
        "avihechoson": "אלמוני", "eimhechoson": "אלמונית",
        "avihakallah": "אלמוני", "eimhakallah": "אלמונית",
        "chosonpatgrandparents": "פלוני ופלונית",
        "chosonmatgrandparents": "פלוני ופלונית",
        "kallahpatgrandparents": "אלמוני ואלמונית",
        "kallahmatgrandparents": "אלמוני ואלמונית",
        "date": "יום חמישי, ארבעה ימים לחדש מרחשון\nשנת חמשת אלפים שבע מאות שמונים ושש",
        "venue": "עטרת עלקא", "address": "ברוקלין",
        "kptime": "6:30 בערב", "chuppatime": "7:30 בערב",
        "font": "DejaVu Sans", "background": "#f9f5f2",
    }


class InvitationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_form_has_current_fields_and_compact_sample(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("Max Greenberg's TeX design", page)
        self.assertIn("See a sample invitation", page)
        self.assertIn('/static/sample.png', page)
        self.assertNotIn("See the original example", page)
        for name in FIELDS:
            self.assertIn(f'name="{name}"', page)
        for name, filename in FONTS.items():
            self.assertIn(f'value="{name}"', page)
            self.assertTrue((ROOT / "static/fonts" / filename).is_file())
        sample = self.client.get("/static/sample.png")
        self.assertEqual(sample.status_code, 200)
        self.assertTrue(sample.data.startswith(b"\x89PNG"))
        width, height = struct.unpack(">II", sample.data[16:24])
        self.assertAlmostEqual(width * 25.4 / 300, 110, delta=0.1)
        self.assertLess(height * 25.4 / 300, 190)
        sample.close()

    def test_settings_are_filled_without_changing_the_original_body(self):
        original = (ROOT / "invitation.tex").read_text(encoding="utf-8")
        filled = build_source(example_data())
        self.assertEqual(original.split(r"\begin{document}")[1], filled.split(r"\begin{document}")[1])
        self.assertIn(r"\setmainfont{DejaVuSans.ttf}", filled)
        self.assertIn(r"\pagecolor[HTML]{f9f5f2}", filled)
        for name in FIELDS:
            self.assertNotIn("\\" + name + "{}", filled)

    def test_special_characters_and_new_lines_are_safe(self):
        self.assertEqual(escape_tex("שלום\nעולם"), "שלום\\\\\nעולם")
        self.assertEqual(escape_tex(r"\input{secret}&%#_$^~"), r"\textbackslash{}input\{secret\}\&\%\#\_\$\textasciicircum{}\textasciitilde{}")
        data = example_data()
        data.update(choson="אדם & חנה", avihechoson="")
        filled = build_source(data)
        self.assertIn(r"\choson{אדם \& חנה}", filled)
        self.assertIn(r"\avihechoson{}", filled)

    @unittest.skipUnless(all(shutil.which(tool) for tool in ["xelatex", "pdftoppm", "pdfinfo"]), "Install XeLaTeX and Poppler for font rendering")
    def test_each_bundled_font_renders_hebrew_and_english_without_missing_glyphs(self):
        for name, filename in FONTS.items():
            with self.subTest(font=name):
                data = example_data()
                data.update(font=name, date="10/13/2026", venue="Brooklyn", address="123 Main St", kptime="6pm", chuppatime="7pm")

                def compile_and_check(source, command, directory):
                    self.assertTrue((Path(directory) / filename).is_file())
                    self.assertIn(r"\setmainfont{" + filename + "}", source)
                    pdf = run_tex(source, command, directory)
                    log = (Path(directory) / "texput.log").read_text(errors="replace")
                    missing = [line for line in log.splitlines() if "Missing character:" in line]
                    self.assertEqual(missing, [], name)
                    return pdf

                with patch("app.run_tex", side_effect=compile_and_check):
                    response = self.client.post("/", data=data)
                self.assertEqual(response.status_code, 200, response.get_data(as_text=True)[:1000])

    def test_invalid_submissions_preserve_form_and_show_errors(self):
        for changes in [{"font": r"\input{secret}"}, {"background": "red}"}, {"choson": " "}, {"venue": "א" * 101}]:
            with self.subTest(changes=changes):
                response = self.client.post("/", data={**example_data(), **changes})
                self.assertEqual(response.status_code, 400)
                self.assertIn(b'role="alert"', response.data)
        with patch("app.shutil.which", return_value=None):
            response = self.client.post("/", data=example_data())
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"xelatex", response.data)

    @unittest.skipUnless(all(shutil.which(tool) for tool in ["xelatex", "pdftoppm", "pdfinfo", "pdftotext"]), "Install XeLaTeX and Poppler for the rendering test")
    def test_real_downloads_are_compact_complete_and_match_the_preview(self):
        original = (ROOT / "invitation.tex").read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            # Use real flask-tex compilation and converters; check temporary job cleanup too.
            with patch("app.tempfile.TemporaryDirectory", return_value=tempfile.TemporaryDirectory(dir=folder)):
                response = self.client.post("/", data=example_data())
            self.assertEqual(list(Path(folder).iterdir()), [])
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            files = {}
            for kind, signature in [("pdf", b"%PDF"), ("png", b"\x89PNG"), ("jpg", b"\xff\xd8"), ("tex", b"\\documentclass")]:
                match = re.search(rb'href="(data:[^"]+;base64,[^" ]+)" download="wedding-invitation\.' + kind.encode() + rb'"', response.data)
                self.assertIsNotNone(match)
                files[kind] = base64.b64decode(match.group(1).split(b",", 1)[1])
                self.assertTrue(files[kind].startswith(signature))
                if kind == "png":
                    self.assertIn(b'src="' + match.group(1) + b'"', response.data)
            self.assertEqual((ROOT / "invitation.tex").read_bytes(), original)
            self.assertIn(b"paperwidth=110mm", files["tex"])
            pdf = Path(folder) / "invitation.pdf"
            pdf.write_bytes(files["pdf"])
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
            self.assertRegex(info, r"Pages:\s+1")
            xml = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, check=True).stdout
            page = ET.fromstring(xml).find('.//{http://www.w3.org/1999/xhtml}page')
            width, height = float(page.get("width")), float(page.get("height"))
            self.assertAlmostEqual(width * 25.4 / 72, 110, delta=0.1)
            self.assertLess(height * 25.4 / 72, 190)
            words = list(page)
            self.assertTrue(words)
            for word in words:
                self.assertGreaterEqual(float(word.get("xMin")), 0)
                self.assertLessEqual(float(word.get("xMax")), width)
                self.assertGreaterEqual(float(word.get("yMin")), 0)
                self.assertLessEqual(float(word.get("yMax")), height)
            # Fail if the old large blank area returns above or below the text.
            self.assertLess(min(float(word.get("yMin")) for word in words) * 25.4 / 72, 20)
            self.assertLess((height - max(float(word.get("yMax")) for word in words)) * 25.4 / 72, 20)


if __name__ == "__main__":
    unittest.main()
