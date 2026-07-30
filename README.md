## A Small Study on Trust

While browsing online, I came across a game about interpersonal trust strategies. I found the idea quite interesting, so I decided to run a few experiments of my own.

Anyone interested in exploring the topic can start here:

https://audreyt.github.io/trust-zh-TW/

Now, let us begin.

### Game Setup

Suppose that each person in a relationship has two possible choices: cooperate or betray.

In most situations, mutual cooperation creates a win-win outcome, while betrayal can provide a larger short-term reward. However, if both sides choose to betray, neither receives any benefit. The payoff structure can therefore be represented as follows:

![payoff](https://hackmd.io/_uploads/ByzomcVTC.png)

This payoff structure has an important property.

If the game is played only once, no rational player will choose to cooperate when attempting to maximize their individual payoff. The interesting part, however, is that cooperation in real life often continues over a long period.

When two people expect to interact repeatedly, trust becomes important because maintaining cooperation may produce greater long-term benefits for both sides.

Based on this idea, I introduced several simple strategies and simulated 100 games under different expected interaction lengths. The number of interactions was sampled from a Poisson distribution.

1. **Random Strategy:** Cooperates with a probability of 50% and betrays with a probability of 50%.
2. **Cooperator Strategy:** Always cooperates.
3. **Cheater Strategy:** Always betrays.
4. **Copycat Strategy:** Cooperates in the first round and then copies the opponent’s previous action.
5. **Grudger Strategy:** Continues cooperating until the opponent betrays once, after which it betrays permanently.

![plot\_o110](https://hackmd.io/_uploads/HJifQ_4pC.png)

The simulation shows that when the expected number of interactions exceeds three, the Mean Strategy can no longer survive because it is unable to establish trust.

The strategies that remain successful are the Nice Strategy, the Gangster Strategy, and the Copycat Strategy.

### Error Rate

In real-life interactions, people sometimes hurt each other unintentionally. Cooperation may also fail because of misunderstandings, communication errors, or incomplete information.

To model this behavior, I introduced an error rate into the simulation. I fixed the expected interaction length at seven rounds using a Poisson distribution with $\lambda = 7$.

![plot\_1o7](https://hackmd.io/_uploads/H1iCduE6R.png)

After introducing errors, the Gangster Strategy and the Copycat Strategy performed best.

However, does this mean that we should permanently betray someone after a single mistake? Should we always respond to accidental harm with immediate retaliation?

To investigate this question, I introduced a sixth strategy:

6. **Copykitten Strategy:** Cooperates by default. If the opponent betrays twice in a row, it begins copying the opponent’s actions.

![plot\_2o7](https://hackmd.io/_uploads/ryAR__4TA.png)

The results show that after the Tolerant Strategy is introduced, the Gangster Strategy and the Copycat Strategy are clearly outperformed.

Next, I increased the level of tolerance even further:

7. **Copy3kitten Strategy:** Cooperates by default. It only begins copying the opponent’s actions after the opponent betrays three times in a row.

![plot\_3o7](https://hackmd.io/_uploads/BkWs5O4aC.png)

The results show that the Highly Tolerant Strategy performs similarly to the Tolerant Strategy. Under high error rates, both strategies are also effective at suppressing the Mean Strategy.

### Additional Experiments

To make the analysis more diverse, I introduced two additional strategies and conducted larger-scale simulations under different conditions:

8. **NegtiveCopycat Strategy:** Betrays in the first round and then copies the opponent’s previous action.
9. **NegtiveCopykitten Strategy:** Betrays by default. If the opponent cooperates twice in a row, it begins copying the opponent’s actions.

The simulations covered expected interaction lengths from 1 to 10 and error rates ranging from 0 to 0.5.

![plot\_10](https://hackmd.io/_uploads/Hk8zgYV6R.png)

### Conclusion

When the expected number of interactions is two or fewer, the three best-performing strategies are the Mean Strategy, the Highly Cautious Strategy, and the Cautious Strategy.

When the expected number of interactions is three, no strategy is clearly dominant.

When the expected number of interactions is four or more, the three best-performing strategies are the Highly Tolerant Strategy, the Tolerant Strategy, and the Copycat Strategy.

In other words, this environment suggests the existence of a broadly adaptive strategy:

When cooperation is expected to be short-term, betrayal may be the most beneficial approach. When cooperation is expected to continue for a long time, tolerance and forgiveness become more effective.

### Other Observations

The following result is particularly interesting. It was produced with an expected interaction length of 100 rounds, even though relationships involving 100 repeated interactions may be relatively uncommon in real life outside of family relationships or other close long-term connections.

A possible explanation is that long-term cooperative environments encourage people to tolerate occasional mistakes. As a result, individuals who behave randomly and unpredictably may exploit this tolerance and obtain the greatest benefit.

![plot\_3o100](https://hackmd.io/_uploads/BJ0SFKEaA.png)

### Source Code

https://github.com/svavil/evolution-of-trust.git
