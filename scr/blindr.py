#!/usr/bin/python

# this is the core script behind blindr
# it will read the specified input table, create animal and group objects with respect to the input
# and then assigns the animals to the groups based on the inference structure

import os
import platform
import sys
import errno
import math
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from scipy.spatial import distance
from functools import reduce
import logger
import logging
import webbrowser
import ontology as on
import itertools
import threading

style.use('ggplot')
np.random.seed(42)
now = datetime.now().strftime("%d-%m-%y_%H-%M-%S")

SCRIPT_PATH = os.getcwd() #example case
DATA_PATH = SCRIPT_PATH + '\\input\\'  # example case
OUTPUT_PATH = SCRIPT_PATH + '\\output\\%s\\' % now # example case
FILE_NAME = 'example_data.xlsx' # example case
FILE_FORMAT = '.'+FILE_NAME.split('.')[-1] # example case
LOG_FILE = FILE_NAME.split('.')[:-1][0] + '.log'
N_GROUPS = 3
DO_LOG = True
OUTHTML = OUTPUT_PATH + FILE_NAME.split('.')[0] + '_output.html' 
INPUT_PATH = 'dummy'

log = logging.getLogger('global')

# this first section is the running order of the script itself

def activate():

    # this function is called by the run button on the gui and starts the scipt

    read_config()
    mkdir_p(OUTPUT_PATH)
    log = logger.global_log('global', OUTPUT_PATH+LOG_FILE,DO_LOG)
    log.info('Starting script...')
    main()


def main():

    # the process is divided into three sections for increased traceability

    data, original_data = initialize()
    data, features, animals, groups = run(data, original_data)
    finalize(original_data, animals, groups, features)


def initialize():

    # this function reads the input data and initializes the output html file

    logger.init_html(OUTHTML, OUTPUT_PATH, INPUT_PATH, N_GROUPS)
    data = load_data(INPUT_PATH)
    logger.write_to_html(OUTHTML, 'Number of animals: %i' % len(data))
    logger.write_to_html(OUTHTML, '<br>')
    original_data = data.copy()

    return data, original_data


def run(data, original_data):

    # this function calls the workflow according to the inference structure

    data, features = process_data(data)
    plt = plot_data(original_data)
    data = standardscale(data, features)
    animals = make_animals(data, features)
    groups = make_groups(features)
    assign_animals(animals, groups)
    if N_GROUPS > 2:
        optimize_groups(animals, groups, features)
    msg = '<br>' 
    logger.write_to_html(OUTHTML,msg)

    return data, features, animals, groups


def finalize(original_data, animals, groups, features):

    # this function finalizes the output after the inference structure is complete

    output = make_output(original_data, animals, groups)
    plot_result(output)
    write_group_difference(groups, output, features)
    output = blind_output(output)
    save_name = 'blinded_%s' % FILE_NAME+'.'+FILE_FORMAT
    save_data(output, save_name)
    msg = 'Grouped data available under %s' % OUTPUT_PATH+save_name 
    write_group_table(output)
    logger.write_to_html(OUTHTML,msg)
    if os.path.isfile(OUTHTML):
        logger.finish_html(OUTHTML)
        webbrowser.open_new_tab(OUTHTML)


# this second section is the workflow of the inference structure

def read_config():

    # this function gets the input parameters specified in the gui and sets important global variables

    global OUTPUT_PATH, OUTHTML, N_GROUPS, INPUT_PATH, FILE_NAME, FILE_FORMAT, LOG_FILE

    f = open("args.txt","r")
    arguments = f.read().split('\n')
    f.close()
    os.remove('args.txt')
    N_GROUPS = int(arguments[0])
    INPUT_PATH = arguments[1]
    OUTPUT_PATH = arguments[2]
    FILE_NAME = arguments[4]
    FILE_FORMAT = arguments[3]
    OUTPUT_PATH = OUTPUT_PATH + now + '/'
    LOG_FILE = FILE_NAME + '.log'
    OUTHTML = OUTPUT_PATH + FILE_NAME + '_output.html' 


