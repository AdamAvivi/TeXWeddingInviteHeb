# Third-party notices

This project uses the invitation template, fonts, and software listed below. Each component retains its own copyright and license. This document summarizes those components; their original license texts and notices remain authoritative.

The existing [LICENSE](LICENSE) contains the LaTeX Project Public License (LPPL) version 1.3c. [GPL-3.0.txt](GPL-3.0.txt) contains the GNU General Public License version 3 for reference. Adding that file does not relicense the application, the template, or third-party assets. In particular, the fonts licensed under GPL version 2 retain that version and any accompanying exceptions.

## Invitation template

- **Design:** Max Greenberg's TeX design.
- **File:** [invitation.tex](invitation.tex).
- **Source:** [TeXWeddingInviteHeb](https://github.com/AdamAvivi/TeXWeddingInviteHeb), whose original repository includes the LPPL license text preserved in [LICENSE](LICENSE).
- **Changes:** The bundled template file is unchanged. At generation time, the application fills in invitation details, selects fonts and paper color, adds character fallbacks where needed, and adjusts the generated page's width, margins, and height to fit the content. These changes appear in the downloadable TeX file; the original template remains available in the repository.

Credit for the original design does not imply that its author maintains or supports this website.

## Bundled fonts

The font binaries in `static/fonts/` are redistributed without modification. Most were obtained through [Open Siddur](https://opensiddur.org/help/fonts/). Exact download sources are listed in [the font README](static/fonts/README.md).

| Font | Credits | License and retained notices |
| --- | --- | --- |
| SBL Hebrew | Society of Biblical Literature; see the font and license for full credits | [SBL license](static/fonts/licenses/SBL-license.pdf). Non-commercial use is permitted under its terms; commercial use requires a separate license. |
| Keter YG | Yoram Gnat; Hebrew layout logic by Ralph Hancock and John Hudson | GPL v2 with font exception; [notices](static/fonts/licenses/KeterYG/LICENSE.TXT), [additional notices](static/fonts/licenses/KeterYG/LICENSE), and [GPL v2 text](static/fonts/licenses/KeterYG/GNU-GPL). The layout logic also carries MIT terms. |
| Shlomo | Shlomo Orbach, derived from SIL International's Ezra SIL SR | SIL Open Font License 1.1; [author's license statement](static/fonts/licenses/Shlomo-OFL.txt) and [original metadata notices](static/fonts/licenses/Shlomo-NOTICES.txt). |
| Shofar | Yoram Gnat; additional glyph and layout contributors identified in the notices | GPL v2 with font exception; [notices](static/fonts/licenses/Shofar/LICENSE) and [GPL v2 text](static/fonts/licenses/Shofar/GNU-GPL). |
| Dyslexia Hebrew | Jake Shoag | SIL Open Font License 1.1; [copyright and license](static/fonts/licenses/DyslexiaHebrew/OFL-license.txt). |
| Dorian CLM | Maxim Iorsh | GPL v2; [package notices](static/fonts/licenses/DorianCLM/LICENSE), [font source and copyright](static/fonts/licenses/DorianCLM/Dorian-Book.sfd), and [GPL v2 text](static/fonts/licenses/DorianCLM/GNU-GPL). |
| Ktav Yad CLM | Maxim Iorsh | GPL v2; [package notices](static/fonts/licenses/KtavYadCLM/LICENSE), [supplied font source and copyright](static/fonts/licenses/KtavYadCLM/KtavYadCLM-MediumItalic.pfa), and [GPL v2 text](static/fonts/licenses/KtavYadCLM/GNU-GPL). |
| Nachlaot | Refoyl Finkl; original metadata credits Atech Software | GPL with font exception according to the distributor's permission statement in [Open Siddur's notices](static/fonts/licenses/OpenSiddur-LICENSES.txt); [original font notice](static/fonts/licenses/Nachlaot-NOTICES.txt). |
| DejaVu Sans | DejaVu contributors, Bitstream, and Tavmjong Bah | [DejaVu, Bitstream Vera, and Arev notices and terms](static/fonts/LICENSE.txt). DejaVu changes are in the public domain. |

Keep the accompanying files in `static/fonts/licenses/`, including additional notices and font sources, when redistributing these assets. Font exceptions apply only as stated in each font's license; they are not a blanket exception for every font in this project.

## Installed software

These dependencies are installed through Python or operating-system packages rather than copied into this repository as application source. Their distributions contain their own license texts, copyright notices, and any further dependency notices.

| Component | Use | License information |
| --- | --- | --- |
| [Flask](https://github.com/pallets/flask) | Web application framework | Copyright Pallets; [BSD-3-Clause](https://github.com/pallets/flask/blob/main/LICENSE.txt). |
| [flask-tex](https://github.com/weinbusch/flask-tex) | Invokes XeLaTeX from Flask | Copyright (c) 2020 Martin Bierbaum; [MIT license at the pinned revision](https://github.com/weinbusch/flask-tex/blob/21ca21aa22d34c9d8d1357953e9b8ad480ba2117/LICENSE). |
| [Gunicorn](https://gunicorn.org/) | Runs the deployed Flask application | [MIT license and third-party notices](https://github.com/benoitc/gunicorn/blob/23.0.0/LICENSE). Installed by the Dockerfile. |
| [TeX Live](https://www.tug.org/texlive/) / XeLaTeX | Compiles the invitation | A collection of separately licensed components; see [TeX Live copying information](https://www.tug.org/texlive/copying.html). LaTeX and many packages use LPPL; the entire distribution is not covered by one LPPL license. |
| [Poppler](https://poppler.freedesktop.org/) | Converts PDF invitations to PNG and JPG | [GPL licensing information](https://gitlab.freedesktop.org/poppler/poppler/-/blob/master/COPYING); retain the installed package's notices and applicable source information when redistributing it. |

Python, the container base image, transitive Python dependencies, and operating-system packages also retain their respective licenses. When distributing a built container or a packaged installation, preserve the included license material and comply with the source-distribution requirements of the actual package versions being distributed. This summary does not replace those materials.
