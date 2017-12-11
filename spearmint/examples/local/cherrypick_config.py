import math

EXPERIMENT = 'local'
GAMMA = 0.48
COST_FUNC = lambda run: math.log(run.cost * 100)
TIME_LIMIT = -1


def filter_runs(runs):
    def bad_runs(run):
        return run.config.count == 0
    return filter(bad_runs, runs)