import os

BO_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
EXP_PATH = os.path.join(BO_PATH, "examples")
EXE_PATH = os.path.join(os.path.dirname(BO_PATH), "bin")
RESULT_PATH = os.path.join(os.path.dirname(BO_PATH), "results")

print BO_PATH
print EXP_PATH
print EXE_PATH
print RESULT_PATH
