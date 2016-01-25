# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint, random

class Instance(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def mutate(self):
        pass

    @abstractmethod
    def cross(self, other):
        pass

class Evaluator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate(self, instance):
        pass

class PopulationGenerator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_population(self, size):
        pass

class GeneticAlgorithm(object):
    def __init__(self, pop_gen, evaluator):
        self._pop_gen = pop_gen
        self._eval = evaluator
        self.print_every = None

    def _select_from_pop(self, eval_pops, score_sum):
        curr_sum = 0
        i = 0
        selection = random() * score_sum

        for score, pop in eval_pops:
            fitness = 1.0 / score
            if curr_sum <= selection <= curr_sum + fitness:
                return pop

            curr_sum += fitness

            i += 1

        return eval_pops[-1][1] # Default to the last one. Should not be reached



    def run(self, pop_size, min_score, max_iter):
        pops = self._pop_gen.generate_population(pop_size)
        best_score = None

        for i in xrange(max_iter):
            # Evaluate the current pop
            eval_pops = sorted([(self._eval.evaluate(pop), pop) for pop in pops])
            score_sum = sum([1.0 / v[0] for v in eval_pops])

            # Generate a new population (elitism!)
            pops = [x[1] for x in eval_pops[0:5]]

            if best_score is None:
                best_score = eval_pops[0][0]
            else:
                best_score = min(best_score, eval_pops[0][0])

            if self.print_every is not None and i % self.print_every == 0:
                print 'Iteration {0}, best score {1}'.format(i, self._eval._evaluate(pops[0]))

            if best_score is not None and best_score <= min_score:
                break

            for i in xrange(5, pop_size):
                parent_a = self._select_from_pop(eval_pops, score_sum)
                parent_b = self._select_from_pop(eval_pops, score_sum)
                child = parent_a.cross(parent_b).mutate()
                pops.append(child)

        return pops[0], best_score
