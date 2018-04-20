import os

BO_PATH = os.path.abspath(os.path.dirname(__file__))
EXP_PATH = os.path.join(BO_PATH, "examples")
EXE_PATH = os.path.join(os.path.dirname(BO_PATH), "bin")
RESULT_PATH = os.path.join(os.path.dirname(BO_PATH), "results")
TEMPLATE_PATH = os.path.join(EXP_PATH, "template")
MAIN_PATH = os.path.join(BO_PATH, "spearmint", "main.py")

GAMMA = 0.4

data_split = [0, 1, 3, 5]