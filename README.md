# Machine learning for Flappy Bird game
A machine learning model that will learn and play flappy bird game. The model is developed using a combination of **Neural networks** and **Genetic algorithm**, combinely known as **NEAT algorithm (NeuroEvolution of Augmenting Topologies)**.

## Overview about NEAT algorithm
from [(wikipedia)](https://en.wikipedia.org/wiki/Neuroevolution_of_augmenting_topologies): **NeuroEvolution of Augmenting Topologies** (NEAT) is a genetic algorithm (GA) for the generation of evolving artificial neural networks (a neuroevolution technique) developed by Ken Stanley in 2002 while at The University of Texas at Austin. It alters both the weighting parameters and structures of networks, attempting to find a balance between the fitness of evolved solutions and their diversity. It is based on applying three key techniques: tracking genes with history markers to allow crossover among topologies, applying speciation (the evolution of species) to preserve innovations, and developing topologies incrementally from simple initial structures ("complexifying").

## Setup instructions
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
### Prerequisites
+ [Python](https://www.python.org/downloads/) (with [numpy](https://docs.scipy.org/doc/numpy-1.15.1/user/install.html) library installed)
### Deploying
+ Clone the Repository `git clone https://github.com/akhil-code/flappy-bird-neuro-evolution`
+ Change current directory to this repository
+ Run the application using command `python app.py`
+ Upon executing the above command, a population of birds will start learning to play the game.

## Authors
+ Akhil Guttula

## Learn more
+ [Genetic Algorithm by Siraj Raval] (https://www.youtube.com/watch?v=rGWBo0JGf50&t=1767s)
+ [Neuro-evolution by Siraj Raval](https://www.youtube.com/watch?v=xLHCMMGuN0Q&t=2578s)
