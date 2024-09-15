# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 18:13:17 2021

@author: vavilse1
"""

from bots import *
from itertools import combinations
from random import randint
import numpy as np
import json

payout = {
    ("C", "C"): (2, 2),
    ("C", "N"): (-1, 3),
    ("N", "C"): (3, -1), 
    ("N", "N"): (0, 0)
}

def match(bot1, bot2, error_rate=0.05, n=10):
    bot1.clear_history()
    bot2.clear_history()
    score1, score2 = 0, 0
    
    # play n games
    gamecnt = int(np.random.poisson(n))
    for _ in range(gamecnt): # play "expect" n games
        resp1 = bot1.move()
        resp2 = bot2.move()
        
        if resp1 == "C" and randint(0, 100) < error_rate * 100:
            resp1 ="N"
        if resp2 == "C" and randint(0, 100) < error_rate * 100:
            resp2 ="N"
        
        bot1.append_history(resp2)
        bot2.append_history(resp1)
        
        dscores = payout[(resp1, resp2)]
        
        score1 += dscores[0]
        score2 += dscores[1]
        
    return (score1, score2)

def evolution(bots_list, n=10, elim=1, error_rate=0.05):
    # play n matchs between all pairs
    scores = {bot.uid: 0 for bot in bots_list}
    for pair in combinations(bots_list, 2):
        dscores = match(pair[0], pair[1], error_rate, n)
        scores[pair[0].uid] += dscores[0]
        scores[pair[1].uid] += dscores[1]
    
    # eliminate the worst bots, replace them with the best bots
    bots_list = sorted(bots_list, key = lambda bot: scores[bot.uid], reverse = True)
    new_bots_list = bots_list[:-elim]
    for bot in bots_list[:elim]:
        new_bots_list.append(bot.__class__())
        
    return new_bots_list

def simulate_evolution(bot_dict, n=10, elim=5, error_rate=0.05, generations=10, debug=False):
    bots_list = []
    for bot in bot_dict.keys():
        bots_list += [eval(bot)() for _ in range(bot_dict[bot])]
        
    for _ in range(generations):
        bots_list = evolution(bots_list, n, elim, error_rate)
        if debug:
            print("\nGeneration", _ + 1)
            cnt_bots = {bot.__class__.__name__: 0 for bot in bots_list}
            for bot in bots_list:
                cnt_bots[bot.__class__.__name__] += 1
            for bot in cnt_bots:
                print(cnt_bots[bot], bot)
    cnt_bots = {bot.__class__.__name__: 0 for bot in bots_list}
    for bot in bots_list:
        cnt_bots[bot.__class__.__name__] += 1
    return cnt_bots

def statistics_simulation(bot_dict, n=10, elim=5, error_rate=0.05, generations=10, simulations=10):
    cnt_bots = {bot: 0 for bot in bot_dict}
    for _ in range(simulations):
        final = simulate_evolution(bot_dict, n=n, elim=elim, error_rate=error_rate, generations=generations)
        print("Simulation", _ + 1, ":", final)
        for bot in final.keys():
            cnt_bots[bot] += final[bot]
    return cnt_bots

if __name__ == "__main__":
    bot_dict = {
        "Random": 4,
        "Cooperator": 4,
        "Cheater": 4,
        
        "Copycat": 4,
        "Copykitten": 4,
        "Copy3kitten": 4,

        "NegtiveCopycat": 4,
        "NegtiveCopykitten": 4,
        
        "Grudger": 4,
    }

    # result_dict = {}
    # for ccnt in np.arange(100, 101, 1):
    #     result_dict[str(ccnt)] = {}
    #     for er in np.arange(0, 11, 1):
    #         print("Simulation for ccnt =", ccnt, "er =", er)
    #         st_sim = statistics_simulation(bot_dict, n=ccnt, elim=3, error_rate=er/20, generations=100, simulations=30)
    #         result_dict[str(ccnt)][str(er)] = st_sim
    #         print(st_sim)
    # with open("result_100.json", "w") as f:
    #     json.dump(result_dict, f)
    st_sim = simulate_evolution(bot_dict, n=7, elim=3, error_rate=0.04, generations=100, debug=True)
    print(st_sim)