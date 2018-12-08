import numpy as np
from scipy import stats


class Animal:

    def __init__(self,id_no,**kwargs):
        self.group_id = None
        self.id = id_no
        self.matrix = []
        for key,value in kwargs.items():
            setattr(self, key, value)
            self.matrix.append(value)
        self.matrix = np.array(self.matrix)
        print("created animal with ID:", self.id)


class Group:

    def __init__(self,id_no,n_feat):
        self.animals = []
        self.id = id_no
        self.n_feat = n_feat
        self.full_matrix = []
        self.mean_matrix = np.zeros(self.n_feat)
        self.sem_matrix = np.zeros(self.n_feat)
        self.animals_list = []
        print("created group with ID:", self.id)

    def assign(self, anim):
        self.animals.append(anim)
        #print("assigned animal", anim.id, "to group", self.id)
        anim.group_id = self.id
        self.update_mean_features()

    def release(self, anim):
        self.animals.remove(anim)
        #print("removed animal", anim.id, "from group", self.id)
        anim.group_id = None
        self.update_mean_features()     

    def update_mean_features(self):
        self.animals_list = [x.id for x in self.animals]
        self.full_matrix = []
        self.mean_matrix = []
        self.sem_matrix = []
        for animal in self.animals:
            self.full_matrix.append(animal.matrix)
        self.sem_matrix = np.matrix(stats.sem(self.full_matrix))
        self.mean_matrix = np.matrix(self.full_matrix).mean(0)


'''
class Experimental_group:
    name = ""
    groups = []

    def __init__(self,id,no_of_groups):
        self.id = id    
        for i in range (no_of_groups):
            group = Group(i)
            self.groups.append(group)

    def assign(self, anim, flag):
        print("how many groups ",len(self.groups))

        ###only the first times
        for i in range(0,len(self.groups)):
            if not self.groups[i].animals:
                self.groups[i].animals.append(anim)
                print(i)
                break

        if flag is True:
            self.groups[0].animals.append(anim)

'''




'''
#TEST
kwargs = {'weight':23,"speed":95000,"actv":4500}
kwargs2 = {'weight':24,"speed":89000,"actv":3500}
kwargs3 = {'weight':25,"speed":76000,"actv":6500}

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
'''