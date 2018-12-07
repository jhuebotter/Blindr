#!/usr/bin/python

import os
import sys
import numpy as np
import numbers
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import errno
#import ontology as on

style.use('ggplot')

SCRIPT_PATH = os.getcwd()
DATA_PATH = SCRIPT_PATH + '\input'
OUTPUT_PATH = SCRIPT_PATH + '\output'
FILE_NAME = 'example_data.xlsx'
GROUPS = ['A','B','C']

def main():

    file_path = '%s\%s' % (DATA_PATH, FILE_NAME)
    data = load_excel(file_path)
    data, features = process_data(data)
    data = standardscale(data)
    plt = plot_data(data)
    save_df(data, 'standardized_%s' % FILE_NAME)
    #plt.show()
    animals make_animals(data, features)
    return animals


def make_animals(data, features):
    animals = []
    for animal_id in data.index:
        kwargs={}
        for key, value in data.loc[animal_id][features].iteritems():
            kwargs[key] = value
        #print('Animal ID:',animal_id)
        #print('Features:',kwargs)
        #print()
        animals.append([animal_id, kwargs])
    print(animals)
        #animals.append(on.Animal(animal_id,**kwargs))

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
                #data[category] = data[category]/n# len(data[f].unique())
            #print(data.head())
        else:
            vector_features.append(f)
        #print(vector_features)
    return data, vector_features


def plot_data(data):
    features = [x for x in data.columns[2:]]
    fig, ax = plt.subplots(1,len(features),figsize=(15, 4))
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            data[f].value_counts().plot(kind='bar',ax=ax[c],title=f)
        else:
            data[f].plot(kind='hist',ax=ax[c],title=f,bins=9)
    fig.tight_layout()
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
        print("saving df as ", OUTPUT_PATH, name)
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
