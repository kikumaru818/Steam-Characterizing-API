#Xianxing Zhang, Apri 14, Kmeans to group gamers into K clusters.
# The measure distance is initialized as Manhattan distance
import os
from random import randint
import copy
import math as math
import numpy as np
import matplotlib.pyplot as plt
import pickle
import pandas as pd

newPoints=[]

with open("test.txt", 'r') as f:
    save_dict = pickle.load(f)

newPoints=save_dict["points"]
vocab=save_dict["vocab"]

for p in newPoints:
    p.append(0)

# for p in newPoints:
#     print p
# print len(newPoints)
####Step 3: Initialize K clustering, first Set K as 3
###Randomly pick a seed point
# seed = randint(0, len(points) - 1)
# SeedPoint = points[seed]
K = 3
seedPoints = []
for i in range(0,K):
    seedPoints.append(copy.deepcopy(newPoints[randint(0, len(newPoints) - 1)]))

for sp in seedPoints:
    print sp


####Step 4: K means clustering until no point's label
### using Manhattan distance
change = 100
count = 0
while (count < 5 or change > 5):
    change = 0
    for p in newPoints:
        min = 10000
        label = 0
        for i in range(0, len(seedPoints)):
            dis = 0
            sp = seedPoints[i]
            for j in (1, len(p)-1):        #caculate the distance between point and center Point
                dis = dis + abs(float(p[j]) - float(sp[j]))
            if (dis < min):
                min = dis
                label = i
        if (int(label)!= int(p[len(p) - 1])):
            # print ("original label is: " + str(p[len(p) - 1]))
            # print ("new label is: " + str(label))
            # print ("min distance is: " + str(float(min)))
            # print ("the ID is: " + str(p[0]))
            # print p
            p[len(p) - 1] = label             #update label
            change = change + 1



    ## update the mean value of the center points
    # initialize center point to zero
    ClusteringSize = []
    for sp in seedPoints:
        ClusteringSize.append(0)
        for i in range(0, len(sp)):
            sp[i] = 0

    # partition and update the value of the center point
    for p in newPoints:
        for i in range(1, len(p)-1):
            seedPoints[int(p[len(p)-1])][i] += float(p[i])
            ClusteringSize[int(p[len(p)-1])] += 1

    for j in range(0, len(seedPoints)):
        sp = seedPoints[j]
        if (ClusteringSize[j] != 0):
            for i in range(1, len(sp)-1):
                sp[i] = sp[i] / ClusteringSize[j]
    count += 1
    print ("Iteration times: " + str(count))
    print ("value of change: " + str(change))
    for sp in seedPoints:
        print sp

print "done"
####Step 4: print the nodes in clusterings
def results(seedPoints, newPoints, vocab):
    group={}
    for i in range(0, len(seedPoints)):
        group[i]=[]
        print ("the players in clustering No." + str(i) + " are as following: ")
        for p in newPoints:
            if (int(p[len(p) - 1]) == i):
                temp=group[i]
                temp.append(p)
                group[i]=temp
                print p

    print "=========================/n/n"
    for p in seedPoints:
        print p


    vocab["label"]=29

    with open("test_graph_result.txt", 'r') as f:
         pickle.dump([newPoints,seedPoints,vocab],f)


    for i in group:
        if len(group[i])!=0:
            group[i]=np.array(group[i])
            group[i]=group[i].mean(axis=0)
            print group[i]
        else:
            group.pop(i)

    result = group.values()
    #for v in zip(*result):
    #    print (*v)





    return

results(seedPoints, newPoints,vocab)

