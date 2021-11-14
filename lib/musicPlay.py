import os
import random
from pygame.mixer import music


def getRandomMusic():
    appen = []
    for _, _, file in os.walk(r'static'):
        appen.append(file)

    musicListLen = len(appen[0])
    if musicListLen == 0:
        return "No_music"
    RandomNumber = random.randint(0, musicListLen-1)
    return appen[0][RandomNumber]

def loadMusic(musicname):
    musicname = 'static/'+musicname
    return music.load(musicname)



