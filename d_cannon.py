import numpy as np

def d_cannon_hit(hit_requirement):
    D3 = np.arange(3) + 1
    D6 = np.arange(6) + 1
    n_shots = np.random.choice(D3, size = 1)
    hit_vector = np.zeros(n_shots)
    reroll_counter = 1
    for i in np.arange(n_shots[0]):
        hit_roll = np.random.choice(D6, size = 1)[0]
        hit_vector[i] = hit_roll
        if reroll_counter > 0 and hit_roll < hit_requirement:
            reroll = np.random.choice(D6, size = 1)[0]
            hit_vector[i] = reroll
            reroll_counter -= 1
    hit_count = np.sum(hit_vector >= hit_requirement)
    return hit_count

n_sims = 100000
sims = np.array([d_cannon_hit(4) for i in range(n_sims)])
print(np.mean(sims), np.unique(sims, return_counts=True), np.unique(sims, return_counts=True)[1]/n_sims)

        
