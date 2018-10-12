from numpy import array, dot, exp, power, random, reshape, sum

class NeuralNetwork:
    def __init__(self, dimensions, weights=None, mutate_prob=0.03):
        self.total_layers = len(dimensions)

        if weights is None:
            self.weights = []
            for i in range(self.total_layers - 1):
                w = 2*random.rand(dimensions[i], dimensions[i+1]) - 1
                self.weights.append(w)
        else:
            for column in weights:
                for i in range(len(column)):
                    if mutate_prob > random.rand():
                        column[i] = 2*random.rand() - 1
            self.weights = weights
    
    def activation(self, X):
        return 1 / (1 + exp(-X))
    
    def feed_forward(self, X):
        l = X
        for w in self.weights:
            l = self.activation(dot(l, w))
        self.y = l
    
    def find_error(self, target):
        error = power(target - self.y, 2)
        return error