import sexmachine.detector as gender

class GenderClassifier:
    def __init__(self):
        self.d= gender.Detector()

    def getGender(self,name):
        return self.d.get_gender(name)
