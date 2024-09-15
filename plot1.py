import matplotlib.pyplot as plt
import numpy as np
import json
# data from https://allisonhorst.github.io/palmerpenguins/

with open("result_100.json", "r") as f:
    result_dict = json.load(f)

# reconstruct the data
result = {}

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
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
er_labels = []
for ccnt in np.arange(100, 101, 1):
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
bottom = np.zeros(11)

for k, v in all_categories.items():
    p = ax.bar(er_labels, v, label=k, bottom=bottom)
    bottom += v

ax.set_title("Winning bots in Expected Game Count = 100")
ax.legend(loc="upper left")

plt.savefig("plot_3o" + str(ccnt) + ".png")

    # plt.show()