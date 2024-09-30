import numpy as np
import cloud
levels = 3
# files = [open(files_folder + f"floor{i + 1}.csv", ) for i in range(levels)]
# files.insert(0, pd.read(files_folder + "total.csv"))
def updatescore(name : str, score : int, where : str):
    lfile = cloud.get_as_list(where)
    # print(npfile)
    line = len(lfile)
    for i in range(len(lfile)):
        if int(lfile[i][1]) <= score:
            line = i
            break
    lfile.insert(line, [name, f"{score}"])
    # print(lfile)
    cloud.upload_np(lfile, where)
    return line == 0 # if it is a HighScore!

