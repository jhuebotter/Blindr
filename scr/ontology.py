#!/usr/bin/python

# this script represents the ontology established for this project
# it refers to the animal and group classes from the domain structure

import numpy as np
from scipy import stats
import logger
import logging

log = logging.getLogger('global')

class Animal:

    # an object of this class referes to the the animal of the domain strucute
    # it can belong to up to one group at a time, has an ID and a set of features

    def __init__(self,id_no,**kwargs):
        self.group_id = None
        self.id = id_no
        self.matrix = []
        for key,value in kwargs.items():
            setattr(self, key, value)
            self.matrix.append(value)
        self.matrix = np.array(self.matrix)
        log.info('created animal with ID: %s', self.id)


class Group:

    # an object of this class referes to the the experimental group of the domain strucute
    # it can contain to several animals at a time, has an ID and a set of average animal features

    def __init__(self,id_no,n_feat):
        self.animals = []
        self.id = id_no
        self.n_feat = n_feat
        self.full_matrix = np.zeros(self.n_feat)
        self.mean_matrix = np.zeros(self.n_feat)
        self.sem_matrix = np.zeros(self.n_feat)
        self.animals_list = []
        log.info("created group with ID: %s", self.id)

    def assign(self, anim):

        # this function assigns any given animal to the group, if not assigned already

        if anim.group_id == None:
            anim.group_id = self.id
            self.animals.append(anim)
            self.update_mean_features()
            log.info("assigned animal %s to group %s", anim.id, self.id)
        elif anim.group_id == self.id:
            log.warning("assignment failed - animal %s already this group", anim.id)
        else:
            log.warning("assignment failed - animal %s already in group %s - please release first to reassign", anim.id, anim.group_id)

    def release(self, anim):

        # this function releases any given animal from this group, if present

        if anim in self.animals:
            self.animals.remove(anim)
            log.info("removed animal %s from group %s", anim.id, self.id)
            anim.group_id = None
            self.update_mean_features()
        else:
            log.warning("release failed - animal %s not in group %s", anim.id, self.id)
            
    def update_mean_features(self):

        # this function updates the mean feature matrix after the group constellation has been changed
        
        self.animals_list = [x.id for x in self.animals]
        self.full_matrix = np.zeros(self.n_feat)
        if len(self.animals_list) > 0: 
            self.mean_matrix = []
            self.sem_matrix = []
            self.full_matrix = []
            for animal in self.animals:
                self.full_matrix.append(animal.matrix)
            self.sem_matrix = np.matrix(stats.sem(self.full_matrix))
            self.mean_matrix = np.matrix(self.full_matrix).mean(0)
        else:
            self.mean_matrix = np.zeros(self.n_feat)
            self.sem_matrix = np.zeros(self.n_feat)


def test():

    # this function tests if animals and groups can be created and assigned properly

    log = logger.global_log('global', 'ontology_test.log')
    
    log.info('Coducting ontology.py testrun')

    kwargs = {'weight':23,"speed":95000,"actv":4500}
    kwargs2 = {'weight':24,"speed":89000,"actv":3500}
    kwargs3 = {'weight':25,"speed":76000,"actv":6500}
    kwargs4 = {'weight':25,"speed":79000,"actv":4500}

    n_features = len(kwargs)
   
    mouse1 = Animal("01", **kwargs)
    mouse2 = Animal("02", **kwargs2)
    mouse3 = Animal("03", **kwargs3)
    mouse4 = Animal("04", **kwargs3)

    group0 = Group(0,n_features)
    group1 = Group(1,n_features)

    group0.assign(mouse1)
    group1.assign(mouse2)
    group1.assign(mouse3)
    group0.assign(mouse4)
    group1.release(mouse4)
    group1.assign(mouse2)
    group0.assign(mouse2)
    group1.release(mouse2)
    group0.assign(mouse2)

    log.info('Ontology.py testrun complete!')


if __name__ == '__main__':
    test()
