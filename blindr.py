#!/usr/bin/python

import os
import sys
import errno
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from scipy.spatial import distance
from functools import reduce
import logger
import webbrowser
import ontology as on

style.use('ggplot')
np.random.seed(42)
now = datetime.now().strftime("%d-%m-%y_%H-%M-%S")

SCRIPT_PATH = os.getcwd()
DATA_PATH = SCRIPT_PATH + '\\input\\'
OUTPUT_PATH = SCRIPT_PATH + '\\output\\%s\\' % now
FILE_NAME = 'example_data.xlsx'
FILE_FORMAT = '.'+FILE_NAME.split('.')[-1]
LOG_FILE = FILE_NAME.split('.')[:-1][0] + '.log'
N_GROUPS = 3
DO_LOG = True
OUTHTML = OUTPUT_PATH + FILE_NAME.split('.')[0] + '_output.html' 

def main():
    data, original_data = initialize()
    data, features, animals, groups = run(data, original_data)
    finalize(original_data, animals, groups)


def finalize(original_data, animals, groups):
    output = make_output(original_data, animals, groups)
    plt = plot_result(output)
    output = blind_output(output)
    save_name = 'blinded_%s' % FILE_NAME
    save_data(output, save_name)
    msg = 'Grouped data available under %s' % OUTPUT_PATH+save_name 
    logger.write_to_html(OUTHTML,msg)
    group_summary = output.reset_index().set_index(['Group','No']).unstack(['Group']).sort_index(0)
    msg = group_summary['ID'].to_html()
    logger.table_to_html(OUTHTML,msg,'Experimental groups')
    if os.path.isfile(OUTHTML):
        logger.finish_html(OUTHTML)
        webbrowser.open_new_tab(OUTHTML)


def run(data, original_data):
    data, features = process_data(data)
    plt = plot_data(original_data)
    data = standardscale(data, features)
    #save_data(data, 'standardized_%s' % FILE_NAME)
    animals = make_animals(data, features)
    groups = make_groups(features)
    assign_animals(animals, groups)
    msg = '<br>' 
    logger.write_to_html(OUTHTML,msg)

    return data, features, animals, groups


def initialize():
    file_path = '%s%s' % (DATA_PATH, FILE_NAME)
    logger.init_html(OUTHTML, file_path, N_GROUPS)
    data = load_data(file_path)
    logger.write_to_html(OUTHTML, 'Number of animals: %i' % len(data))
    logger.write_to_html(OUTHTML, '<br>')
    original_data = data.copy()

    return data, original_data


def blind_output(data):
    log.info('Blinding output')
    drop = list(data.columns.values[2:-2])
    new = [column for column in data.columns.values if column not in drop]
    data = data.loc[:, data.columns.isin(new)]
    log.info('output blinded!')
    log.info('')
    
    return data


def make_output(data, animals, groups):
    log.info('Creating output!')
    output = data[data.columns[:]]
    output['Group'] = None
    for animal in animals:
        output['Group'].loc[animal.id] = animal.group_id+1
    for group in groups:
        output.loc[output['Group'] == group.id+1,'No'] = range(1,len(group.animals)+1)
    output['No'] = output['No'].astype(int)
    log.info('output created!')
    log.info('')
    
    return output