def process_data(data):

    # this function coverts the input file into animals features and converts categorical into a specific form of pseudocode
    log.info('Preprocessing data')
    features = [x for x in data.columns[2:]]
    msg = '\n Found features:'
    log.info(msg)
    logger.write_to_html(OUTHTML, msg)
    vector_features = []
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            msg = '     Categorical feature: %s' % f
            log.info(msg)
            logger.write_to_html(OUTHTML, msg)
            msg = '         Unique values: %i' % len(data[f].unique())
            log.info(msg)
            logger.write_to_html(OUTHTML, msg)
            log.info(data[f].value_counts())
            categories = [x for x, n in data[f].value_counts().iteritems()]
            for category, n in data[f].value_counts().iteritems(): #categories:
                log.info('Numerizing category: %s',category)
                data[category] = (data[f] == category).astype(float)
                vector_features.append(category)
        else:
            msg = '     Numerical feature: %s' % f
            log.info(msg)
            logger.write_to_html(OUTHTML, msg)

            vector_features.append(f)
    log.info('Preprocessing complete')
    log.info('')

    return data, vector_features


def make_groups(features):

    # this function creates the number of specified experimental groups as group objects from the ontology / domain model

    log.info('Creating groups')
    groups = []
    for i in range(N_GROUPS):
        groups.append(on.Group(i+1,len(features)))
    log.info('Created %i groups', len(groups))
    log.info('')

    return groups


def make_animals(data, features):

    # this function creates the specified animals as objects from the ontology / domain model

    log.info('Creating animals')
    animals = []
    for animal_id in data.index:
        kwargs={}
        for key, value in data.loc[animal_id][features].iteritems():
            kwargs[key] = value
        animals.append(on.Animal(animal_id,**kwargs))
    log.info('Created %i animals', len(animals))
    log.info('')

    return animals


def assign_animals(animals, groups):

    # this function does the initial assignment of animals to experimental groups, based on soft requirements

    log.info('Assigning animals to groups')
    for i, group in enumerate(groups):
        group.assign(animals[i])
    unassigned_animals = [animal for animal in animals if animal.group_id==None]
    while len(unassigned_animals) > 0:
        largest_distance = 0.0
        group_id = 0
        animal_id = 0
        for animal in unassigned_animals:
            for group in groups:
                dist = distance.euclidean(animal.matrix, group.mean_matrix)
                if dist > largest_distance:
                    largest_distance = dist
                    group_pick = group
                    animal_pick = animal
        group_pick.assign(animal_pick)
        unassigned_animals = [animal for animal in animals if animal.group_id==None]
    log.info('Initial assignment complete!')
    log.info('')
    equalize_groups(animals, groups)


def equalize_groups(animals, groups):

    # this function equalizies the group sizes while preserving group feature similarity

    log.info('Equalizing group sizes')
    mean_p = 0.0
    largest_group_id = None
    largest_group_size = 0
    smallest_group_id = None
    smallest_group_size = 100000000
    for group in groups:
        log.info('')
        log.info('Group ID: %i',group.id)
        log.info('Group size: %i',len(group.animals))
        if len(group.animals) > largest_group_size:
            largest_group_size = len(group.animals)
            largest_group = group
        if len(group.animals) < smallest_group_size:
            smallest_group_size = len(group.animals)
            smallest_group = group
        for other_group in groups:
            if group == other_group:
                pass
            else:
                t, p = compare_groups(group,other_group)
                mean_p = np.mean(p)
                log.info('mean feature difference between group %i and %i: %.3f', group.id, other_group.id, mean_p)
    log.info('mean difference: %.3f',mean_p)
    log.info('largest group: %i', largest_group.id)
    log.info('smallest group %i:', smallest_group.id)
    while largest_group_size - smallest_group_size > 1:
        log.info('Group sizes are not balanced!')
        log.info('checking for best animal to reassign')
        many_animals = largest_group.animals
        best_mean_p = 0.0
        best_animal = None
        for animal in many_animals:
            log.info('')
            largest_group.release(animal)
            smallest_group.assign(animal)
            t, p = compare_groups(largest_group,smallest_group)
            mean_p = np.mean(p)
            if mean_p > best_mean_p:
                best_mean_p = mean_p
                best_animal = animal
            smallest_group.release(animal)
            largest_group.assign(animal)
        log.info('')
        log.info('best animal to switch is: %s with new mean p = %.6f', best_animal.id, best_mean_p)
        largest_group.release(best_animal)
        smallest_group.assign(best_animal)
        log.info('')
        largest_group_id = None
        largest_group_size = 0
        smallest_group_id = None
        smallest_group_size = 100000000
        for group in groups:
            log.info('')
            log.info('Group ID: %i',group.id)
            log.info('Group size: %i',len(group.animals))
            if len(group.animals) > largest_group_size:
                largest_group_size = len(group.animals)
                largest_group = group
            if len(group.animals) < smallest_group_size:
                smallest_group_size = len(group.animals)
                smallest_group = group
    else:
        log.info('')
        msg = 'Group sizes are balanced!'
        log.info(msg)
        logger.write_to_html(OUTHTML,msg)
        for group in groups:
            msg = '     Group %i contains %i animals' % (group.id, len(group.animals))
            log.info(msg)
            logger.write_to_html(OUTHTML,msg)
            for other_group in groups:
                if group == other_group:
                    pass
                else:
                    t, p = compare_groups(group,other_group)
                    mean_p = np.mean(p)
                    log.info('mean feature difference between group %i and %i: %.3f', group.id, other_group.id,mean_p)
    log.info('Equalizing group size complete!')
    log.info('')

    return


