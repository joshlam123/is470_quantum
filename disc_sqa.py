# import time
import math
import numpy as np
import os
import random
import matplotlib.pyplot as plt
import time
import sys
from operator import itemgetter
sys.path.insert(0, '../TSPData')

import pandas as pd


class SQA:
    def __init__(self, cities, distance_table, start_city, trotter_dim:int = 100, ann_para:int = 100, MC_STEP:int = 100, beta:float=100.0,\
        REDUC_PARA:float = 0.99):
        '''
        Initialise Parameters: City data, precomputed distance table, start city, annealing parameters, number of monte carlo sweeps,
        Beta, Reduction Paramaeter
        '''

        self.trotter_dim = trotter_dim
        
        self.steps = MC_STEP
        self.beta, self.s = beta, ann_para

        self.REDUC_PARA = REDUC_PARA
        self.start_city, self.cities, self.distances = start_city, cities, distance_table
        self.POINT = [[k, v[0][0], v[0][1]] for k,v in self.cities.items()]
        self.ncity = len(self.POINT)
        self.total_time = self.ncity

        self.temps = list()
        


    def getSpin(self, config_at_init_time:list) -> list:
        '''
        input: initial configuration of spins
        first, set spin configs for each path where a randomly chosen city is set to +1 and the rest to -1
        output:         
        '''
        
        def trotter_spin_config_time(tag):
            ''' Set the Spin coordination at a certain time in a certain Trotter dimension to -1, and a specific tag to 1 '''
            config = list(-np.ones(self.ncity, dtype = np.int))
            config[tag-1] = 1
            return config

        
        def trotter_spin_config(tag) -> list:
            ''' Spin coordination in a Trotter dimension '''
            spin = [trotter_spin_config_time(j) for i,j in enumerate(tag) if i != len(tag)]
            spin = [config_at_init_time] + spin
            return spin

        spin = list()
        for i in range(self.trotter_dim):
            tag = np.arange(2,self.ncity+1)
            np.random.shuffle(tag)
            spin.append(trotter_spin_config(tag)) 
        return spin


    def bestRoute(self, config:list) -> list:
        '''
        Select the Trotter dimension that is the shortest distance and output the route at that time
        '''   
        length = []
        for i in range(self.trotter_dim):
            route = [(config[i][j-1].index(1))+1 for j in range(1,self.total_time+1)]
            route += [self.start_city]
            length.append(self.getTotaldistance(route))

        min_Tro_dim = np.argmin(length)
        Best_Route = [config[min_Tro_dim][i-1].index(1)+1 for i in range(1,self.total_time+1)]
        return Best_Route
    
    
    def getTotaldistance(self, route:list) -> float:
        '''
        Total distance divided by max value for a route
        '''
        Total_distance = 0
        Total_distance += np.sum([self.distances[route[i-1]][route[i]] for i in range(1,self.total_time)])
        return Total_distance/self.ncity


    def acceptance_probability(self, partition):
        '''
        takes in the partition and partition prime function. acceptance is defined as 1/2nl * min(1, partition_prime/partition)
        '''
        return ((2*self.ncity*self.trotter_dim)**-1) * min(1, partition)

    
    def quantumPartition(self, path, path_prime):
        '''
        takes in a list of paths and calculates the quantum partition function
        '''
        # modularize it a little bit so that it can be reused as long as I pass in a path
        
        def tr_a(paths, path_prime):
        # calculates trace_A part of pi(x)
            const_factor = -self.beta * self.s / self.trotter_dim
            total_sum_factor = np.sum([self.distances(j, path_prime[i]) for i,j in enumerate(paths)])

            return np.exp(const_factor * total_sum_factor)
        
        # calculates trace_B part of quantum partition function
        def tr_b(path):
            t_b = []
            omega = math.tanh(self.beta*(1-self.s)/self.trotter_dim)
            
            # some crazy n**3 run time going on here..
            for j in range(self.trotter_dim):
                for k in range(self.ncity):
                    
                    consecutive = []
                    prev = path[j][k][0]
                    c_bits = 0
                    current = 0

                    for idx, no in enumerate(path[j][k]):
                        if prev != no:
                            c_bits += 1
                        else:
                            consecutive.append(c_bits)

                            c_bits = 0

                        prev = no

                        if idx == self.ncity-1:
                            consecutive.append(c_bits)

                if np.sum(consecutive) == 0: 
                    pdt = 0
                else:
                    pdt = 1
                    for entry in consecutive:
                        if entry != 0:
                            pdt *= entry
                            
                t_b.append(omega**pdt)

            pdt = 1
            for entry in t_b:
                pdt *= entry

            return pdt
        
        b = tr_b(path)
        b_prime = tr_b(path_prime)
        a = tr_a(path, path_prime)
        pi_x_prime = a * (b/b_prime)

            
        return pi_x_prime

    def flipBits(self, path, bit_swap):
            if bit_swap == 0:
                path = f"{int(not int(path[bit_swap]))}{path[bit_swap+1:]}"
            elif bit_swap == len(path) - 1:
                path = f"{path[:bit_swap]}{int(not int(path[bit_swap]))}"
            else:
                path = f"{path[:bit_swap]}{int(not int(path[bit_swap]))}{path[bit_swap+1:]}"
            return path

    def PIMC(self, config, ann_para):
        self.temps.append(ann_para)
        '''
        PIMC Stemp
        input: dictionary of array paths with Nl sites, annealing parameter
        METROPOLIS UPDATE & Difference in Sampling Distribution
        '''
        # choose a random path to look at 
        new_path = list()
        costs = dict()
        
        bit_swaps = random.choices(range(0, self.nctiy), k=self.trotter_dim)   
                                                                                                                                          
        for idx, path in enumerate(config):
            # append a new path to the list of new paths
            new = self.flipBits(path, bit_swaps[idx])
            costs[idx] = self.distances(path, new)
            new_path.append(new)

        pi_x_prime = self.quantumPartition(config, new_path)
                     
        # do single site metropolis updates for each site
        for idx, path in enumerate(new_path):
            delta_cost = self.distances(path, config[idx])
            #self.cost_fn(path) - self.cost_fn(config[idx])
            
            if delta_cost <= 0 or random.uniform(0,1) < self.acceptance_probability(pi_x_prime):
                config[idx] = path       

        return config


    def run_anneal(self):
        ''' run annealing '''
        best_cost = list()
        best_route = list()

        max_key = list()
        for k,v in self.distances.items():
            max_keys = max(v.keys(), key=(lambda l: v[l]))
            max_key.append([max_keys, v[max_keys]])
        self.max_distance = max_key[max(enumerate(map(itemgetter(1), max_key)),key=itemgetter(1))[0]][1]
        print(f"The max distance is {self.max_distance}")
        
        # Spin coordination at the initial time (Be sure to be in city 0 at the initial time)
        config_at_init_time = list(-np.ones(self.ncity,dtype=np.int))
        config_at_init_time[0] = 1
        
        print("start...")
        t0 = time.clock()

        np.random.seed(100)

        spin = self.getSpin(config_at_init_time)
        LengthList = list()
        
        t = 0
        while round(self.s,2) > 0.01:
            con = [self.PIMC(spin, self.s) for i in range(self.steps)]
            rou = [self.bestRoute(j) for j in con]
            length = [round(self.getTotaldistance(i),2) for i in rou]

            LengthList.append(min(length))
            new_route = rou[np.argmin(length)]
            
            if t == 0:
                best_cost.append(min(length))
                best_route = new_route
            else:
                if best_cost[-1] > min(length):
                    best_route = new_route
                    best_cost.append(min(length))
                else:
                    best_cost.append(best_cost[-1])
            
            print("Step:{}, Annealing Parameter:{}, Lowest length:{}".format(t+1,self.s, length[-1]))
            self.temps.append(self.s)
            self.s *= self.REDUC_PARA
            t += 1

        elapsed_time = time.clock()-t0

        return (best_route, best_cost, elapsed_time, LengthList, self.temps, t)
        
        