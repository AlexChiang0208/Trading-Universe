# %%

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# file path should under level first
os.chdir("..")
print(os.getcwd())

from module.optimization import GeneticAlgorithm, RandomSearch, GridSearch, SimulatedAnnealing, ParticleSwarmOptimization

# %%

# Domains
domain_range = [
    list(range(1, 101)),
    list(range(5, 81)),
    [round(i,1) for i in np.arange(1.5, 2.6, 0.1)],
    [round(i,2) for i in np.linspace(-5.12, 5.12, 125)]
    ]

# Fitness function
def fitness_func(individual):

    a, b, c, d = individual
    fitness_value = a-b-c+d

    return fitness_value

# %%

### Genetic Algorithm ###

# Hyperparameters
INI_SIZE = 200
POP_SIZE = 100
ELITE_SIZE = 10
GENERATIONS = 13
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.01
OBJECTIVE = 'maximum'
SELECTION_STG = 'uniform'
MOVING_STG = True
expended_ratio = 0.15
MOVE_RATE = 0.25
save_process = False

ga_obj = GeneticAlgorithm(domain_range, fitness_func, INI_SIZE, POP_SIZE, ELITE_SIZE, 
                          GENERATIONS, CROSSOVER_RATE, MUTATION_RATE, OBJECTIVE, 
                          SELECTION_STG, MOVING_STG, expended_ratio, MOVE_RATE,
                          save_process)

result = ga_obj.optimize()
result

# %%

### Random Search ###

# Hyperparameters
OBJECTIVE = 'maximum'
search_times = 1500
save_process = False

rs_obj = RandomSearch(domain_range, fitness_func, OBJECTIVE, search_times, save_process)

result = rs_obj.optimize()
result

# %%

### Simulated Annealing ###

# Hyperparameters
T0 = 100
Tf = 0.001
alpha = 0.97
Q = 5
expended_ratio = 0.15 
max_count = 1500
OBJECTIVE = 'maximum'
save_process = False

sa_obj = SimulatedAnnealing(domain_range, fitness_func, T0, Tf, alpha, Q, 
                            expended_ratio, max_count, OBJECTIVE, save_process)

result = sa_obj.optimize()
result

# %%

### Particle Swarm Optimization ###

# Hyperparameters
OBJECTIVE = 'maximum'
num_particles = 50
num_iteration = 30
Velocity_Strategy = 'zero'
W_MAX = 0.8
W_MIN = 0.2
W_Strategy = 'decrease'
C1_MAX = 2
C1_MIN = 0.9
C1_Strategy = 'increase'
C2_MAX = 2
C2_MIN = 0.9
C2_Strategy = 'decrease'
R_MAX = 0
R_MIN = 0
R_Strategy = 'increase'
variable_type = 'discrete'
save_process = False

pso_obj = ParticleSwarmOptimization(domain_range, fitness_func, OBJECTIVE, num_particles, 
                                    num_iteration, Velocity_Strategy, W_MAX, W_MIN, W_Strategy, 
                                    C1_MAX, C1_MIN, C1_Strategy, C2_MAX, C2_MIN, C2_Strategy, 
                                    R_MAX, R_MIN, R_Strategy, variable_type, save_process)

result = pso_obj.optimize()
result

# %%

### Grid Search ###

# Domains
domain_range = [
    list(range(1, 101, 20)),
    list(range(5, 81, 20)),
    [round(i,1) for i in np.arange(1.5, 2.6, 0.5)],
    [round(i,2) for i in np.linspace(-5.12, 5.12, 25)]
    ]

# Hyperparameters
OBJECTIVE = 'maximum'
save_process = False

gs_obj = GridSearch(domain_range, fitness_func, OBJECTIVE, save_process)

result = gs_obj.optimize()
result

# %%
