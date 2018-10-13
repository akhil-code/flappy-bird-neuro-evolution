import pygame
from numpy import array, random, reshape

import attrib
from neural import NeuralNetwork


class Individual:
    dimensions = (5, 5, 5, 1)
    feature_limits = None

    def __init__(self, feature_limits=None, weights=None, mutate_prob=0.03):
        if weights is None:
            self.nn = NeuralNetwork(Individual.dimensions)
        else:
            self.nn = NeuralNetwork(Individual.dimensions, weights=weights, mutate_prob=mutate_prob)
        
        self.bird = attrib.Bird()
        Individual.feature_limits = feature_limits
    
    def find_fitness(self, X):
        # step-1 : feature scaling
        X = X / self.feature_limits
        # step-2 : feed forward
        self.nn.feed_forward(X)
        y = self.nn.y
        if y > 0.5:
            self.bird.fly()
        
        return self.bird.score


class Population:
    """
    class for population of specific generation

    functions
    -----------
    grade : calculates the fitness of that generation
    select_parents : selects the fittest parents of current generation
    crossover : combines the genes of two parent to form genes of child
    breed : creates new children from set of parents
    update : updates the individual of a generation
    evolve : evolves the population to next generation
    reset_individuals_to_inital_state : resets individuals to initial states when evolved

    """
    def __init__(self, feature_limits, pop_size=10, mutate_prob=0.03, retain_prob=0.01, select=0.333):
        self.pop_size = pop_size                # population size of generation
        self.mutate_prob = mutate_prob          # probability of mutation of genes
        self.retain_prob = retain_prob          # probability of selecting unfittest parents
        self.select = select                    # ratio of fittest parents select

        self.feature_limits = feature_limits    # maximum valus of features of neural network (used for normalization)

        self.fitness_history = []               # stores fitness history of generation as list
        self.generation = 1                     # current generation

        self.individuals = [Individual(feature_limits) for i in range(self.pop_size)]   # initializes individuals of population
    
    # population fitness
    def grade(self):
        """ calculates the fitness of that generation """
        self.population_fitness = max([i.bird.score for i in self.individuals])
        print([i.bird.score for i in self.individuals])
        self.fitness_history.append(self.population_fitness)
    
    def select_parents(self):
        """ selects the fittest parents of current generation """
        retain_length = int(self.select * self.pop_size)
        # sorts individual based on their fitness
        self.individuals = sorted(self.individuals, key=lambda x: x.bird.score, reverse=True) 
        self.parents = self.individuals[:retain_length]
        # selecting random unfittest parents
        unfittest = self.individuals[retain_length:]
        for individual in unfittest:
            if self.retain_prob > random.rand():
                self.parents.append(individual)

    def crossover(self, weights1, weights2):
        """ combines the genes of two parent to form genes of child """
        weights = []

        for w1, w2 in zip(weights1, weights2):
            w = []
            for column1, column2 in zip(w1, w2):
                column = []
                for theta1, theta2 in zip(column1, column2):
                    # selecting randomly from father or mother genes
                    choosen = random.choice((theta1, theta2))       
                    column.append(choosen)
                w.append(column)
            weights.append(array(w))
        return weights
    
    def breed(self):
        """ creates new children from set of parents """

        # filling rest of population
        target_children_size = self.pop_size - len(self.parents)
        children = []
        if len(self.parents) > 0:
            while len(children) < target_children_size:
                father = random.choice(self.parents)
                mother = random.choice(self.parents)
                if father != mother:
                    child_weights = self.crossover(father.nn.weights, mother.nn.weights)
                    # mutation
                    child = Individual(feature_limits=self.feature_limits, weights=child_weights)
                    children.append(child)
            self.individuals = self.parents + children
    
    def update(self, pipe):
        """ updates the individual of a generation with current features"""

        for individual in self.individuals:
            X = array([
                individual.bird.posy,
                individual.bird.velocity,
                pipe.gap_start,
                pipe.gap_end,
                pipe.posx,
            ])

            X = reshape(X, (1, -1))

            individual.find_fitness(X)
    
    def evolve(self):
        """
        evolves the population to next generation

        it involves:
        1. selecting fittest parents (with some unfittest as well)
        2. breeding new children
        """
        self.select_parents()
        self.breed()
        self.parents = []
        self.generation += 1
    
    def reset_individuals_to_inital_state(self):
        """ reinstantiates entire population """
        for individual in self.individuals:
            individual.bird.__init__()
