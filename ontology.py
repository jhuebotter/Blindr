import numpy as np

kwargs = {'weight':23,"speed":95000,"actv":4500}
kwargs2 = {'weight':24,"speed":89000,"actv":3500}
kwargs3 = {'weight':25,"speed":76000,"actv":6500}



class Animal:
    id = ""
    matrix = []

    def __init__(self,id,**kwargs):
        self.id = id
        for key,value in kwargs.items():
            print(key,value)
            setattr(self, key, value)
            self.matrix.append(value)
        self.matrix = np.array(self.matrix)
        print("A clone has been made")


class Group:
    id = ""
    animals = []
    mean_matrix = []

    def __init__(self,id_no):
        self.id = id_no

    def update_mean_features(self):
        for i in range(0,len( self.animals )):
            self.mean_matrix.append( self.animals[i].matrix )
        print(self.mean_matrix)





class Experimental_group:
    name = ""
    groups = []

    def __init__(self,id,no_of_groups):
        self.id = id
        for i in range (no_of_groups):
            group = Group(i)
            self.groups.append(group)

    def assign(self, anim,flag):
        print("how many groups ",len(self.groups))

        ###only the first times
        for i in range(0,len(self.groups)):
            if not self.groups[i].animals:
                self.groups[i].animals.append(anim)
                print(i)

                break

        if flag is True:
            self.groups[0].animals.append(anim)







#TEST
mouse = Animal("01", **kwargs)
mouse2 = Animal("02", **kwargs2)
mouse3 = Animal("03", **kwargs3)
mouse4 = Animal("03", **kwargs3)


experiment = Experimental_group("test_case", 2)

experiment.assign(mouse,False)
experiment.assign(mouse2,False)
experiment.assign(mouse3, True)
experiment.assign(mouse4, True)



experiment.groups[0].update_mean_features()



#print(vars(mouse))
