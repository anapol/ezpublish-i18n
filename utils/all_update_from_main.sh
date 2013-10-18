#!/bin/bash

TSFILES="../translations/cze-CZ/translation.ts
../../extension/aabagrycz/translations/cze-CZ/translation.ts
../../extension/ezdemo/translations/cze-CZ/translation.ts
../../extension/ezwebin/translations/cze-CZ/translation.ts
../../extension/ezchat/translations/cze-CZ/translation.ts
../../extension/ezmultiupload/translations/cze-CZ/translation.ts
../../extension/ezoe/translations/cze-CZ/translation.ts
../../extension/ezstyleeditor/translations/cze-CZ/translation.ts
../../extension/ezwt/translations/cze-CZ/translation.ts
"

IFS="
"
for FILENAME in $TSFILES; do
    ./aaeztranslator.py --tsUpdate "$FILENAME" ./cze_CZ.main3
done
