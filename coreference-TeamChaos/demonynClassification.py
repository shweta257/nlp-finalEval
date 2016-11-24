class DemonymClassify:
    def __init__(self):
        self.fileName = "demonyms.txt"
        self.demonyms = {}


    def createDemonym(self):
        with open(self.fileName) as f:
            for line in f:
                line = line.lower().split()
                keyName = line[0].lower()
                if self.demonyms.has_key(keyName):
                    continue
                else:
                    self.demonyms[keyName] = line



    def isDemonym(self, noun1, noun2):
        # print "here"
        noun1 = noun1.lower()
        noun2 = noun2.lower()
        if self.demonyms.has_key(noun1):
            if noun2 in self.demonyms[noun1]:
                return True
        elif self.demonyms.has_key(noun2):
            if noun1 in self.demonyms[noun2]:
                return True
        return False



if __name__=="__main__":
    demonym = DemonymClassify()
    demonym.createDemonym()
    # print demonym.demonyms
    # print demonym.demonyms.has_key('america')
    # print demonym.isDemonym('american','americans')