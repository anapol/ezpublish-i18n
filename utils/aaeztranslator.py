#!/usr/bin/env python

# a couple of functions to help translating multiple ezpublish ts files using a master
# dictionary


siteroot = "/Users/petr/dev2/bagry.cz/site/bagry.cz/"

generalLanguageDict = siteroot + "ezpublish-i18n/translations/cze-CZ/cze_CZ.pickleddict"

ezpublishts = siteroot + "ezpublish-i18n/translations/cze-CZ/translation.ts"
ezdemots = siteroot + "extension/ezdemo/translations/cze-CZ/translation.ts"
ezwebints = siteroot + "extension/ezwebin/translations/cze-CZ/translation.ts"
aabagryczts = siteroot + "extension/aabagrycz/translations/cze-CZ/translation.ts"


import os
import xml.etree.ElementTree as etree
import pickle


def addXMLTranslationsFromTSFileToIntermediaryDictionary(tsFilePath, itermediaryDictionaryPath):
    """
    Adds all translations from a .ts file tsFilePath to a pickled dictionary
        term.lower(): [translation1, translation2, ...]
    stored at itermediaryDictionaryPath.
    """
    if os.path.exists(itermediaryDictionaryPath):
        intermediaryFile = open(itermediaryDictionaryPath)
        intermediaryDict = pickle.load(intermediaryFile)
        intermediaryFile.close()
    else:
        intermediaryDict = {}
    tstree = etree.parse(tsFilePath)
    tsroot = tstree.getroot()
    for c in tsroot.findall('context'):
        for message in c.findall('message'):
            string = message.find('source').text
            translation = message.find('translation').text
            if not translation:
                continue
            translationlist = intermediaryDict.setdefault(string.lower(), [])
            if translation.lower() not in [t.lower() for t in translationlist]:
                translationlist.append(translation)
    intermediaryFile = open(itermediaryDictionaryPath, "w+")
    pickle.dump(intermediaryDict, intermediaryFile)
    intermediaryFile.close()


import plistlib
def intermediaryToPlist(itermediaryDictionaryPath, plistPath, currentTranslationDictionaryPath=None):
    """
    Converts intermediary to plist, phrases ordered by relevance, with hints.
    """
    hints = {}
    if currentTranslationDictionaryPath:
        hints = pickle.load(open(currentTranslationDictionaryPath))
    imd = pickle.load(open(itermediaryDictionaryPath))
    for key, value in imd.items():
        hint = hints.get(key)
        if hint is not None:
            if hint in value:
                value.remove(hint)
            value.insert(0, hint)

    print "To file:", plistPath
    plistlib.writePlist(imd, plistPath)


def plistToMain(plistPath, newTranslationDictionaryPath):
    """
    Plist to main.
    """
    im = plistlib.readPlist(plistPath)
    mainDict = {}
    for key, value in im.items():
        mainDict[key] = value[0]
    pickle.dump(mainDict, open(newTranslationDictionaryPath, "w"))


def createNewTranslationDictionary(newTranslationDictionaryPath, itermediaryDictionaryPath, currentTranslationDictionaryPath=None):
    """
    Creates a new translation dictionary at newTranslationDictionaryPath.
    
    itermediaryDictionaryPath is a combined dictionary from all the .ts files that are to be translated.

    Takes an optional currentTranslationDictionaryPath for a current translation that serves as hinting
    help.
    
    Interactively asks for any term that has more than one translation,
    """
    hints = {}
    if currentTranslationDictionaryPath:
        hints = pickle.load(open(currentTranslationDictionaryPath))
    imd = pickle.load(open(itermediaryDictionaryPath))
    newdict = {}
    for msg, tslist in imd.items():
        if len(tslist) > 1:
            hint = hints.get(msg)
            print "========"
            print msg
            for idx, val in enumerate(tslist):
                print "%s%s: %s" % (idx, "*" if val == hint else "", val)
            h = ""
            while 1:
                h = raw_input("Which?")
                if h == "" and hint:
                    newdict[msg] = hint
                    pickle.dump(newdict, open(newTranslationDictionaryPath, "w"))
                    break
                else:
                    if len(h) > 2:
                        newdict[msg] = unicode(h, "utf-8")
                    else:
                        h = int(h)
                        newdict[msg] = tslist[h]
                    pickle.dump(newdict, open(newTranslationDictionaryPath, "w"))
                    break
        else:
            if len(tslist) == 1:
                newdict[msg] = tslist[0]
    pickle.dump(newdict, open(newTranslationDictionaryPath, "w"))


