import pandas as pd
# from nltk.corpus import wordnet
# import gender_classification
# import math
import re
import sys
import helper
import clustering
import genderClassification
import demonynClassification
import os

def containArticle(words):
    if 'a' in words or 'an' in words or 'the' in words:
        return True
    else:
        return False

def getCoreference(coreference, corefRadius):
    genderObj = genderClassification.GenderClassifier()
    # genderD = genderOj.d


    for index, row in df.iterrows():
        df.loc[index, 'pronounType'] = False
        words = row['words']
        headnoun = row['headNoun']
        # feature pronoun type
        if row['headNoun'] in pronounList:
            df.loc[index, 'pronounType'] = True
        # feature article
        wordList = words.strip().split()
        if 'a' in wordList or 'an' in wordList:
            df.loc[index, 'article'] = 'INDEF'
        elif 'the' in wordList:
            df.loc[index, 'article'] = 'DEF'
        else:
            df.loc[index, 'article'] = 'NONE'
        # feature appositive
        df.loc[index,'appositive'] = 'NO'
        # feature Number
        if headnoun.endswith('s') and headnoun not in pronounList:
            df.loc[index, 'number'] = 'PLURAL'
        else:
            df.loc[index, 'number'] = 'SING'
        # Feature Proper Name
        for word in wordList:
            if word[0].isupper():
                isProperName = True
            else:
                isProperName = False
                break
        if isProperName:
            df.loc[index, 'properName'] = 'YES'
        else:
            df.loc[index, 'properName'] = 'NO'

        if row['words'] in coreference.NER:
            # row['semanticClass'] = coreference.NER[row['words']]
            df.loc[index,'semanticClass'] = coreference.NER[row['words']]
        else:
            df.loc[index, 'semanticClass'] = 'OBJECT'

        firstName = word.split()[0]
        if isinstance(firstName,str):
            if genderObj.getGender(firstName) == 'female':
                df.loc[index, 'gender'] = 'Female'
            elif genderObj.getGender(firstName) == 'male':
                df.loc[index, 'gender'] = 'Male'
            else:
                df.loc[index, 'gender'] = 'NONE'

        df.loc[index, 'demonym'] = 'False'
    for index, row in df.iterrows():
        if row['semanticClass'] == 'HUMAN' or row['semanticClass'] == 'ANIMAL':
            df.loc[index, 'animacy'] = 'ANIM'
        else:
            df.loc[index, 'animacy'] = 'INANIM'
    # #print df
    distanceClusterProcessing(df, coreference,corefRadius)


def isAppositive(np1, np2, coref):
    regex = np1 + '[ ]*,[ ]*' + np2
    p = re.compile(regex)  # define pattern
    text = coref.fullText  # whole document text
    if len(p.findall(text)) > 0:
        return True
    return False


def wordSubsumes(wordList1, wordList2):
    regex = ' [ ]*'.join(words for words in wordList2)
    p = re.compile(regex)  # define pattern
    text = " ".join(word for word in wordList1)  # whole document text
    if len(p.findall(text)) > 0:
        return True
    return False


def allNPsCompatible(cluster,c1,c2,df, i, j, lengthOfDF, r):
    # #print cluster
    # #print len(cluster)
    # #print c1
    # #print c2

    for word1 in cluster[c1]:
        for word2 in cluster[c2]:
            if calculateDistance(df,df[df['words'] == word1].index.tolist()[0], df[df['words'] == word2].index.tolist()[0], word1, word2, lengthOfDF, r) == sys.maxint:
                return False
    return True


def formCluster(df, distanceMatrix, cluster, r):
    # #print 'a'
    lengthOfDF = len(df.index)
    for j, row_j in df.iterrows():
        for i, row_i in df.iterrows():
            if i != j:
                # d = calculateDistance(df, i, j, row_i['words'], row_j['words'], lengthOfDF, r)
                d = distanceMatrix[i][j]
                # #print row_i['words']+","+ row_j['words'] + "," +str(d)
                for e in cluster:
                    if row_i['words'] in e:
                        c1 = cluster.index(e)
                    if row_j['words'] in e:
                        c2 = cluster.index(e)
                if d < r and allNPsCompatible(cluster, c1, c2, df, i, j, lengthOfDF, r):
                    # if d < r :
                    cluster[c1].extend(cluster[c2])
                    # del cluster[c2]
    # #print cluster


