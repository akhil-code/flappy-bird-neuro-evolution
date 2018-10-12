from numpy import array, dot, exp, power, random, reshape, sum


class NeuralNetwork:
    """
    class used to create neural network objects

    functions
    -----------
    activation : used to calculate activation (sigmoid) of a layer input
    feed_forward : calculates activation values for all the layers for one iteration
    find_error : calculates error of predicted value with the actual value
    """

    def __init__(self, dimensions, weights=None, mutate_prob=0.03):
        """
            used to initialize neural network if weights argument is not provided. 
            Else mutation(by genetic algorithm) of neural network takes place

            parameters
            ------------
            dimensions : list of number of activation units in each layer
            weights : weights of neural network if object is already created (used for mutation)
            mutate_prob : probability that a particular gene is mutated
        """

        # no of layers including input layer
        self.total_layers = len(dimensions)     

        # initializing weights of neural network
        if weights is None:
            self.weights = []
            for i in range(self.total_layers - 1):
                w = 2*random.rand(dimensions[i], dimensions[i+1]) - 1
                self.weights.append(w)
        else:
            # mutate the genes
            for column in weights:
                for i in range(len(column)):
                    if mutate_prob > random.rand():
                        column[i] = 2*random.rand() - 1
            self.weights = weights
    
    def activation(self, X):
        """ calcuates activation of activation units """
        return 1 / (1 + exp(-X))
    
    def feed_forward(self, X):
        """ makes forward propagation for one iteration """
        l = X
        for w in self.weights:
            l = self.activation(dot(l, w))
        self.y = l
    
    def find_error(self, target):
        """ finds error between actual and predicted values """
        error = power(target - self.y, 2)
        return error
