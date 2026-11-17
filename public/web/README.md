# Reader

Copied from Noah Airmet's gsa-dash (https://github.com/Noah-Airmet/gsa-dash): static/reader/, tokens.css, fonts.css, fonts/ and icons.svg, plus pdfjs-viewer.html as /pdfjs/web/viewer.html.
The engine in /pdfjs/ is Mozilla PDF.js 6.1.200, the legacy build (Apache-2.0, see /pdfjs/LICENSE), with the locales cut to en-US.

Changes for this static site are marked "Deseret Wiki" in reader.js: no instant page (/page/), no Librarian (/api/engines), the title comes from ?title=, and Back goes to /library/.
Open a PDF with /pdfjs/web/viewer.html?file=/library/<file>.pdf&title=<title>.
