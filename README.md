# transpy

## Description
Transpy is a script designed to be used in the [Burchards Dekret Digital](https://www.adwmainz.de/projekte/burchards-dekret-digital/beschreibung.html) project, but can be adapted for usage in other contexts as well. It assumes an exist-db and Transkribus-based workflow, where transcriptions are created in Transkribus using special characters and enriched with a simple markup structure. The transcriptions are then exported as PAGE XML and post-processed using a generated list of abbreviations and rules specified in `config.py`. Finally, the transcriptions are transformed into TEI format according to the project's documentation.

## Installation
To install transpy, simply clone the repository and install the dependencies using pip:
```bash
git clone https://github.com/your/repo.git
pip install -r requirements.txt
```

## Prerequisites
### Configuration
Transpy uses three different configuration files: `exist_credentials.py`, `transkribus_credentials.py`, and `config.py`. Please rename the provided template files (`exist_credentials_template.py`, `transkribus_credentials_template.py`, and `config_template.py`) by removing the "_template" suffix. Then, provide the necessary credentials and adjust the folder structure and other settings in `config.py` according to your needs.

### Abbreviation-list
The script automatically expands abbreviated words identified by special characters. For abbreviation expansion, a list of abbreviations in JSON format is used. You can provide the abbreviation dictionary by creating a file named `abbreviation_dictionary.json` in the `resources` folder. If the abbreviation is not found there, rules are used as specified in `config.py`. 

### Special characters
Transpy uses a predefined set of special Unicode characters that are recommended for transcribing manuscripts in Transkribus. These characters represent common phenomena found in medieval manuscripts and are based on the MUFI (Medieval Unicode Font Initiative) recommendations. The script relies on the usage of these special characters in your Transkribus transcriptions.

The table below shows some of the special characters used in transpy, along with their glyph, codepoint, MUFI name, and MUFI link:

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

This script relies on a set of structural tags in Transkribus to determine the importance, place, and role of text zones. These tags need to be created and used in Transkribus for the script to work properly. The following tags are required:

* `header` (existing): Used to mark the header section of the manuscript.
* `footer` (existing): Used to mark the footer section of the manuscript.
* `marginalia` (existing): Used to mark marginalia or notes in the manuscript.
* `column_1` (to be created): This tag should be created and used to mark the first column of text in the manuscript.
* `column_2` (to be created): This tag should be created and used to mark the first column of text in the manuscript.
* `chapter_count` (to be created): This tag should be created and used to mark the chapter count or numbering in the manuscript.

Make sure to apply these tags appropriately in your Transkribus documents according to the structure and content of the manuscript.

## Usage
To use this script, you need to call it from the command line (CLI) and provide specific parameters for the manuscript to be processed. The parameters include the manuscript's sigla (based on the specified values in config.py) and the book number. Additionally, you need to specify the Transkribus page range, the first folio of the section, and the IIIF canvas number.

Here's an example command to run the script:

```bash
python bdd.py B 7 282-291 139v 236435 -dl

```

The -dl flag indicates whether the PAGE XML needs to be downloaded from Transkribus or if existing XML files can be used.

It's important to ensure that there is a corresponding folder for the book to be processed in the documents directory, as well as an output folder to store the generated output files. For example, if you're processing book 7, there should be a folder named `07` in the `documents` directory.

Ensure that you have provided the necessary credentials in the `exist_credentials.py` and `transkribus_credentials.py` files, as mentioned in the prerequisites section of the README.