import math
import time
import random
import itertools
import numpy as np
from tqdm import tqdm
from scipy.stats import rankdata

'''
未來優化
1 fitness 改成參數高原 (可參考 Dean 的作法)
    - 記憶性要涵蓋每一個樣本點
    - 平面看多遠、每格間距拉多大
    - 越靠近的權重越大
    - 看能不能用加裝飾器的方式一次解決 (就不用大改架構與記憶功能)
2 演算法 function 優化 (分析優化效果)
    - selection function
    - moving function
    - evolution process
    - dynamic hyperparameters
    - etc.
3 新增演算法
    - PSO (Particle Swarm Optimization)
    - BAS (Beetle Antennae Search)
    - 差分進化演算法 (Differential Evolution)

Thanks for 北科大工業工程管理系, 啟發式演算法
https://hackmd.io/@AlexChiang/Hkxp317Ao
'''


def get_random_seed():

    timestamp = time.time()
    seed = str(timestamp).split('.')[0][-3:]
    seed = int(seed)

    return seed


class GeneticAlgorithm:

    def __init__(self, domain_range, fitness_func, INI_SIZE=200, POP_SIZE=100, ELITE_SIZE=10, 
                 GENERATIONS=13, CROSSOVER_RATE=0.7, MUTATION_RATE=0.01, OBJECTIVE='maximum', 
                 SELECTION_STG='uniform', MOVING_STG=True, expended_ratio=0.2, MOVE_RATE=0.25,
                 save_process=False):

        # Hyperparameters
        self.INI_SIZE = INI_SIZE
        self.POP_SIZE = POP_SIZE
        self.ELITE_SIZE = ELITE_SIZE
        self.GENERATIONS = GENERATIONS
        self.CROSSOVER_RATE = CROSSOVER_RATE
        self.MUTATION_RATE = MUTATION_RATE
        self.OBJECTIVE = OBJECTIVE
        self.SELECTION_STG = SELECTION_STG
        self.MOVING_STG = MOVING_STG
        self.expended_ratio = expended_ratio
        self.MOVE_RATE = MOVE_RATE
        self.domain_range = domain_range
        self.fitness_func = fitness_func
        self.save_process = save_process

        # give a random seed
        seed = get_random_seed()
        random.seed(seed)

    # Selection function
    def selection(self, population, fitnesses, OBJECTIVE, SELECTION_STG):

        if OBJECTIVE == 'minimum':
            fitnesses = [-fitness_ for fitness_ in fitnesses]

        if SELECTION_STG == 'minmax' or SELECTION_STG == 'sqrt':
            copy_fitnesses_ = np.array(fitnesses)
            fitnesses_max = copy_fitnesses_.max()
            fitnesses_min = copy_fitnesses_.min()
            copy_fitnesses_ = (copy_fitnesses_-fitnesses_min) / (fitnesses_max-fitnesses_min)
            
            if SELECTION_STG == 'sqrt':
                copy_fitnesses_ = np.sqrt(copy_fitnesses_)
            copy_fitnesses = list(copy_fitnesses_)

        elif SELECTION_STG == 'uniform':
            copy_fitnesses = list(rankdata(fitnesses))

        total_fitness = sum(copy_fitnesses)
        pick = random.uniform(0, total_fitness)
        cumulative_fitness = 0

        for individual, fitness in zip(population, copy_fitnesses):
            cumulative_fitness += fitness
            if pick <= cumulative_fitness:
                return individual

    # Crossover function
    def onepoint_crossover(self, parent1, parent2):

        idx = random.randint(1, len(parent1)-1)
        child1 = parent1[:idx] + parent2[idx:]
        child2 = parent2[:idx] + parent1[idx:]

        return [child1, child2]

    def uniform_crossover(self, parent1, parent2):

        uniform_sequence = [random.randint(0,1) for _ in range(len(parent1))]
        child1 = list(np.where(uniform_sequence, parent1, parent2))
        child2 = list(np.where(uniform_sequence, parent2, parent1))

        return [child1, child2]

    # Mutation function
    def onepoint_mutation(self, individual, domain_range):

        new_individual = individual.copy()
        idx = random.randint(0, len(new_individual)-1)
        new_gene = random.choice(domain_range[idx])
        new_individual[idx] = new_gene

        return new_individual

    def uniform_mutation(self, individual, domain_range):

        RATE = 1 / len(individual)
        new_individual = individual.copy()

        for idx in range(len(individual)):
            if random.random() <= RATE:
                new_gene = random.choice(domain_range[idx])
                new_individual[idx] = new_gene

        return new_individual

    def silent_mutation(self, individual, expended_ratio, MOVE_RATE, domain_range):

        new_individual = individual.copy()

        for gene, gene_range, num in zip(individual, domain_range, range(len(individual))):
            if random.random() < MOVE_RATE:
                params_len = len(gene_range)
                expend_len = int(params_len*expended_ratio)
                num_index = gene_range.index(gene)

                new_index_lower_bound = num_index - expend_len
                new_index_upper_bound = num_index + expend_len

                if new_index_lower_bound < 0:
                    new_index_lower_bound = 0
                
                if new_index_upper_bound > params_len-1:
                    new_index_upper_bound = params_len-1

                new_index = random.randint(new_index_lower_bound, new_index_upper_bound)
                new_individual[num] = gene_range[new_index]

        return new_individual

    # Deletion function
    def deletion(self, population, new_population, fitnesses, new_fitnesses, OBJECTIVE, POP_SIZE, ELITE_SIZE):

        if OBJECTIVE == 'maximum':
            indices = sorted(range(len(fitnesses)), key=lambda x: fitnesses[x], reverse=True)
            new_indices = sorted(range(len(new_fitnesses)), key=lambda x: new_fitnesses[x], reverse=True)
        elif OBJECTIVE == 'minimum':
            indices = sorted(range(len(fitnesses)), key=lambda x: fitnesses[x], reverse=False)
            new_indices = sorted(range(len(new_fitnesses)), key=lambda x: new_fitnesses[x], reverse=False)

        elite_indices = indices[:ELITE_SIZE]
        elite_new_indices = new_indices[:int(POP_SIZE-ELITE_SIZE)]

        next_population = [population[i] for i in elite_indices] + [new_population[i] for i in elite_new_indices]
        next_fitnesses = [fitnesses[i] for i in elite_indices] + [new_fitnesses[i] for i in elite_new_indices]

        return next_population, next_fitnesses

    # Utils function
    def get_best_one(self, population, fitnesses, OBJECTIVE):

        if OBJECTIVE == 'maximum':
            best_fitness = max(fitnesses)
        elif OBJECTIVE == 'minimum':
            best_fitness = min(fitnesses)

        # if there is more than one optimal solution, it can return a list of best_individual
        best_individual = population[fitnesses.index(best_fitness)]

        return best_individual, best_fitness

    def cal_fitness(self, population, fitness_func, record_dict={}):

        fitnesses = []
        for individual in population:
            individual_tuple = tuple(individual)

            if individual_tuple in record_dict.keys():
                fitness_ = record_dict[individual_tuple]
            else:
                fitness_ = fitness_func(individual)
                record_dict[individual_tuple] = fitness_

            fitnesses.append(fitness_)
            
        return fitnesses, record_dict

    # Main function
    def optimize(self):

        result_dict = {}
        record_dict = {}
        process_dict = {}

        # Start of Genetic Algorithm
        for _ in tqdm(range(self.GENERATIONS)):

            if _ == 0:
                population = [[random.choice(domain) for domain in self.domain_range] for _ in range(self.INI_SIZE)]
                fitnesses, record_dict = self.cal_fitness(population, self.fitness_func, record_dict)
                cal_times = len(population)
                if self.save_process == True:
                    process_dict[str(_)] = {'population': population, 'fitnesses': fitnesses}
            
            new_population = []

            # each time will get two offsprings
            for __ in range(self.POP_SIZE // 2):

                # Selection
                parent1 = self.selection(population, fitnesses, self.OBJECTIVE, self.SELECTION_STG)
                parent2 = self.selection(population, fitnesses, self.OBJECTIVE, self.SELECTION_STG)
                offspring = [parent1, parent2]

                # Crossover
                if random.random() < self.CROSSOVER_RATE:
                    if random.random() > 0.5:
                        offspring = self.onepoint_crossover(parent1, parent2)
                    else:
                        offspring = self.uniform_crossover(parent1, parent2)
                # Local Search
                else:
                    if self.MOVING_STG == True:
                        for i in range(len(offspring)):
                            offspring[i] = self.silent_mutation(offspring[i], self.expended_ratio, self.MOVE_RATE, self.domain_range)

                # Mutation
                for i in range(len(offspring)):
                    if random.random() < self.MUTATION_RATE:
                        if random.random() > 0.5:
                            offspring[i] = self.onepoint_mutation(offspring[i], self.domain_range)
                        else:
                            offspring[i] = self.uniform_mutation(offspring[i], self.domain_range)

                new_population.extend(offspring)

            new_fitnesses, record_dict = self.cal_fitness(new_population, self.fitness_func, record_dict)
            cal_times += len(new_population)
            population, fitnesses = self.deletion(population, new_population, fitnesses, new_fitnesses, self.OBJECTIVE, self.POP_SIZE, self.ELITE_SIZE)
            # print(self.get_best_one(population, fitnesses, self.OBJECTIVE))
            if self.save_process == True:
                process_dict[str(_)] = {'population': population, 'fitnesses': fitnesses}

        best_individual, best_fitness = self.get_best_one(population, fitnesses, self.OBJECTIVE)

        # print('Best Individual: ', best_individual)
        # print('Best Fitness: ', best_fitness)
        # print('Run Times :', cal_times)

        result_dict['best_individual'] = best_individual
        result_dict['best_fitness'] = best_fitness
        result_dict['cal_times'] = cal_times
        result_dict['process_dict'] = process_dict

        return result_dict


class RandomSearch:

    def __init__(self, domain_range, fitness_func, OBJECTIVE='maximum', search_times=1000, save_process=False):

        # Hyperparameters
        self.domain_range = domain_range
        self.fitness_func = fitness_func
        self.OBJECTIVE = OBJECTIVE
        self.search_times = search_times
        self.save_process = save_process

        # give a random seed
        seed = get_random_seed()
        random.seed(seed)

    # Utils function
    def get_best_one(self, population, fitnesses, OBJECTIVE):

        if OBJECTIVE == 'maximum':
            best_fitness = max(fitnesses)
        elif OBJECTIVE == 'minimum':
            best_fitness = min(fitnesses)

        # if there is more than one optimal solution, it can return a list of best_individual
        best_individual = population[fitnesses.index(best_fitness)]

        return best_individual, best_fitness

    def cal_fitness(self, population, fitness_func, record_dict={}):

        fitnesses = []
        for individual in tqdm(population):
            individual_tuple = tuple(individual)

            if individual_tuple in record_dict.keys():
                fitness_ = record_dict[individual_tuple]
            else:
                fitness_ = fitness_func(individual)
                record_dict[individual_tuple] = fitness_

            fitnesses.append(fitness_)
            
        return fitnesses, record_dict

    # Main function
    def optimize(self):

        result_dict = {}
        record_dict = {}
        process_dict = {}

        population = [[random.choice(domain) for domain in self.domain_range] for _ in range(self.search_times)]
        fitnesses, record_dict = self.cal_fitness(population, self.fitness_func, record_dict)
        best_individual, best_fitness = self.get_best_one(population, fitnesses, self.OBJECTIVE)

        if self.save_process == True:
            process_dict = {'population': population, 'fitnesses': fitnesses}

        result_dict['best_individual'] = best_individual
        result_dict['best_fitness'] = best_fitness
        result_dict['cal_times'] = self.search_times
        result_dict['process_dict'] = process_dict
        
        return result_dict


class GridSearch:

    def __init__(self, domain_range, fitness_func, OBJECTIVE='maximum', save_process=False):

        # Hyperparameters
        self.domain_range = domain_range
        self.fitness_func = fitness_func
        self.OBJECTIVE = OBJECTIVE
        self.save_process = save_process

        # give a random seed
        seed = get_random_seed()
        random.seed(seed)

    # Utils function
    def get_best_one(self, population, fitnesses, OBJECTIVE):

        if OBJECTIVE == 'maximum':
            best_fitness = max(fitnesses)
        elif OBJECTIVE == 'minimum':
            best_fitness = min(fitnesses)

        # if there is more than one optimal solution, it can return a list of best_individual
        best_individual = population[fitnesses.index(best_fitness)]

        return best_individual, best_fitness

    # Main function
    def optimize(self):

        result_dict = {}
        process_dict = {}
        population = []
        fitnesses = []

        grid_range = list(itertools.product(*self.domain_range))

        for individual in tqdm(grid_range):
            fitness = self.fitness_func(individual)
            population.append(individual)
            fitnesses.append(fitness)

        if self.save_process == True:
            population = [list(i) for i in population]
            process_dict = {'population': population, 'fitnesses': fitnesses}

        best_individual, best_fitness = self.get_best_one(population, fitnesses, self.OBJECTIVE)

        result_dict['best_individual'] = best_individual
        result_dict['best_fitness'] = best_fitness
        result_dict['cal_times'] = len(grid_range)
        result_dict['process_dict'] = process_dict

        return result_dict


class SimulatedAnnealing:

    def __init__(self, domain_range, fitness_func, T0=100, Tf=0.001, 
                 alpha=0.97, Q=2, expended_ratio=0.15, max_count=1500, 
                 OBJECTIVE='maximum', save_process=False):

        # Hyperparameters
        self.domain_range = domain_range
        self.fitness_func = fitness_func
        self.T0 = T0
        self.Tf = Tf
        self.alpha = alpha
        self.Q = Q
        self.expended_ratio = expended_ratio
        self.max_count = max_count
        self.OBJECTIVE = OBJECTIVE
        self.save_process = save_process

        # give a random seed
        seed = get_random_seed()
        random.seed(seed)

   # Neighborhood function
    def neighborhood_func(self, individual, expended_ratio, domain_range):

        new_individual = individual.copy()

        for gene, gene_range, num in zip(individual, domain_range, range(len(individual))):
            params_len = len(gene_range)
            expend_len = int(params_len*expended_ratio)
            num_index = gene_range.index(gene)

            new_index_lower_bound = num_index - expend_len
            new_index_upper_bound = num_index + expend_len

            if new_index_lower_bound < 0:
                new_index_lower_bound = 0
            
            if new_index_upper_bound > params_len-1:
                new_index_upper_bound = params_len-1

            new_index = random.randint(new_index_lower_bound, new_index_upper_bound)
            new_individual[num] = gene_range[new_index]

        return new_individual

    # Utils function
    def cal_fitness(self, individual, fitness_func, record_dict={}):

        individual_tuple = tuple(individual)

        if individual_tuple in record_dict.keys():
            fitness = record_dict[individual_tuple]
        else:
            fitness = fitness_func(individual)
            record_dict[individual_tuple] = fitness
            
        return fitness, record_dict

    # Main function
    def optimize(self):

        """
        T0: init temperature
        Tf: target temperature
        alpha: cooling rate
        Q: equilibrium time
        """

        result_dict = {}
        record_dict = {}
        process_dict = {}
        population = []
        fitnesses = []
        temperature = []
        delta_list = []
        accept_list = []

        T = self.T0
        count = 0
        q_sleep = 0

        sa_count = math.ceil(math.log(self.Tf / self.T0, self.alpha)) * self.Q
        total_times = min(sa_count, self.max_count)

        pbar = tqdm(desc="simulated annealing", total=total_times)

        while T > self.Tf:

            if count == 0:
                individual = [random.choice(domain) for domain in self.domain_range]
                fitness, record_dict = self.cal_fitness(individual, self.fitness_func, record_dict)
                delta_E = np.nan
                p_accept = np.nan
                
            else:
                new_individual = self.neighborhood_func(individual, self.expended_ratio, self.domain_range)
                new_fitness, record_dict = self.cal_fitness(new_individual, self.fitness_func, record_dict)
                
                if self.OBJECTIVE == 'maximum':
                    delta_E = new_fitness - fitness
                elif self.OBJECTIVE == 'minimum':
                    delta_E = fitness - new_fitness

                if delta_E > 0:
                    individual = new_individual
                    fitness = new_fitness
                    p_accept = np.nan
                else:
                    p_accept = math.exp(delta_E / T)
                    if random.uniform(0, 1) < p_accept:
                        individual = new_individual
                        fitness = new_fitness

            q_sleep += 1
            count += 1
            pbar.update(1)

            if self.save_process == True:
                population.append(individual)
                fitnesses.append(fitness)
                temperature.append(T)
                delta_list.append(delta_E)
                accept_list.append(p_accept)

            # if Equilibrium (run Q times), cool down temperature
            if q_sleep >= self.Q:
                T *= self.alpha
                q_sleep = 0

            # force stop if count is better than max_count
            if count >= self.max_count:
                break

        if self.save_process == True:
            process_dict = {'population': population, 'fitnesses': fitnesses, 
                            'temperature': temperature, 'delta_E': delta_list, 
                            'p_accept': accept_list}

        result_dict['best_individual'] = individual
        result_dict['best_fitness'] = fitness
        result_dict['cal_times'] = count
        result_dict['process_dict'] = process_dict

        return result_dict

