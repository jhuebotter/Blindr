from itertools import permutations 
import random
import numpy as np

def main():

    get_design()

def get_design(n=7, m=3):
    
    groups = np.arange(m)

    # Get all permutations of the groups 
    perm = permutations(groups)

    # Get all pairs possible
    pairs = list(permutations(groups,2))

    # put all possile combinations in a list
    combs = [x for x in list(perm)]

    best_sum = 9999999999
    best_off = 9999999999
    best_design = np.zeros((n, m))

    improvement = True
    while improvement:
        improvement = False
        for i in range(100):

            design = np.array(random.sample(combs, n%len(combs)))
            if n/len(combs) > 1:
                for j in range(int(n/len(combs))):
                    design = np.append(design, combs ,axis = 0)
            elif n/len(combs) == 1:
                design = np.array([list(x) for x in combs])

            value_counts = np.array([np.bincount(design[:,x]) for x in range(m)])
            if value_counts.shape != (m,m):
                continue
                
            SS_off, pair_counts = count_pairs(design, pairs)
            SS_value = ((value_counts-int(n/m))**2).sum()

            if SS_value < best_sum and SS_off < best_off:
                improvement = True
            if SS_value <= best_sum and SS_off <= best_off:
                best_sum = SS_value
                best_off = SS_off
                best_design = design
                best_value_counts = value_counts

    np.random.shuffle(best_design)

    pair_counts = count_pairs(best_design, pairs)[1]

    return best_design, value_counts, pair_counts


def count_pairs(x, y):

    # counting pairs

    counts = np.zeros((len(y)))
    for e, i in enumerate(y):
        for j in x:
            for k in range(j.size):
                if list(j[k:k+2]) == list(i):
                    counts[e] +=1

    pair_counts = dict(zip(y, counts))
    expected = counts.sum()/len(counts)
    min_found = counts.min()
    max_found = counts.max()
    offset = ((counts-expected)**2).sum()

    return offset, pair_counts


if __name__ == '__main__':
    main()