def assign_animals(animals, groups):
    log.info('Assigning animals to groups')
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
            largest_group_id = group.id
        if len(group.animals) < smallest_group_size:
            smallest_group_size = len(group.animals)
            smallest_group_id = group.id
        for other_group in groups:
            if group == other_group:
                pass
            else:
                t, p = compare_groups(group,other_group)
                print(p)
                mean_p = np.mean(p)
                log.info('mean feature difference between group %i and %i: %.3f', group.id, other_group.id, mean_p)
    #mean_p /= len(groups)*(len(groups)-1)
    log.info('mean difference: %.3f',mean_p)
    log.info('largest group: %i', largest_group_id)
    log.info('smallest group %i:', smallest_group_id)
    while largest_group_size - smallest_group_size > 1:
        log.info('Group sizes are not balanced!')
        log.info('checking for best animal to reassign')
        many_animals = groups[largest_group_id].animals
        best_mean_p = 0.0
        best_animal = None
        for animal in many_animals:
            log.info('')
            groups[largest_group_id].release(animal)
            groups[smallest_group_id].assign(animal)
            t, p = compare_groups(groups[largest_group_id],groups[smallest_group_id])
            mean_p = np.mean(p)
            if mean_p > best_mean_p:
                best_mean_p = mean_p
                best_animal = animal
            groups[smallest_group_id].release(animal)
            groups[largest_group_id].assign(animal)
        log.info('')
        log.info('best animal to switch is: %s with new mean p = %.6f', best_animal.id, best_mean_p)
        groups[largest_group_id].release(best_animal)
        groups[smallest_group_id].assign(best_animal)
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
                largest_group_id = group.id
            if len(group.animals) < smallest_group_size:
                smallest_group_size = len(group.animals)
                smallest_group_id = group.id
    else:
        log.info('')
        msg = 'Group sizes are balanced!'
        log.info(msg)
        logger.write_to_html(OUTHTML,msg)
        for group in groups:
            msg = '     Group %i contains %i animals' % (group.id+1, len(group.animals))
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


def compare_groups(group1,group2):
    matrix1 = group1.full_matrix
    matrix2 = group2.full_matrix
    t, p = stats.ttest_ind(matrix1, matrix2, axis=0, equal_var=False)

    return t, p #np.mean(p)


def make_groups(features):
    log.info('Creating groups')
    groups = []
    for i in range(N_GROUPS):
        groups.append(on.Group(i,len(features)))
    log.info('Created %i groups', len(groups))
    log.info('')

    return groups


def make_animals(data, features):
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


def standardscale(df,features=None):
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


def process_data(data):
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


def plot_data(data,savefig=True,show=False):
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
        name = "%sdata_%s.png" % (OUTPUT_PATH, FILE_NAME.split('.')[0])
        plt.savefig(name)
        log.info("saving plot as %s", name)
        title = 'Features to be equally distributed'
        logger.plot_to_html(OUTHTML, name, title)
        logger.write_to_html(OUTHTML,'Plot saved under %s' % name)
    if show:
        plt.show()
        return
    log.info('')
    
    return plt


def plot_result(data,savefig=True,show=False):
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
        name = "%sgrouped_%s.png" % (OUTPUT_PATH, FILE_NAME.split('.')[0])
        plt.savefig(name)
        log.info("saving plot as %s", name)
        title = 'Distribution of features in generated groups'
        logger.plot_to_html(OUTHTML, name, title)
        logger.write_to_html(OUTHTML,'Plot saved under %s' % name)
    if show:
        plt.show()
        return
    log.info('')

    return plt


def load_data(path=DATA_PATH):
    log.info('Loading data from %s', path)
    if FILE_FORMAT in ['.xlsx','.xls']:
        data = pd.read_excel(path)
    elif FILE_FORMAT == '.csv':
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
    if fullpath == False:
        name = OUTPUT_PATH+name
        mkdir_p(OUTPUT_PATH) 
    log.info("saving data as %s", name)       
    if FILE_FORMAT in ['.xlsx','.xls']:
        df.to_excel(name)
    elif FILE_FORMAT == '.csv':
        df.to_csv(name)
    log.info("saving succuessful!")


def mkdir_p(path):
    try:
        os.makedirs(path)
        #log.info("created directory %s", path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':
    mkdir_p(OUTPUT_PATH)
    log = logger.global_log('global', OUTPUT_PATH+LOG_FILE,DO_LOG)
    log.info('Starting script...')
    main()
    log.info('Exiting script...')
    sys.exit()
