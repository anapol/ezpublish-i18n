# take translation strings defined in oldfile and, make a simple dict from them, then apply to a ts file. Case insensitive.
# *very* dirty one-off right now...


siteroot = "/somewhere/to/example.com/"
newfile = siteroot + "ezpublish-i18n/translations/cze-CZ/translation.ts"
oldfile = siteroot + "ezpublish-i18n/translations/cze-CZ/translation.ts.old"
result = siteroot + "ezpublish-i18n/translations/cze-CZ/translation.ts.merged"
pickleddict = siteroot + "ezpublish-i18n/translations/cze-CZ/pickleddict.pik"

root = siteroot + "extension/ezwebin/translations/cze-CZ/"
root = siteroot + "extension/ezdemo/translations/cze-CZ/"
result=root+"translation.ts.merged"
newfile=root+"translation.ts"


import xml.etree.ElementTree as etree
newtree = etree.parse(newfile)
oldtree = etree.parse(oldfile)

def processOldTranslations():
    oldroot = oldtree.getroot()
    oldtranslations = {}
    for c in oldroot.findall('context'):
        for message in c.findall('message'):
            string = message.find('source').text
            translation = message.find('translation').text
            if not translation:
                continue
            translationlist = oldtranslations.setdefault(string.lower(), [])
            if translation.lower() not in [t.lower() for t in translationlist]:
                translationlist.append(translation)

    newdict = {}
    for msg, tslist in oldtranslations.items():
        if len(tslist) > 1:
            print "========"
            print msg
            for idx, val in enumerate(tslist):
                print "%s: %s" % (idx, val)
            h = raw_input("Which?")
            h = int(h)
            newdict[msg] = tslist[h]
        else:
            if len(tslist) == 1:
                newdict[msg] = tslist[0]
    import pickle
    pickle.dump(newdict, open(picklekleddict, "w"))

# load pickled data and update new translations

import pickle
oldTranslations = pickle.load(open(pickleddict))
newroot = newtree.getroot()
for c in newroot.findall('context'):
    name = c.find('name')
    if name is None:
        print "Hey, no name for context", c
    else:
        name = name.text
        for message in c.findall('message'):
            source = message.find('source').text
            translationel = message.find('translation')
            if translationel is None:
                translationel = etree.SubElement(message, 'translation')
            translation = translationel.text
            if source.lower() in oldTranslations:
                translationel.text = oldTranslations[source.lower()]


newxml = etree.tostring(newroot, encoding="utf-8", method="xml")

f = open(result, "w")
f.write(newxml)
f.close()
