from numpy import random, array, reshape
from neural import NeuralNetwork
import attrib
import pygame

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
    def __init__(self, feature_limits, pop_size=10, mutate_prob=0.03, retain_prob=0.01, select=0.333):
        self.pop_size = pop_size
        self.mutate_prob = mutate_prob
        self.retain_prob = retain_prob
        self.select = select

        self.feature_limits = feature_limits

        self.fitness_history = []
        self.generation = 1

        self.individuals = [Individual(feature_limits) for i in range(self.pop_size)]
    
    # population fitness
    def grade(self):
        self.population_fitness = max([i.bird.score for i in self.individuals])
        print([i.bird.score for i in self.individuals])
        self.fitness_history.append(self.population_fitness)
    
    def select_parents(self):
        retain_length = int(self.select * self.pop_size)
        self.individuals = sorted(self.individuals, key=lambda x: x.bird.score, reverse=True)
        self.parents = self.individuals[:retain_length]

        unfittest = self.individuals[retain_length:]
        for individual in unfittest:
            if self.retain_prob > random.rand():
                self.parents.append(individual)

    def crossover(self, weights1, weights2):
        weights = []

        for w1, w2 in zip(weights1, weights2):
            w = []
            for column1, column2 in zip(w1, w2):
                column = []
                for theta1, theta2 in zip(column1, column2):
                    choosen = random.choice((theta1, theta2))
                    column.append(choosen)
                w.append(column)
            weights.append(array(w))
        return weights
    
    def breed(self):
        target_children_size = self.pop_size - len(self.parents)
        children = []
        if len(self.parents) > 0:
            while len(children) < target_children_size:
                father = random.choice(self.parents)
                mother = random.choice(self.parents)
                if father != mother:
                    child_weights = self.crossover(father.nn.weights, mother.nn.weights)
                    child = Individual(feature_limits=self.feature_limits, weights=child_weights)
                    children.append(child)
            self.individuals = self.parents + children
    
    def update(self, pipe):
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
        # self.grade()
        # for i in range(len(self.individuals)):
        #     ind = self.individuals[i]
        #     print(f'INDIVIDUAL-{i}\n {ind.nn.weights}')

        self.select_parents()
        self.breed()
        self.parents = []
        self.generation += 1
        # print(f'evolved to {self.generation}')
    
    def reset_individuals_to_inital_state(self):
        for individual in self.individuals:
            individual.bird.__init__()