def optimize_groups(animals, groups, features):

    # this function switches animals between equally sized groups to further optimize group similarity

    log.info('Optimizing groups')
    imps = 1
    first_sqH = get_sqH(groups, features)
    while imps > 0:
        imps = 0
        for animal, other_animal in list(itertools.combinations(animals, 2)):
            if animal.group_id == other_animal.group_id:
                continue
            else:
                animal_group = [group for group in groups if animal in group.animals][0]
                other_animal_group = [group for group in groups if other_animal in group.animals][0]
                animal_group.release(animal)
                other_animal_group.release(other_animal)
                animal_group.assign(other_animal)
                other_animal_group.assign(animal)

                new_sqH = get_sqH(groups, features)
                if new_sqH > first_sqH:
                    first_sqH = new_sqH
                    imps += 1
                    #print('animal1',animal.id,'from',animal_group.id)
                    #print('animal2', other_animal.id,'from', other_animal_group.id)
                    print('improved the sum of squared p to ', new_sqH)
                else:
                    animal_group.release(other_animal)
                    other_animal_group.release(animal)
                    animal_group.assign(animal)
                    other_animal_group.assign(other_animal)
        print('total of ',imps,'improvements')
    log.info('Optimizing groups complete!')

    return


def make_output(data, animals, groups):

    # this function creates the output of this script

    log.info('Creating output!')
    output = data[data.columns[:]]
    output['Group'] = None
    for animal in animals:
        output['Group'].loc[animal.id] = animal.group_id
    for group in groups:
        output.loc[output['Group'] == group.id,'No'] = range(1,len(group.animals)+1)
    output['No'] = output['No'].astype(int)
    log.info('output created!')
    log.info('')
    
    return output


def blind_output(data):

    # this function blinds the output of the script 

    log.info('Blinding output')
    drop = list(data.columns.values[2:-2])
    new = [column for column in data.columns.values if column not in drop]
    data = data.loc[:, data.columns.isin(new)]
    log.info('output blinded!')
    log.info('')
    
    return data


# this third section contains helper functions used by the aformentioned functions for logic and output

def write_group_difference(groups, output, features):

    # this helper function writes paired feature per group differences to the output for later manual quality control
    
    org_features = list(output.columns.values[2:-2])
    num_features = [feat for feat in org_features if feat in features]
    topic = 'Difference significance of features between groups'  
    logger.topic_to_html(OUTHTML, topic)
    for feat in num_features:
        msg = 'Feature: %s' % feat
        logger.write_to_html(OUTHTML,msg)
        difs = np.zeros(shape=(len(groups),len(groups)))
        ps = []
        for group, other_group in list(itertools.combinations(groups, 2)):
            df1 = output.loc[output['Group'] == group.id]
            df2 = output.loc[output['Group'] == other_group.id]
            t, p = compare_features(df1,df2,feat)
            ps.append(p)
            msg = '    Group %i & group %i     p = %.4f' % (group.id, other_group.id,p)
            logger.write_to_html(OUTHTML,msg)
        msg = '      Mean significance     p = %.4f' % (np.mean(ps))
        logger.write_to_html(OUTHTML,msg)
        msg = '<br>'
        logger.write_to_html(OUTHTML,msg)


def write_group_table(output):

    # this helper function writes the final group assignments to the html output file

    group_summary = output.reset_index().set_index(['Group','No']).unstack(['Group']).sort_index(0)
    msg = group_summary['ID'].to_html()
    logger.table_to_html(OUTHTML,msg,'Experimental groups')


def get_sqH(groups, features):

    # this helper function calculates the sum of squared p values to be maximized

    sq_p = 0
    for i in range(len(features)):
        H, p = nonpar_anova(groups,i)
        sq_p += p**2

    return sq_p


def nonpar_anova(groups,feat):

    # this helper function conducts a oneway anova for a given feature across all groups

    grouped_vector = []
    for group in groups:
        grouped_vector.append([row[feat] for row in group.full_matrix])

    H, p = stats.f_oneway(*grouped_vector)

    return H, p