def distanceClusterProcessing(df,coreference, corefRadius):
    r = corefRadius
    lengthOfDF = len(df.index)
    distanceMatrix = [[0 for x in range(lengthOfDF)] for y in range(lengthOfDF)]
    for i, row_i in df.iterrows():
        for j, row_j in df.iterrows():
            if i != j and distanceMatrix[i][j] == 0 :
                d = calculateDistance(df, coreference,i, j, row_i['words'],row_j['words'], lengthOfDF, r)
                distanceMatrix[i][j] = d
                # distanceMatrix[j][i] = d

    # formCluster(df, distanceMatrix, cluster, r)
    # #print distanceMatrix

    cluster = clustering.Cluster(r, distanceMatrix)
    cluster.makecluster()
    clusters = cluster.clusterSetList
    # print clusters
    for cl in clusters:
        if len(cl) > 0:
            clSorted = sorted(cl)
            currentid = -1
            for c in clSorted:
                if currentid > -1 and not str(currentid).startswith('NEW'):
                    df.loc[c, 'RefId'] = currentid
                    if not df.loc[c,'Id'].startswith('NEW'):
                        currentid = df.loc[c, 'Id']
                else:
                    if str(currentid).startswith('NEW'):
                        df.loc[c, 'RefId'] = currentid
                        currentid = df.loc[c, 'Id']
                    elif currentid == -1:
                        df.loc[c, 'RefId'] = df.loc[c, 'Id']
                        currentid = df.loc[c, 'RefId']
    # #print clusters

def calculateDistance(df,coreference, indexI, indexJ, wordI, wordJ, length, r):
    d = 0
    demonym = demonynClassification.DemonymClassify()
    demonym.createDemonym()

    wordList_i = wordI.strip().split()
    wordList_j = wordJ.strip().split()

    lenWordi = len(set(wordList_i))
    lenWordj = len(set(wordList_j))
    matchWordCount  = len(set(wordList_i) & set(wordList_j))

    if wordI == wordJ:
        return -1

    if wordSubsumes(wordList_i, wordList_j):
        # return -1
        d += 10

    if isAppositive(wordI, wordJ, coreference):
        return -1

    if demonym.isDemonym(wordI, wordJ):
        return -1

    # if wordSubsumes(wordList_i, wordList_j) and df['semanticClass'].loc[indexI] == df['semanticClass'].loc[indexJ]:
    #     d += 7
    #
    # if df['gender'].loc[indexI] == df['gender'].loc[indexJ] and df['gender'].loc[indexI] != 'NONE' and df['semanticClass'].loc[indexI] == df['semanticClass'].loc[indexJ]:
    #     d += 5

    d += 10 * ((lenWordi +lenWordj -2*matchWordCount)/float(max(lenWordj,lenWordi)))

    if df['headNoun'].loc[indexI] != df['headNoun'].loc[indexJ]:
        d += 1

    d += 5 * (abs(df['position'].loc[indexI] - df['position'].loc[indexJ]) / (float(length -1)))

    if df['pronounType'].loc[indexI] != df['pronounType'].loc[indexJ] and df['pronounType'].loc[indexI]:
        d += r

    if df['article'].loc[indexJ] == 'INDEF' and not isAppositive(wordI, wordJ, coreference):
        d += r

    if df['semanticClass'].loc[indexI] != df['semanticClass'].loc[indexJ]:
        return sys.maxint

    if df['gender'].loc[indexI] != df['gender'].loc[indexJ] and df['gender'].loc[indexI] != 'NONE' and df['gender'].loc[indexJ] != 'NONE':
        return sys.maxint

    if df['animacy'].loc[indexI] != df['animacy'].loc[indexJ]:
        return sys.maxint

    if df['properName'].loc[indexI] == df['properName'].loc[indexJ] and df['properName'].loc[indexJ] == 'YES' and len(set(wordList_j) & set(wordList_i)) == 0:
        return sys.maxint

    if df['number'].loc[indexI] != df['number'].loc[indexJ]:
        return sys.maxint
    return d

def makePronounSeperate(words, pronounList):
    for word in words:
        for w in word.split( ):
            if w in pronounList:
                # words.append(w)
                words[words.index(word)] = word.replace(w,'')
                # #print words

if __name__ == "__main__":
    score = 10
    corefRadius = 20
    listofFiles = sys.argv[1]
    responseDir = sys.argv[2]
    coreference = helper.CoReferenceHandler()
    coreference.initializeConll()
    coreference.initializeSpacy()

    pronounList = coreference.pronounList

    with open(listofFiles, 'r') as file:
        for line in file:
            coreference.cleanData()
            coreference.inputFile = line.strip().replace('\n','')
            coreference.outputFile = responseDir + os.path.basename(coreference.inputFile).replace('.crf','.response')
            coreference.parseDocument()
            coreference.extractNERsentence()
            # #print coreference.fullText

            words = []
            corefIdList = []
            for each_obj in coreference.nounPhrase:
                words.append(each_obj.npPhrase)
                corefIdList.append(each_obj.corefId)

            words = [word.strip() for word in words]
            #print words

            df = pd.DataFrame(words, columns=['words'])
            df['headNoun'] = df['words'].map(lambda x: x.lower().split()[-1])
            df['position'] = df.index + 1
            df['semanticClass'] = 'OBJECT'
            for index, row in df.iterrows():
                df.loc[index,'Id'] = corefIdList[index]
            df['RefId'] = -1

            getCoreference(coreference, corefRadius)
            # print df[100:240]
            columnReturnList = ['words','Id','RefId']
            slicedDF = df[columnReturnList]
            coreference.writeOutput(slicedDF)
            #print slicedDF


