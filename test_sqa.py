import numpy as np
import pandas as pd
import logging
import time
import sys
import os, os.path
import errno
from operator import itemgetter

import pymp

sys.path.insert(0, '../../SQA')
from disc_sqa import SQA

sys.path.insert(0, '../../TSP/Greedy')
from gen_cities import GenCities
from greedy import GreedyTSP

sys.path.insert(0, '../')
from test_util import mkdir_p

sys.path.insert(0, '../../TSP')
sahara_lowest = pd.read_csv(sys.path[0] + '/' + 'sahara_greedy.csv')
sahara_lowest = sahara_lowest.groupby(['city']).mean().reset_index()
sahara_greedy = sahara_lowest[sahara_lowest['city']=='sahara']['avg_tour_len'].iloc[0]
sahara_lowest = sahara_lowest[sahara_lowest['city']=='sahara']['avg_lowest'].iloc[0]

logging.basicConfig(filename='app.log', filemode='w', format = '%(asctime)s  %(levelname)-10s %(processName)s  %(name)s %(message)s')


if __name__ == '__main__':

    def create_problem(Ncity, explore, batch_iter):
        cities_dict = {"city":list(), "x":list(), "y":list()}
        for k,v in Ncity.cities.items():
            cities_dict['city'].append(k)
            cities_dict['x'].append(Ncity.cities[k][0][0])
            cities_dict['y'].append(Ncity.cities[k][0][1])
        cities_dataframe = pd.DataFrame(cities_dict)
        cities_dataframe.to_csv(os.getcwd()+"/problems/city_coordinates_{}_iter{}.csv".format(explore, batch_iter))
        print("Problem data created!")
        sys.stdout.flush()

    def prep_city(datas):
        cities = dict()
        for i in datas:  # not to include the start city
            state = [float(i[1]), float(i[2])]
            cities[int(i[0])] = [state, 0]
        return cities

    def precomp_distances(cities):
        '''
        input: none
        function that comes up with a table of distances of each city to the next 
        output: none
        '''
        distance = lambda x, y: np.sqrt((x[0] - y[0]) ** 2 + (x[1]
                    - y[1]) ** 2)
        # distances is an ordered list containing visited cities
        "Cities Precomputed and stored in Matrix"
        table_distances = dict()
        for (k, v) in cities.items():
            table_distances[k] = {i:distance(cities[i][0], cities[k][0]) for i,j in cities.items()\
                                        if i != k}
        return table_distances


    # exp = 10000
    beta = [10]
    trotter = [10]
    batch_iter = 50
    anneal_param = 1.0
    geom_params = [0.90]

    start_cities = list()

    def mkdir_p(paths):
        for path in paths:
            try:
                os.makedirs(path)
                print('Successfully created directory: {}'.format(path))
                sys.stdout.flush()
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else: 
                    print("Error in creating path \n")
                    sys.stdout.flush()
                    raise

    FILE_NAME = 'sahara.txt'
    f = open(sys.path[0] + '/' + FILE_NAME)
    POINT = []
    for i in f:
        POINT.append(i.split(" "))

    cities = prep_city(POINT)


    try:
        config_start_time = time.time()

        # mcmc step
        anneal_pairs = {"steps":list(), "current_cost":list(), "temp":list(), "trotter":list(), "best":list(), \
             "average":list(), "time":list(), "greedy":list(), "lowest":list()}

        path_dir = [os.getcwd()+'/sahara']#, os.getcwd()+'/{}sweeps'.format(maxstp)]                    
        mkdir_p(path_dir)

        for b in beta:
            print(b)
            sys.stdout.flush()
            for t in trotter:
                print(t)
                sys.stdout.flush()
                # set the trotter
                for l in geom_params:
                    print(l)
                    sys.stdout.flush()
                    # set the geometric reduction parameter
                    for maxstp in [100, 1000, 10000, 30000]:
                        print(b)
                        sys.stdout.flush()
                        # set number of sweeps taken by sqa
                        for i in range(batch_iter): 

                            print("Current Batch Iteration: {}".format(i))
                            sys.stdout.flush()

                            start_time = time.time()
                            
                            sys.stdout.flush()

                            sqa = SQA(cities, precomp_distances(cities), 1, TROTTER_DIM = t, ANN_PARA = anneal_param, MC_STEP = maxstp, BETA = b, \
                                    REDUC_PARA = l, correct = sahara_lowest)
                            

                            converged, route, best_all, it_time, lengthlist, temps, steps = sqa.run_anneal()

                            print("Batch Iteration Execution Time: --- %s seconds ---" % (time.time() - start_time))
                            sys.stdout.flush()

                            temps = np.unique(np.array(temps)).tolist()

                            for i,j in enumerate(temps):
                                anneal_pairs['steps'].append(maxstp)
                                anneal_pairs['temp'].append(temps[i])
                                anneal_pairs['current_cost'].append(lengthlist[i])
                                anneal_pairs['trotter'].append(10)
                                anneal_pairs['greedy'].append(sahara_greedy)
                                anneal_pairs['average'].append(np.mean(lengthlist))
                                anneal_pairs['best'].append(best_all[i])
                                anneal_pairs['lowest'].append(sahara_lowest)
                                anneal_pairs['time'].append(it_time)

                            df = pd.DataFrame.from_dict(anneal_pairs)
                            df.to_csv(os.getcwd()+"/sahara/trotter{}_beta{}_geom{}_steps{}_iter{}.csv".format(t, b, l, maxstp, i))

        print("Configuration Execution Time: --- %s seconds ---" % (time.time() - config_start_time))
        sys.stdout.flush()

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)

