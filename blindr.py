#!/usr/bin/python

import os
import sys
import numpy as np
import numbers
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import errno
from scipy.spatial import distance
import ontology as on


style.use('ggplot')
np.random.seed(42)

SCRIPT_PATH = os.getcwd()
DATA_PATH = SCRIPT_PATH + '\input'
OUTPUT_PATH = SCRIPT_PATH + '\output'
FILE_NAME = 'example_data.xlsx'
N_GROUPS = 3


def main():

    file_path = '%s\%s' % (DATA_PATH, FILE_NAME)
    data = load_excel(file_path)
    original_data = data.copy()
    data, features = process_data(data)
    data = standardscale(data)
    #plt = plot_data(data)
    #save_df(data, 'standardized_%s' % FILE_NAME)
    #plt.show()
    animals = make_animals(data, features)
    groups = make_groups(features)
    assign_animals(animals, groups)
    output = make_output(original_data, animals)
    plt = plot_result(output)
    output = blind_output(output)
    save_df(output, 'grouped_%s' % FILE_NAME)
    #plt.show()


def blind_output(data):
    drop = data.columns.values[2:-1]
    new = [column for column in data.columns.values if column not in drop]
    data = data.loc[:, data.columns.isin(new)]
    print('output blinded!')
    
    return data


def make_output(data, animals):
    output = data[data.columns[:]]
    output['Group'] = None
    for animal in animals:
        output['Group'].loc[animal.id] = animal.group_id+1
    
    return output


def assign_animals(animals, groups):
    unassigned_animals = [animal for animal in animals if animal.group_id==None]
    while len(unassigned_animals) > 0:
        largest_distance = 0.0
        group_id = 0
        animal_id = 0
        for animal in unassigned_animals:
            for group in groups:
                dist = distance.euclidean(animal.matrix, group.mean_matrix)
                #print(animal.id,group.id, dist)
                if dist > largest_distance:
                    largest_distance = dist
                    group_pick = group
                    animal_pick = animal
        group_pick.assign(animal_pick)
        unassigned_animals = [animal for animal in animals if animal.group_id==None]
    equalize_groups(animals, groups)


def equalize_groups(animals, groups):
    mean_p = 0.0
    largest_group_id = None
    largest_group_size = 0
    smallest_group_id = None
    smallest_group_size = 100000000
    for group in groups:
        print()
        print('Group ID:',group.id)
        print('Group size:',len(group.animals))
        if len(group.animals) > largest_group_size:
            largest_group_size = len(group.animals)
            largest_group_id = group.id
        if len(group.animals) < smallest_group_size:
            smallest_group_size = len(group.animals)
            smallest_group_id = group.id
        for other_group in groups:
            if group == other_group:
                pass
            else:
                t, p = compare_groups(group,other_group)
                mean_p += p
                print('Difference between group', group.id, 'and', other_group.id,':',p)
    mean_p /= len(groups)*(len(groups)-1)
    print('mean difference:',mean_p)
    print('largest group:', largest_group_id)
    print('smallest group:', smallest_group_id)
    while largest_group_size - smallest_group_size > 1:
        print('Group sizes are not balanced!')
        many_animals = groups[largest_group_id].animals
        best_mean_p = 0.0
        best_animal = None
        for animal in many_animals:
            groups[largest_group_id].release(animal)
            groups[smallest_group_id].assign(animal)
            t, p = compare_groups(groups[largest_group_id],groups[smallest_group_id])
            #print(animal.id,p)
            if p > best_mean_p:
                best_mean_p = p
                best_animal = animal
            groups[smallest_group_id].release(animal)
            groups[largest_group_id].assign(animal)
        print('best animal to switch is:',best_animal.id, 'with new mean p =', best_mean_p)
        groups[largest_group_id].release(best_animal)
        groups[smallest_group_id].assign(best_animal)

        largest_group_id = None
        largest_group_size = 0
        smallest_group_id = None
        smallest_group_size = 100000000
        for group in groups:
            print()
            print('Group ID:',group.id)
            print('Group size:',len(group.animals))
            if len(group.animals) > largest_group_size:
                largest_group_size = len(group.animals)
                largest_group_id = group.id
            if len(group.animals) < smallest_group_size:
                smallest_group_size = len(group.animals)
                smallest_group_id = group.id
    else:
        print('Group sizes are balanced!')
        for group in groups:
            print('Group ID:',group.id)
            print('Group size:',len(group.animals))
            for other_group in groups:
                if group == other_group:
                    pass
                else:
                    t, p = compare_groups(group,other_group)
                    mean_p += p
                    print('Difference between group', group.id, 'and', other_group.id,':',p)
        return

