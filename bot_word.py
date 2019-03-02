from itertools import cycle
import os
import time
from inputimeout import inputimeout, TimeoutOccurred

with open('./total_word_counts.txt') as ff:
    data = ff.readlines()

with open('./word_labels.txt') as ff:
    lab = ff.readlines()

data = [(x.split()[0], None) for x in data]
lab = set([x.split()[0] for x in lab])


def labelize():
    count_labels = 0

    for i in cycle(range(len(data))):
        os.system('clear')
        if count_labels == len(data):
            break

        word, label = data[i]

        if word in lab:
            continue

        if label:
            continue

        try:
                res = inputimeout('{} '.format(word), timeout=10)
                res = int(res)
                with open("word_labels.txt", "a") as myfile:
                    myfile.write("{} {}\n".format(word, res))
        except:
            continue


labelize()