def updateTSFileWithDictionary(tsFilePath, dictionaryPath=None):
    # load pickled data and update new translations
    originalTree = etree.parse(tsFilePath)

    if dictionaryPath is None:
        dictionary = {}
    else:
        dictionary = pickle.load(open(dictionaryPath))

    for c in originalTree.findall("context"):
        name = c.find("name")
        if name is None:
            print "Hey, no name for context", c
        else:
            name = name.text
            for message in c.findall('message'):
                source = message.find('source').text
                if source is None:
                    continue
                translationel = message.find('translation')
                if translationel is None:
                    translationel = etree.SubElement(message, 'translation')
                translation = translationel.text
                if source.lower() in dictionary:
                    translationel.text = dictionary[source.lower()]
    newxml = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
"""
    newxml += etree.tostring(originalTree.getroot(), encoding="utf-8", method="xml")
    newxml += "\n"
    f = open(tsFilePath, "w")
    f.write(newxml)
    f.close()


def compactTS(tsFilePath):
    originalTree = etree.parse(tsFilePath)

    for c in originalTree.findall("context"):
        name = c.find("name")
        if name is None:
            print "Hey, no name for context", c
        else:
            name = name.text
            sourcesInContext = []
            for message in c.findall('message'):
                source = message.find('source').text
                if source is None:
                    c.remove(message)
                    continue
                elif source in sourcesInContext:
                    c.remove(message)
                    continue
                else:
                    sourcesInContext.append(source)

                locationel = message.find('location')
                if locationel is not None:
                    message.remove(locationel)

    newxml = """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE TS>
        """
    newxml += etree.tostring(originalTree.getroot(), encoding="utf-8", method="xml")
    newxml += "\n"
    f = open(tsFilePath, "w")
    f.write(newxml)
    f.close()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Manage a master dictionary for a language from a set of .ts files. Update .ts files based on a curated master dictionary.

a) Add .ts files to an intermediary dictionary, holding
   all the (lowercased) translations for a source message.
b) Process the intermediary dictionary to finalized by interactively
   picking preferred translation if multiple translations are present.
   
   Possibly use hinting based on an existing finalized dictionary.
c) Compact and translate .ts files using the finalized dictionary.
""")
    parser.add_argument('--tsToIntermediary', nargs=2, help='--tsToIntermediary tsfile intermediaryFile')
    parser.add_argument('--intermediaryToMain', nargs=2, help='Intermediary to main')
    parser.add_argument('--hints', nargs=1, help='Former main for hinting')
    parser.add_argument('--tsCompact', nargs=1, help='Compact a TS file (after ezlupdate)')
    parser.add_argument('--tsUpdate', nargs=2, help='Update a TS file with main dict')
    parser.add_argument('--intermediaryToPlist', nargs=2, help='Intermediary to plist')
    parser.add_argument('--plistToMain', nargs=2, help='Plist to main')


    args = parser.parse_args()
    if args.tsToIntermediary:
        tsFile, intermediaryDictFile = args.tsToIntermediary
        print "Adding ", tsFile, "to", intermediaryDictFile
        addXMLTranslationsFromTSFileToIntermediaryDictionary(tsFile, intermediaryDictFile)
    if args.intermediaryToMain:
        intermediaryDictFile, mainDictFile = args.intermediaryToMain
        print "Adding intermediaryToMain ", intermediaryDictFile, "to", mainDictFile
        hintsFile = None
        if args.hints:
            hintsFile = args.hints[0]
        createNewTranslationDictionary(mainDictFile, intermediaryDictFile, hintsFile)
    if args.tsCompact:
        tsFile = args.tsCompact
        print "Compacting ", tsFile
        compactTS(tsFile)
    if args.tsUpdate:
        tsFile, mainDictFile = args.tsUpdate
        print "Updating ", tsFile, "with", mainDictFile
        updateTSFileWithDictionary(tsFile, mainDictFile)
    if args.intermediaryToPlist:
        intermediaryDictFile, plistPath = args.intermediaryToPlist
        print "Adding intermediaryToPlist ", intermediaryDictFile, "to", plistPath
        hintsFile = None
        if args.hints:
            hintsFile = args.hints[0]
        intermediaryToPlist(intermediaryDictFile, plistPath, hintsFile)
    if args.plistToMain:
        plistPath, mainDictFile = args.plistToMain
        print "Creating ", mainDictFile, "from", plistPath
        plistToMain(plistPath, mainDictFile)