def compare_groups(group1,group2):
    matrix1 = group1.full_matrix
    matrix2 = group2.full_matrix
    t, p = stats.ttest_ind(matrix1, matrix2, axis=None, equal_var=False)
    #print(t, p)
    return t, p


def make_groups(features):
    groups = []
    for i in range(N_GROUPS):
        groups.append(on.Group(i,len(features)))
    
    return groups


def make_animals(data, features):
    animals = []
    for animal_id in data.index:
        kwargs={}
        for key, value in data.loc[animal_id][features].iteritems():
            kwargs[key] = value
        animals.append(on.Animal(animal_id,**kwargs))

    return animals


def standardscale(df):
    scaler = StandardScaler(copy=False)
    features = [x for x in df.columns[2:]]
    n = len(features)
    i = 1
    for column in features:
        print(str(datetime.now()), "standard scaling (%i of %i): %s" % (i, n, column))
        try:
            i += 1
            df[column] = scaler.fit_transform(df[column].values.reshape(-1, 1))
        except (RuntimeError, TypeError, NameError, ValueError) as err:
            print(str(datetime.now()), "could not scale feature due to: ", err)
            continue
    
    return df


def process_data(data):
    features = [x for x in data.columns[2:]]
    print('found features:',features)
    vector_features = []
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            print('found categorical feature:',f)
            print('unique values:',len(data[f].unique()))
            print(data[f].value_counts())
            print()
            categories = [x for x, n in data[f].value_counts().iteritems()]
            for category, n in data[f].value_counts().iteritems(): #categories:
                print('numerizing category:',category)
                data[category] = (data[f] == category).astype(float)
                vector_features.append(category)
        else:
            vector_features.append(f)
    
    return data, vector_features


def plot_data(data):
    features = [x for x in data.columns[2:]]
    fig, ax = plt.subplots(1,len(features),figsize=(15, 4))
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            data[f].value_counts().plot(kind='bar',ax=ax[c],title=f)
        else:
            data[f].plot(kind='hist',ax=ax[c],title=f,bins=9)
    plt.tight_layout()
    
    return plt


def plot_result(data,savefig=True,show=False):
    features = [x for x in data.columns[2:-1]]
    n_groups = len(data['Group'].unique())
    fig, ax = plt.subplots(1,len(features),figsize=(15, 4))
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            data.groupby(by='Group')[f].value_counts().unstack().plot.bar(ax=ax[c])
        else:
            data.boxplot(column=[f], by='Group', ax=ax[c])
    plt.tight_layout()
    if savefig:
        name = "%s\grouped_%s.png" % (OUTPUT_PATH, FILE_NAME.split('.')[0])
        plt.savefig(name)
        print("saving plot as", name)
    if show:
        plt.show()
        return
    
    return plt


def load_excel(path=DATA_PATH):
    data = pd.read_excel(path)
    data.set_index('ID', inplace=True)
    
    return data


def save_df(df, name, fullpath=False):
    if fullpath:
        print("saving df as ", name)
        df.to_excel('%s' % (name))
    else:
        mkdir_p(OUTPUT_PATH)
        print("saving data as %s\%s" % (OUTPUT_PATH, name))
        df.to_excel('%s\%s' % (OUTPUT_PATH, name))
    print("saving succuessful!")


def mkdir_p(path):
    try:
        os.makedirs(path)
        print("created directory %s" % path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':
    main()
    sys.exit()