def compare_features(df1,df2,feat):

    # this helper function conducts a non-parametric t-test comparing a feature of two given groups

    feats1 = df1[feat].values
    feats2 = df2[feat].values
    t, p = stats.ttest_ind(feats1, feats2, equal_var=False)
      
    return t, p


def compare_groups(group1,group2):

    # this helper function conducts a non-paramentric t-test across all featues of two given groups

    matrix1 = [list(row) for row in group1.full_matrix]
    matrix2 = [list(row) for row in group2.full_matrix]
    t, p = stats.ttest_ind(matrix1, matrix2, axis=0, equal_var=False)

    return t, p


def standardscale(df,features=None):

    # this helper function standardscales all features and converts them into z-scores
    log.info('Standardscaling data')
    scaler = StandardScaler(copy=False)
    if features==None:
        features = [x for x in df.columns[2:]]
    n = len(features)
    i = 1
    for column in features:
        log.info("standard scaling (%i of %i): %s", i, n, column)
        try:
            i += 1
            df[column] = scaler.fit_transform(df[column].values.reshape(-1, 1))
        except (RuntimeError, TypeError, NameError, ValueError) as err:
            log.warning("could not scale non-numerical feature: %s", column)
            continue
    log.info('Standardscaling complete!')
    log.info('')
    
    return df


def plot_data(data,savefig=True,show=False):

    # this helper function creates a plot of input data distribution for manual quality control in the output file
    
    log.info('Plotting data')
    features = [x for x in data.columns[2:]]
    fig, ax = plt.subplots(1,len(features),figsize=(15, 4))
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            data[f].value_counts().plot(kind='bar',ax=ax[c],title=f)
        else:
            data[f].plot(kind='hist',ax=ax[c],title=f,bins=9)
    plt.tight_layout()
    if savefig:
        name = "%s_features.png" % FILE_NAME
        plt.savefig(OUTPUT_PATH+name)
        log.info("saving plot as %s", OUTPUT_PATH+name)
        title = 'Features to be equally distributed'
        logger.plot_to_html(OUTHTML, OUTPUT_PATH, name, title)
    if show:
        plt.show()
        return
    log.info('')
    
    return plt


def plot_result(data,savefig=True,show=False):

    # this helper function creates a plot of feature distribution across the optimized groups for manual quality control in the output file

    log.info('Plotting results')
    features = [x for x in data.columns[2:-2]]
    n_groups = len(data['Group'].unique())
    fig, ax = plt.subplots(1,len(features),figsize=(15, 4))
    for c, f in enumerate(features):
        if data[f].dtypes == object:
            data.groupby(by='Group')[f].value_counts().unstack().plot.bar(ax=ax[c],title=f)
        else:
            data.boxplot(column=[f], by='Group', ax=ax[c])
    plt.tight_layout()
    if savefig:
        name = "grouped_%s.png" % FILE_NAME
        plt.savefig(OUTPUT_PATH+name)
        log.info("saving plot as %s", OUTPUT_PATH+name)
        title = 'Distribution of features in generated groups'
        logger.plot_to_html(OUTHTML, OUTPUT_PATH, name, title)
    if show:
        plt.show()
        return
    log.info('')

    return plt


def load_data(path=DATA_PATH):

    # this helper function loads the data from the specified input file

    log.info('Loading data from %s', path)
    if FILE_FORMAT in ['xlsx','xls']:
        data = pd.read_excel(path)
    elif FILE_FORMAT == 'csv':
        data = pd.read_csv(path)
    else:
        log.warning('Cannot read data format: %s', FILE_FORMAT)
        log.info('please use .xlsx, .xls or .csv file')
        return
    data.set_index('ID', inplace=True)
    log.info('Loading succuessful!')
    log.info('')
    
    return data


def save_data(df, name, fullpath=False):

    # this helper function saves the output data to a csv / excel table

    if fullpath == False:
        name = OUTPUT_PATH+name
        mkdir_p(OUTPUT_PATH) 
    log.info("saving data as %s", name)       
    if FILE_FORMAT in ['xlsx','xls']:
        df.to_excel(name)
    elif FILE_FORMAT == 'csv':
        df.to_csv(name)
    log.info("saving succuessful!")


def mkdir_p(path):

    # this helper function creates the output directory

    try:
        os.makedirs(path)
        log.info("created directory %s", path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':
    import pop
    pop.App()
    activate()
    log.info('Exiting script...')
    sys.exit()
