import sys



class Cluster():
    def __init__(self,radius, distanceMatrix):
        # self.distanceMatrix = [[ 0, 3, 5 ,6, 7],[3, 0, 2, 1, 8 ],[6, 2 , 0, 100,10],[5,1,100,0,7],[7,8,10,7,0]]
        self.distanceMatrix = distanceMatrix
        # print self.distanceMatrix
        self.clusterSetList = [set([i]) for i in range(0,len(self.distanceMatrix[0]))]
        self.newClusterList = {}
        # print self.clusterSetList
        self.radius = radius
        self.bitMatrix = [i for i in range(0,len(self.distanceMatrix[0]))]

    def mergeCluster(self, i,j):
        indexI = self.bitMatrix[i]
        indexJ = self.bitMatrix[j]
        # print indexI , indexJ
        if indexJ == indexI:
            return
        canmerge = True
        for eachElementI in self.clusterSetList[indexI]:
            for eachElementJ in self.clusterSetList[indexJ]:
                if self.distanceMatrix[eachElementI][eachElementJ] == sys.maxint:
                # if self.distanceMatrix[eachElementI][eachElementJ] == 20:
                    canmerge = False


        if canmerge != False:
            self.clusterSetList[indexI] = self.clusterSetList[indexI] | self.clusterSetList[indexJ]
            for eachElement in self.clusterSetList[indexJ]:
                self.bitMatrix[eachElement] = indexI

            self.clusterSetList[indexJ] = []

    def makecluster(self):
        for i in range(0,len(self.distanceMatrix)):
            for j in range(i+1, len(self.distanceMatrix[0])):
                # print self.distanceMatrix[i][j], i ,j
                if self.distanceMatrix[i][j] < self.radius:
                    self.mergeCluster(i,j)


    def makenewcluster(self):
        for i in range(0,len(self.distanceMatrix)):
            self.newClusterList[i] = []
            for j in range(0, len(self.distanceMatrix[0])):
                # print self.distanceMatrix[i][j], i ,j
                if self.distanceMatrix[i][j] < 10 and i != j:
                    self.newClusterList[i].append((j,self.distanceMatrix[i][j]))

    
if __name__=="__main__":
    cluster = Cluster()
    cluster.makecluster()
    # print cluster.clusterSetList