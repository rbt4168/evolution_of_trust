import matplotlib.pyplot as plt
import numpy as np
import json
# data from https://allisonhorst.github.io/palmerpenguins/

with open("result.json", "r") as f:
    result_dict = json.load(f)

# reconstruct the data
result = {}

fig, ax = plt.subplots(5, 2, figsize=(15, 20))

for ccnt in np.arange(1, 11, 1):
    er_labels = []
    all_categories = {
        "Random": [], 
        "Cooperator": [], 
        "Cheater": [], 
        "Copycat": [], 
        "Grudger": [],
        "Copykitten": [],
        "Copy3kitten": [],
        "NegtiveCopycat": [],
        "NegtiveCopykitten": [],
    }
    for er in np.arange(0, 11, 1):
        er_labels.append(str(round(er/20, 2)))
        for bot in result_dict[str(ccnt)][str(er)]:
            if bot not in all_categories:
                all_categories[bot] = []
            all_categories[bot].append(result_dict[str(ccnt)][str(er)][bot])
    # result[str(ccnt)] = all_categories
#     print(er_labels)
        
# print(result)
    
    # fig.set_size_inches(10, 6)
    bottom = np.zeros(len(er_labels))
    ax_coord = (int((ccnt-1)/2), (ccnt-1)%2)

    for k, v in all_categories.items():
        p = ax[ax_coord[0], ax_coord[1]].bar(er_labels, v, label=k, bottom=bottom)
        bottom += v

    ax[ax_coord[0], ax_coord[1]].set_title("Winning bots in Expected Game Count = " + str(ccnt))
    ax[ax_coord[0], ax_coord[1]].legend(loc="upper left")

plt.savefig("plot_l" + str(ccnt) + ".png")

    # plt.show()