import os

BO_PATH = os.path.abspath(os.path.dirname(__file__))
EXP_PATH = os.path.join(BO_PATH, "examples")
EXE_PATH = os.path.join(os.path.dirname(BO_PATH), "bin")
RESULT_PATH = os.path.join(os.path.dirname(BO_PATH), "results")
TEMPLATE_PATH = os.path.join(EXP_PATH, "template")
MAIN_PATH = os.path.join(BO_PATH, "spearmint", "main.py")

# GAMMA = 0.4

# data_split = [0, 1, 3, 5]
#
# flavor_space = [
#     "m1.medium",
#     "m1.large",
#     "m1.xlarge",
#     "r2.small",
#     "r2.medium",
#     "r2.large",
#     "r2.xlarge",
#     "c3.medium",
#     "c3.large",
#     "c3.xlarge"
# ]
#
# machine_space = [2, 4, 8, 16]