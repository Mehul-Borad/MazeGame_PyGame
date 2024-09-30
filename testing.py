import numpy as np
import pandas as pd

pdfile = pd.read_csv("scores/floor1" + ".csv")
line = 0
for i in range(pdfile.__len__()):
    print(pdfile["score"])
# print(np.array(a == [0,0]).all(1).any(0))