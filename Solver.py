# -*- coding: utf-8 -*-

from Parser import Parser
from GABase import GeneticAlgorithm
from GAImpl import ScheduleEvaluator, RandomSchedulePopulationGenerator

POP_SIZE = 50
MAX_ITER = 500
MIN_ERR = 10000


p = Parser()
problem = p.parse('instance.txt')

pop_gen = RandomSchedulePopulationGenerator(problem)
evaluator = ScheduleEvaluator(problem)
ga = GeneticAlgorithm(pop_gen, evaluator)
ga.print_every = 50

print ga.run(POP_SIZE, MIN_ERR, MAX_ITER)
