import numpy as np
toughness = 10
strength = 7

def realize_wounds(hit_requirement, wound_requirement, lethal, sustained, reroll = False):
    D6 = np.arange(6) + 1
    wound_count = 0
    hit_roll = np.random.choice(D6, size = 1)
    if hit_roll == 6 and lethal == True:
        wound_count = 1
    elif hit_roll == 6 and sustained == True:
        w1_r = realize_wounds(1, wound_requirement, False, False, reroll) # hit req 1 = always hits
        w2_r = realize_wounds(1, wound_requirement, False, False, reroll)
        wound_count = wound_count + w1_r + w2_r
    elif hit_roll >= hit_requirement:
        wound_roll = np.random.choice(D6, size = 1)
        if wound_roll >= wound_requirement:
            wound_count = 1
        elif wound_roll < wound_requirement and reroll:
            wound_count = realize_wounds(1, wound_requirement, False, False, False) # explicitly set reroll to False to not get recursive rerolls
    return wound_count

def wound_sims(hit_requirement, s, t, N, mode, reroll = False):
    if s == t:
        wound_requirement = 4
    elif s/t <= 0.5:
        wound_requirement = 2
    elif s/t >= 2:
        wound_requirement = 6
    elif s < t:
        wound_requirement = 5
    elif s > t:
        wound_requirement = 3
    if mode == 'lethal':
        sims = np.array([realize_wounds(hit_requirement, wound_requirement, lethal = True, sustained = False, reroll = reroll) for i in range(N)])
    elif mode == 'sustained':
        sims = np.array([realize_wounds(hit_requirement, wound_requirement, lethal = False, sustained = True, reroll = reroll) for i in range(N)])
    #print(sims)
    return np.mean(sims)

print(wound_sims(2, 7, 10, 50000, 'lethal', reroll = True), 'lethal')
print(wound_sims(2, 7, 10, 50000, 'sustained', reroll = True), 'sustained')
        
