# transpy

## Installation
TODO

## Description
TODO

## Prerequisites
This script uses a predefined set of special unicode characters that have to be used in transcribing manuscripts in Transkribus. These characters have been choosen to represent common phenomenon of medieval manuscripts in a standardized manner and are based on MUFI https://mufi.info/ recomendation.

| Glyph | font-Image | Codepoint | MUFI Name | MUFI link |
| ----- | ----- | --------- | --------- | --------- |
| ƀ     | ![ƀ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3744&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10)      | \u0180    | LATIN SMALL LETTER B WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3744 |
| đ | ![đ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3773&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0111 | LATIN SMALL LETTER D WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3773 |
| ę | ![ę](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3805&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0119 | LATIN SMALL LETTER E WITH OGONEK | https://mufi.info/m.php?p=muficharinfo&i=3805 |
| ħ | ![ħ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3945&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0127 | LATIN SMALL LETTER H WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3945 |
| Ꝁ | ![Ꝁ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4043&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua740 | LATIN CAPITAL LETTER K WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4043 |
| ꝁ | ![ꝁ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4042&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua741 | LATIN SMALL LETTER K WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4042 |
| Ꝉ | ![Ꝉ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4071&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua748 | LATIN CAPITAL LETTER L WITH HIGH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4071 |
| ꝉ | ![ꝉ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4070&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua749 | LATIN SMALL LETTER L WITH HIGH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4070 |
| P̄ | - | \u0050+\u0304 | - | - |
| p̄ | - | \u0070+\u0304 | - | - |
| Ꝑ | ![Ꝑ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4281&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua750 | LATIN CAPITAL LETTER P WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4281 |
| ꝑ | ![ꝑ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4280&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua751 | LATIN SMALL LETTER P WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4280 |
| Ꝓ | ![Ꝓ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4283&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua752 | LATIN CAPITAL LETTER P WITH FLOURISH | https://mufi.info/m.php?p=muficharinfo&i=4283 |
| ꝓ | ![ꝓ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4282&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua753 | LATIN SMALL LETTER P WITH FLOURISH | https://mufi.info/m.php?p=muficharinfo&i=4282 |
| Ꝗ | ![Ꝗ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4307&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua756 | LATIN CAPITAL LETTER Q WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4307 |
| ꝗ | ![ꝗ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4306&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua757 | LATIN SMALL LETTER Q WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4306 |
| Ꝙ | ![Ꝙ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4305&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua758 | LATIN CAPITAL LETTER Q WITH DIAGONAL STROKE | https://mufi.info/m.php?p=muficharinfo&i=4305 |
| ꝙ | ![ꝙ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4304&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua759 | LATIN SMALL LETTER Q WITH DIAGONAL STROKE | https://mufi.info/m.php?p=muficharinfo&i=4304 |
|  [quia] | ![](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4309&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ue8b3 | LATIN SMALL LETTER Q LIGATED WITH R ROTUNDA | https://mufi.info/m.php?p=muficharinfo&i=4309 |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
|  | ![]() |  |  |  |
