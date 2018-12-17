from qOutput import *
from qTraining import *
from agents import *
from game import *
import pickle

random.seed(10)

def play1():
    pBot2 = RandomAgent("Hmm")
    # qBot1 = RandomAgent("random")
    qBot1 = QPlayer('qPlayer', featureSet1, pickle.loads(trainingWeights1), pBot2) #default values
    
    random.seed(183)
    g = Game([qBot1, pBot2], True)
    g.playGame(100)

    # #print stats
    for player in g.players:
        print player.name
        print player.wins
        if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent or type(player) == QPlayer:
            print np.average(player.validPercentByRound)

def play2():
    pBot2 = RandomAgent("Random")
    # qBot1 = RandomAgent("random")
    qBot1 = QPlayer('qPlayer', featureSet2, pickle.loads(bigtrainingweights2), pBot2) #default values
    
    random.seed(183)
    g = Game([qBot1, pBot2], True)
    g.playGame(1000)

    # #print stats
    for player in g.players:
        print player.name
        print player.wins
        if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent or type(player) == QPlayer:
            print np.average(player.validPercentByRound)

play2()
