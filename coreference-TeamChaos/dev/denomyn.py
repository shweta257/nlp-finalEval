# -*- coding: utf-8 -*-
#!/pkg/ldc/bin/python2.5
#-----------------------------------------------------------------------------
# Name:        auxiliarLaboCase.py
#
# Author:      Horacio
#
# Created:     2013/09/30
# skeleton programa for extracting demonyms
#-----------------------------------------------------------------------------

import re
from string import *
import sys

##using NLTK toolbox (Natural Language Tool Kit), http://nltk.org/
##is not strictily necesary but can simplify some of your tasks

from nltk import *
import locale

##For facilitating access to Wikipedia (WP) it is useful to use the python module
##wikitools (http://code.google.com/p/python-wikitools/)
##from which the following files should be imported
##The main aim of wikitools is providing a python wrapper to the services of
##mediawiki's API, in charge of the corresponding processes
##mediawiki api: http://www.mediawiki.org/wiki/API
##For knowing about the available functions the best way is to inspect the code
##in the files imported.

from wikitools import wiki
from wikitools import api
from wikitools import page
from wikitools import category

##If you use a WP other than English thre is a bug in wikitools, ask to me if
##you need help for solving it

##The following is needed for dealing with Unicode

locale.setlocale(locale.LC_ALL, '')

##constants

##We define a language using the coding in WP

lang = 'en'

##Here are the pages in WP corresponding to "Demonym" for Spanish and English


demonymPages = {
    'en':u'Demonym',
    'es':u'Anexo:Gentilicios'}

##Also for Spanish and English we define the addresses of the corresponding APIs
##for accessing the WP


wikiAPI = {
    'en': "http://en.wikipedia.org/w/api.php",
    'es': "http://es.wikipedia.org/w/api.php"}

##classes

##functions

##For detecting coding and transforming to Unicode

##########################################################################
# Guess Character Encoding
##########################################################################

# adapted from io.py in the docutils extension module (http://docutils.sourceforge.net)
# http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html

def guess_encoding(data):
    """
    Given a byte string, attempt to decode it.
    Tries the standard 'UTF8' and 'latin-1' encodings,
    Plus several gathered from locale information.

    The calling program *must* first call::

        locale.setlocale(locale.LC_ALL, '')

    If successful it returns C{(decoded_unicode, successful_encoding)}.
    If unsuccessful it raises a C{UnicodeError}.
    """
    successful_encoding = None
    # we make 'utf-8' the first encoding
    encodings = ['utf-8']
    #
    # next we add anything we can learn from the locale
    try:
        encodings.append(locale.nl_langinfo(locale.CODESET))
    except AttributeError:
        pass
    try:
        encodings.append(locale.getlocale()[1])
    except (AttributeError, IndexError):
        pass
    try:
        encodings.append(locale.getdefaultlocale()[1])
    except (AttributeError, IndexError):
        pass
    #
    # we try 'latin-1' last
    encodings.append('latin-1')
    for enc in encodings:
        # some of the locale calls
        # may have returned None
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc

        except (UnicodeError, LookupError):
            pass
        else:
            break
    if not successful_encoding:
         raise UnicodeError(
        'Unable to decode input data.  Tried the following encodings: %s.'
        % ', '.join([repr(enc) for enc in encodings if enc]))
    else:
         return (decoded, successful_encoding)


##initial collection of rules (only one but very productive)
##it detects the pair <u'Africa', u'African'> from the string:
##u'*[[Africa]] \u2192 African' (printed as *[[Africa]] â†’ African)
##The two fields to extract (the location and the demonym) are described as([\w]+)
##Look at re python documentation for details

extractionRules = [
    re.compile(u'^\*\[\[([\w]+)\]\] \u2192 ([\w]+)$',re.L)]

##inicializing the list of triples to extract
##The elements of each triple are:
##    location
##    demonym
##    identifier of the rule applied (just the index in the list)
##The identifier is useful for computing the coverage of each rule

demonymTriples = []

# An object of the class Wiki associated to the WP is built

site = wiki.Wiki(wikiAPI[lang])

##An object  of the class Page associated to the demonyms page

pageDemonym = page.Page(site,demonymPages[lang])

##The lines of the page are read and translated into  Unicode
##We print the number of lines

lines=pageDemonym.getWikiText().split('\n')
lines = map(lambda x:guess_encoding(x)[0],lines)
len(lines)

##In my test (19/09/2013) I collected 733 lines, obviously
##WP can change and the results can be different

##I iterate over all the lines and I appply all the rules.
##Whe athe application of une rule succeeds I discard the following ones
##The lines from which no rule is succesful are printed

for linea in lines:
    for ir in range(len(extractionRules)):
        r = extractionRules[ir]
        m = re.match(r,linea)
        if not m:
            print linea
            continue
        demonymTriples.append((m.group(1), m.group(2), ir))
        break
print len(demonymTriples), 'triples have been obtained '

##In my test  (19/09/2013) 295 triples were obtained, obviously
##WP can change and the results can be different.
