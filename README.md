# transpy

## Installation
TODO

## Description
TODO

## Prerequisites

### Special characters

This script uses a predefined set of special unicode characters that have to be used in transcribing manuscripts in Transkribus. These characters have been choosen to represent common phenomenon of medieval manuscripts in a standardized manner and are based on MUFI https://mufi.info/ recomendation.

| Glyph | font-Image | Codepoint | MUFI Name | MUFI link |
| ----- | ----- | --------- | --------- | --------- |
| ƀ | ![ƀ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3744&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10)      | \u0180    | LATIN SMALL LETTER B WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3744 |
| đ | ![đ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3773&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0111 | LATIN SMALL LETTER D WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3773 |
| ę | ![ę](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3805&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0119 | LATIN SMALL LETTER E WITH OGONEK | https://mufi.info/m.php?p=muficharinfo&i=3805 |
| ħ | ![ħ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=3945&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0127 | LATIN SMALL LETTER H WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=3945 |
| Ꝁ | ![Ꝁ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4043&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua740 | LATIN CAPITAL LETTER K WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4043 |
| ꝁ | ![ꝁ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4042&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua741 | LATIN SMALL LETTER K WITH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4042 |
| Ꝉ | ![Ꝉ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4071&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua748 | LATIN CAPITAL LETTER L WITH HIGH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4071 |
| ꝉ | ![ꝉ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4070&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua749 | LATIN SMALL LETTER L WITH HIGH STROKE | https://mufi.info/m.php?p=muficharinfo&i=4070 |
| P̄ [Per] | - | \u0050+\u0304 | - | - |
| p̄ [per] | - | \u0070+\u0304 | - | - |
| Ꝑ | ![Ꝑ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4281&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua750 | LATIN CAPITAL LETTER P WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4281 |
| ꝑ | ![ꝑ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4280&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua751 | LATIN SMALL LETTER P WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4280 |
| Ꝓ | ![Ꝓ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4283&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua752 | LATIN CAPITAL LETTER P WITH FLOURISH | https://mufi.info/m.php?p=muficharinfo&i=4283 |
| ꝓ | ![ꝓ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4282&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua753 | LATIN SMALL LETTER P WITH FLOURISH | https://mufi.info/m.php?p=muficharinfo&i=4282 |
| Ꝗ | ![Ꝗ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4307&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua756 | LATIN CAPITAL LETTER Q WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4307 |
| ꝗ | ![ꝗ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4306&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua757 | LATIN SMALL LETTER Q WITH STROKE THROUGH DESCENDER | https://mufi.info/m.php?p=muficharinfo&i=4306 |
| Ꝙ | ![Ꝙ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4305&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua758 | LATIN CAPITAL LETTER Q WITH DIAGONAL STROKE | https://mufi.info/m.php?p=muficharinfo&i=4305 |
| ꝙ | ![ꝙ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4304&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua759 | LATIN SMALL LETTER Q WITH DIAGONAL STROKE | https://mufi.info/m.php?p=muficharinfo&i=4304 |
|  [quia] | ![](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4309&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ue8b3 | LATIN SMALL LETTER Q LIGATED WITH R ROTUNDA | https://mufi.info/m.php?p=muficharinfo&i=4309 |
| x̄ [Nasalstrich] | ![x̄](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4713&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0304 | COMBINING MACRON | https://mufi.info/m.php?p=muficharinfo&i=4713 |
| x̅ [Kürzungszeichen] | ![x̅](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4734&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0305 | COMBINING OVERLINE | https://mufi.info/m.php?p=muficharinfo&i=4734 |
|  ᷒ [-us] | ![ ᷒](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4753&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u1dd2 | COMBINING US ABOVE | https://mufi.info/m.php?p=muficharinfo&i=4753 |
|  ᷓ [^a] | ![ ᷓ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4748&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u1dd3 | COMBINING LATIN SMALL LETTER FLATTENED OPEN A ABOVE | https://mufi.info/m.php?p=muficharinfo&i=4748 |
| ◌᷑ [-ur] | ![◌᷑](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4752&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u1dd1 | COMBINING UR ABOVE | https://mufi.info/m.php?p=muficharinfo&i=4752 |
| ◌ͥ [^i] | ![◌ͥ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4672&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0365 | COMBINING LATIN SMALL LETTER I | https://mufi.info/m.php?p=muficharinfo&i=4672 |
| ◌ͦ [^o] | ![◌ͦ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4684&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \u0366 | COMBINING LATIN SMALL LETTER O | https://mufi.info/m.php?p=muficharinfo&i=4684 |
| ◌ͧ [^u] | ![◌ͧ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4701&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) |\u0367| COMBINING LATIN SMALL LETTER U | https://mufi.info/m.php?p=muficharinfo&i=4701 |
| Ꝝ | ![Ꝝ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4776&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua75c | LATIN CAPITAL LETTER RUM ROTUNDA | https://mufi.info/m.php?p=muficharinfo&i=4776 |
| ꝝ | ![ꝝ](https://mufi.info/db-imgtxt.php?t=mufi_char&c=mufichar&i=4775&pt=50&x=80&y=80&fg=102020&align=centre&ypad=10) | \ua75d | LATIN SMALL LETTER RUM ROTUNDA | https://mufi.info/m.php?p=muficharinfo&i=4775 |


### Transkribus structural tags

This script uses as set of structural tags to determain importance, place and role of text zones in Transkribus. In order to have this script to work, the folowing tags must be created and used in Transkribus.

* header (existing)
* footer (existing)
* marginalia (existing)
* column_1 (to be created)
* column_2 (to be created)
* chapter_count (to be created)
