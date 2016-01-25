# -*- coding: utf-8 -*-

from Parser import Parser
from GABase import GeneticAlgorithm
from GAImpl import ScheduleEvaluator, MixedPopulationGenerator

POP_SIZE = 100
MAX_ITER = 1000
MIN_ERR = 5000

def marker(d):
    if d != 0 and (d % 7 == 5 or d % 7 == 6):
        return 'W'
    return '-'

p = Parser()
problem = p.parse('instance.txt')

pop_gen = MixedPopulationGenerator(problem)
evaluator = ScheduleEvaluator(problem)

ga = GeneticAlgorithm(pop_gen, evaluator)
ga.print_every = 25

for i in xrange(1):
    solution, score = ga.run(POP_SIZE, MIN_ERR, MAX_ITER)
    is_feasible = evaluator.is_feasible(solution)

    print 'Final score', score, 'Feasible?', is_feasible

    if is_feasible:
        with open('solutions/res-' + str(score) + '.txt', 'w') as fp:
            fp.write(str(solution))
