# BOOKS -- COMPLETENESS CHECK (the human checks this by hand)

For each book: does our PDF contain the WHOLE book, or only part of a set?

| book | TOC kind | chapters in the contents | chapters inside our PDF | chapters MISSING | our PDF pages | last printed page in our PDF | last page the contents lists | VERDICT |
|---|---|---|---|---|---|---|---|---|
| ADAMS-12 | printed | 49 | 49 | 0 | 1616 | 1576 | 1503 | ok |
| AVERY-2021 | printed | 61 | 61 | 0 | 1019 | 960 | 930 | ok |
| BENZON-2023 | printed | 86 | 85 | 1 | 1503 | 1127 | 1128 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| BOLOGNIA-2024 | printed | 161 | 94 | 67 | 2042 | 1679 | 2705 | **CHECK ME - possible half-book** |
| BRANT-5 | pdf-page | 83 | 83 | 0 | 4324 | 75 | 4055 | ok |
| BRAUNWALD-12 | printed | 102 | 45 | 57 | 1227 | 874 | 1893 | **CHECK ME - possible half-book** |
| BRENNER-11 | printed | 71 | 71 | 0 | 3529 | 2664 | 2663 | ok |
| CAMPBELL-2020 | printed | 82 | 82 | 0 | 5036 | 4526 | 4503 | ok |
| DEVITA-12 | printed | 107 | 104 | 3 | 2427 | 1853 | 1872 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| FIRESTEIN-12 | printed | 125 | 122 | 3 | 2875 | 2196 | 2229 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| GOODMAN-14 | printed | 78 | 77 | 1 | 1664 | 1576 | 1591 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| GRAY-2020 | printed | 79 | 51 | 28 | 2602 | 955 | 1430 | **CHECK ME - possible half-book** |
| GREEN-HAND-2021 | printed | 60 | 60 | 0 | 2535 | 2240 | 2234 | ok |
| GUYTON-2026 | printed | 85 | 6 | 79 | 1070 | 84 | 1101 | **CHECK ME - possible half-book** |
| HARRISON-22 | printed | 505 | 502 | 3 | 4273 | 3976 | 3995 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| HAZZARD-2022 | pdf-page | 108 | 108 | 0 | 3952 | 280 | 3765 | ok |
| IRWIN-RIPPE-2023 | pdf-page | 215 | 215 | 0 | 7992 | 8 | 7576 | ok |
| KAPLAN-11 | pdf-page | 60 | 60 | 0 | 16525 | 3544 | 15194 | ok |
| KRAUSE-16 | printed | 93 | 78 | 15 | 1214 | 1171 | 1200 | **CHECK ME - possible half-book** |
| MANDELL-9 | pdf-page | 210 | 210 | 0 | 4895 | 3827 | 4882 | ok |
| MIDDLETON-2019 | pdf-page | 99 | 99 | 0 | 1886 | 1660 | 1723 | ok |
| MILLER-10 | pdf-page | 87 | 87 | 0 | 13485 | 1916 | 12659 | ok |
| MURRAY-7 | pdf-page | 142 | 142 | 0 | 3317 | 1969 | 3291 | ok |
| NELSON-2024 | pdf-page | 519 | 519 | 0 | 4534 | 4472 | 4522 | ok |
| OXFORD-6 | printed | 127 | 127 | 0 | 1409 | 1372 | 1335 | ok |
| ROBBINS-10 | printed | 29 | 29 | 0 | 1328 | 1314 | 1305 | ok |
| ROCKWOOD-10 | pdf-page | 69 | 69 | 0 | 3628 | 69 | 3567 | ok |
| ROSEN-2022 | pdf-page | 208 | 208 | 0 | 3050 | 2460 | 3043 | ok |
| SABISTON-22 | printed | 92 | 92 | 0 | 2843 | 2074 | 2065 | ok |
| SLEISENGER-11 | printed | 132 | 131 | 1 | 2725 | 2198 | 2206 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| STAHL-2024 | printed | 61 | 57 | 4 | 605 | 549 | 582 | look at the last pages (usually the last chapter starts on a page after the last numbered page) |
| THOMPSON-2023 | printed | 20 | 20 | 0 | 612 | 579 | 425 | ok |
| WILLIAMS-ENDO-2024 | pdf-page | 48 | 48 | 0 | 2319 | 1783 | 2310 | ok |
| WILLIAMS-HEMATOLOGY-2021 | pdf-page | 140 | 140 | 0 | 5052 | 100 | 4999 | ok |
| WILLIAMS-OBSTETRICS-26 | pdf-page | 68 | 68 | 0 | 3475 | 335 | 3139 | ok |
| YOUMANS-4 | printed | 432 | 432 | 0 | 6482 | 3810 | 3796 | ok |
| DELISA-6 | pdf-page | 62 | 62 | 0 | 3742 | 2017 | 3518 | ok |

The two "kind" values mean how the Table of Contents was read:
`printed` = the contents prints the page number of each chapter (we compare it with the last page our PDF reaches);
`pdf-page` = the chapter pages came from the PDF bookmarks (we compare them with the number of pages our PDF has).

A book with chapters MISSING > 0 may be only volume 1 of a set, or the scan may be missing pages. The human checks those by hand.
