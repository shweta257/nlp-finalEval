import nltk
from xml.dom.minidom import parse
import xml.dom.minidom
from nltk.tag.stanford import StanfordNERTagger
from spacy.en import English
import re


class NPElement():
    def __init__(self, word, corefId, refId):
        self.npPhrase = word
        self.corefId = corefId
        self.refId = refId

class ChunkParser(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]

        self.tagger = nltk.TrigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word, pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word, pos), chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.conlltags2tree(conlltags)

class CoReferenceHandler():

    def __init__(self):
        self.inputFile = ''
        self.outputFile = ''
        self.inputText = ""
        self.outputText = ''
        self.responseText = ''
        self.fullText = ''
        self.NPChunker = ''
        self.counter = 1
        self.train_sents = ""
        self.coRefDict ={}
        self.nounPhrase = []
        self.NER = {}
        self.ignoreWordList = ['a', 'i']

        self.labels = { 'DATE':'TIME', 'GPE':'CITY', 'PERSON':'HUMAN', 'CARDINAL':'NUMBER',
                        'MONEY':'MONEY', 'ORG':'COMPANY'}
        self.pronounList = ['i', 'you', 'he', 'she', 'it', 'me', 'him', 'her', 'we', 'they', 'us', 'them', 'mine', 'yours',
                   'hers',
                   'ours', 'theirs', 'myself', 'yourself',
                   'himself', 'herself', 'itself', 'oneself', 'ourselves', 'yourselves', 'themselves', 'each other',
                   'one another', 'that', 'which', 'who',
                   'whose', 'whom', 'where', 'when', 'this', 'these', 'those', 'what', 'whatever', 'why', 'anything',
                   'anybody', 'anyone', 'something', 'somebody',
                   'someone', 'nothing', 'nobody', 'none', 'no one', 'his']

    def cleanData(self):
        self.inputFile = ''
        self.outputFile = ''
        self.inputText = ""
        self.outputText = ''
        self.responseText = ''
        self.fullText = ''
        self.counter = 1
        self.coRefDict = {}
        self.nounPhrase = []
        self.NER = {}

    def readFile(self):
        self.outputText =''
        with open(self.inputFile) as dictionary1:
            for lines in dictionary1:
                self.outputText += lines.replace('\n',' ')

        self.outputText = re.sub('\s+', ' ', self.outputText).strip()
        self.outputText = re.sub('\'+','',self.outputText).strip()
        self.outputText = self.outputText.replace('\'s', '')
        self.outputText = self.outputText.replace('\'', '')
       # print self.outputText

        # print self.inputText
    def writeOutput(self, slicedDF):
        start = 0
        end = 0;
        # self.outputText = re.sub('\s+', ' ', self.outputText).strip()
        # self.outputText = re.sub('\'+', '', self.outputText).strip()
        self.readFile()
        refTags = []
        corefIddict = {}
        problemdict = {}
        for index, row in slicedDF.iterrows():
            word = slicedDF.loc[index, 'words'].strip()
            corefId = slicedDF.loc[index, 'Id'].strip()
            refId = slicedDF.loc[index, 'RefId'].strip()

            if corefId.find('NEW') == -1 and refId.find('NEW') != -1:
                refTags.append(refId)

            if corefId != refId:
                corefIddict[corefId.strip()] = refId.strip()


        for index, row in slicedDF.iterrows():
            word = slicedDF.loc[index, 'words'].strip()
            corefId = slicedDF.loc[index, 'Id'].strip()
            refId = slicedDF.loc[index, 'RefId'].strip()


            if corefId in refTags:
                #print word
                end = self.outputText.find(word)
                if end == -1:
                    problemdict[corefId] = 1
                    continue
                self.responseText += self.outputText[start:end]
                newWord = ' <COREF ID=\"' + corefId.strip() + '\">' + word.strip() + '</COREF> '
                self.outputText = self.outputText[end:].replace(word, newWord, 1)
                end = len(newWord)
                self.responseText += self.outputText[start:end]
                self.outputText = self.outputText[end:]

            else:
                end = self.outputText.find(word) + len(word)
                if end == -1:
                    continue
                self.responseText += self.outputText[start:end]
                self.outputText = self.outputText[end:]




        self.responseText += self.outputText[start:]
        ##print self.responseText

        with open(self.outputFile, "w") as text_file:
            text_file.write(self.responseText)

        #print self.outputFile

        DOMTree = xml.dom.minidom.parse(self.outputFile)

        collection = DOMTree.documentElement
        # if collection.hasAttribute("TXT"):
        #     print "Root element : %s" % collection.getAttribute("TXT")

        self.coRefIds = collection.getElementsByTagName("COREF")

        for corefId in self.coRefIds:
            if corefId.hasAttribute("ID"):
                id = corefId.getAttribute("ID")
                if id in corefIddict and id.find('NEW') == -1:
                    if corefIddict[id] not in problemdict:
                        corefId.setAttribute("REF", corefIddict[id])


        with open(self.outputFile, 'wb') as f:
            DOMTree.writexml(f)

        #print "ref tags "
        #print refTags
        #print "problems dict"

        #print problemdict
        # print DOMTree.toxml()

    def writeFile(self, slicedDF):
        start = 0
        self.readFile()
        for index, row in slicedDF.iterrows():
            word = slicedDF.loc[index, 'words']
            corefId = slicedDF.loc[index, 'Id']
            refId = slicedDF.loc[index, 'RefId']

            if corefId.find('NEW') == -1 and corefId != refId:
                corefId = corefId.strip()
                tempword = '<COREF ID=\"' + corefId + '\">'
                # print tempword
                newWord = '<COREF ID=\"' + corefId + '\" ' + ' REF=\"' + refId.strip() + '\">'
                self.outputText = self.outputText.replace(tempword, newWord, 1)


            else:
                tempword = word.strip()
                tempword += ' '
                if self.outputText.find(tempword) == -1:
                    tempword = tempword.strip()
                    tempword = ' ' + tempword
                newWord = ' <COREF ID=\"' + corefId.strip() + '\">' + word.strip() + '</COREF> '
                self.outputText = self.outputText.replace(tempword, newWord, 1)

        #print self.outputText

        with open(self.outputFile, "w") as text_file:
            text_file.write(self.outputText)




    def extractNER(self):
        st = StanfordNERTagger('/usr/share/stanford-ner/classifiers/all.3class.distsim.crf.ser.gz',
             '/usr/share/stanford-ner/stanford-ner.jar')
        ap = st.tag(self.inputText.split())
        # print ap


    def extractNPSpacy(self):
        spacyObject = English(path='spacy')
        nerObject = spacyObject(self.inputText)
        # for np in nerObject.noun_chunks:
        #     print np
        #     # npchunk = str(np)
        #     # # print npchunk
        #     # npchunk = npchunk.replace('\n', ' ')
        #     # npchunk = npchunk.strip().split(' ')
        #     # npPhrase = ''
        #     # start = 0
        #     # # npPhrase = ' '.join(word.split('/')[0] for word in npchunk)
        #     # npPhrase = npPhrase + npchunk[0]
        #     # if npPhrase in self.pronounList:
        #     #     self.nounPhrase.append(npPhrase.strip())
        #     #     start = 1
        #     #
        #     # npPhrase = ''
        #     # prevWord = ''
        #     # for word in npchunk[start:]:
        #     #     if (len(prevWord) != 1 and len(word) != 1):
        #     #         npPhrase += ' '
        #     #     if (prevWord.lower() in ignoreWordList or word.lower() in ignoreWordList):
        #     #         npPhrase += ' '
        #     #     npPhrase = npPhrase + word
        #     #     prevWord = word
        #     #
        #     # npPhrase = npPhrase.strip()
        #     # if npPhrase != '':
        #     #     self.nounPhrase.append(npPhrase)
        #
        # print self.nounPhrase

    def initializeSpacy(self):
        self.spacyObject = English(path='spacy')

    def extractNERStanford(self):
        from nltk.tag import StanfordNERTagger

        stanford_ner_dir = '/home/shweta/stanford-ner-2015-04-20/'
        eng_model_filename = stanford_ner_dir + 'classifiers/english.muc.7class.distsim.crf.ser.gz'
        my_path_to_jar = stanford_ner_dir + 'stanford-ner.jar'

        st = StanfordNERTagger(model_filename=eng_model_filename, path_to_jar=my_path_to_jar)
        tag = st.tag(self.inputText.split())
        # print tag
        prevTag = ''

        for tuple in tag:
            if tuple[1] == 0:
                self.NER[tuple[0]] = 'OBJECTS'
            else:
                if(tuple[1] == prevTag):
                    fullPhrase = fullPhrase + ' ' + tuple[0]
                    prevTag = tuple[1]


            # if label == '':
            #     self.NER[self.inputText] = 'OBJECTS'
                # for obj in self.NER:
                #     print obj , self.NER[obj]

            # print tuple[0], tuple[1]

        # for obj in self.NER:
        #     print obj , self.NER[obj]


    def extractNERSpacy(self):
        # data_dir = os.environ.get('SPACY_DATA', LOCAL_DATA_DIR)
        nerObject = self.spacyObject(self.inputText)
        label =''
        for ent in nerObject.ents:
            #print ent,  ent.label_
            label = ent.label_
            if self.inputText not in self.NER:
                if str(ent.label_) in self.labels:
                    self.NER[self.inputText] = self.labels[str(ent.label_)]
                else:
                    self.NER[self.inputText] = 'OBJECTS'

        if label == '':
            self.NER[self.inputText] = 'OBJECTS'
        # for obj in self.NER:
        #     print obj , self.NER[obj]



    def parseDocument(self):
        #DOMTree = xml.dom.minidom.parse("dev/text.crf")
        DOMTree = xml.dom.minidom.parse(self.inputFile)

        collection = DOMTree.documentElement
        # if collection.hasAttribute("TXT"):
        #     print "Root element : %s" % collection.getAttribute("TXT")

        self.inputText = ""
        for data in collection.childNodes:
            if data.nodeName == "COREF":
                self.inputText =  ((data.childNodes)[0].wholeText)
                self.inputText = self.inputText.replace('\'s', '')
                self.inputText = self.inputText.replace('\'', '')
                npElement = NPElement(self.inputText, data.getAttribute("ID"), '')
                self.nounPhrase.append(npElement)
                self.fullText += self.inputText

            else:
                self.inputText = data.wholeText
                self.inputText = self.inputText.replace('\'s', '')
                self.inputText = self.inputText.replace('\'', '')
                self.fullText += self.inputText
                self.outputText += self.inputText
                self.extractNP()


        #
        # print self.inputText
        #
        # # Get all the movies in the collection



    def extractNPfromChunk(self, t):
        try:
            t.label()
        except AttributeError:
            return
        else:

            if t.label() == 'NP':
                npchunk = str(t)
                npchunk = npchunk.replace('(NP', '').replace(')', '')
                # print npchunk

                npchunk = npchunk.strip().split(' ')
                npPhrase = ''
                npPhrase = ' '.join(word.split('/')[0] for word in npchunk)
                npPhrase = re.sub('\`+','',npPhrase).strip()
                npPhrase = npPhrase.strip().split(' ')


                # start = 0
                # Code to add feature of breaking words with single sentence
                # npPhrase = npPhrase + npchunk[0].split('/')[0]
                # if npPhrase in self.pronounList:
                #     self.nounPhrase.append(npPhrase.strip())
                #     start = 1
                #
                newnpPhrase = ''
                prevWord = ''
                for word in npPhrase:
                    newnpPhrase = newnpPhrase + word

                    if (len(word) != 1):
                        newnpPhrase += ' '
                    if(prevWord.lower() in self.ignoreWordList or word.lower() in self.ignoreWordList):
                        newnpPhrase += ' '
                    prevWord = word
                newnpPhrase = newnpPhrase.strip()
                if len(newnpPhrase) != 1 or newnpPhrase.lower() in self.ignoreWordList:
                    # print newnpPhrase
                    npElement = NPElement(newnpPhrase, 'NEW'+str(self.counter), '')
                    self.nounPhrase.append(npElement)
                    self.counter += 1

            else:
                for child in t:
                    self.extractNPfromChunk(child)

    def initializeConll(self):
        from nltk.corpus import conll2000
        self.test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
        self.train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
        self.NPChunker = ChunkParser(self.train_sents)

    def extractNP(self):
        # get training and testing data


        rawtext = self.inputText
        sentences = nltk.sent_tokenize(rawtext)  # NLTK default sentence segmenter
        sentences = [nltk.word_tokenize(sent) for sent in sentences]  # NLTK word tokenizer
        sentences = [nltk.pos_tag(sent) for sent in sentences]  # NLTK POS tagger

        for sent in sentences:
            chunks = self.NPChunker.parse(sent)
            # print chunks
            self.extractNPfromChunk(chunks)


        # print self.nounPhrase
        #self.extractNERSpacy()
        # self.extractNER()

    def extractNERsentence(self):
        for each_obj in self.nounPhrase:
            self.inputText = each_obj.npPhrase
            if self.inputText == '':
                continue
            # print self.inputText
            self.inputText = self.inputText.decode('utf-8')
            self.extractNERSpacy()



if __name__=="__main__":
    coreference = CoReferenceHandler("sdd","sdsd")
    coreference.inputText = "Rami Eid is studying at Stony Brook University in NY"
    coreference.extractNERStanford()
    # coreference.initializeConll()
    # coreference.readFile()
    # coreference.parseDocument()
    # coreference.initializeSpacy()
    # coreference.extractNERsentence()
    # for eachelem in coreference.nounPhrase:
    #     print eachelem.npPhrase
    #
    # for eachkey in coreference.NER:
    #     print eachkey, coreference.NER[eachkey]
    #
    # # print coreference.NER
    #
    # print len(coreference.NER) , len(coreference.nounPhrase)

    # coreference.readFile()
    coreference.extractNERSpacy()
   # coreference.extractNP()
    #coreference.extractNPSpacy()
    #print coreference.nounPhrase

    #coreference.extractNERSpacy()


