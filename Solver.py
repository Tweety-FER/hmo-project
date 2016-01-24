# -*- coding: utf-8 -*-

from Parser import Parser
from GABase import GeneticAlgorithm
from GAImpl import ScheduleEvaluator, GreedySchedulePopulationGenerator

POP_SIZE = 50
MAX_ITER = 1000
MIN_ERR = 5000

def marker(d):
    if d != 0 and (d % 7 == 5 or d % 7 == 6):
        return 'W'
    return '-'

p = Parser()
problem = p.parse('instance.txt')

pop_gen = GreedySchedulePopulationGenerator(problem)
evaluator = ScheduleEvaluator(problem)
ga = GeneticAlgorithm(pop_gen, evaluator)
ga.print_every = 50
#pop = pop_gen.generate_population(1)[0]

#employee = problem.employees[12]
#row = pop._matrix[12]

#for day, e in enumerate(row):
#    print '{} {:3d} : {}'.format(marker(day), day, 'x' if day in employee.days_off else e)
#evaluator.evaluate(pop)

solution, score = ga.run(POP_SIZE, MIN_ERR, MAX_ITER)
is_feasible = evaluator.is_feasible(solution)

print '------------------------------------'
print 'Final score', score, 'Feasible?', is_feasible

with open('res-last.txt', 'w') as fp:
    fp.write(str(score) + ', ' + str(is_feasible) + '\n')
    fp.write(str(solution))
