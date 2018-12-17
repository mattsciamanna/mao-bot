from game import *
import pickle

 #  _______        _       _               __ 
 # |__   __|      (_)     (_)             /_ |
 #    | |_ __ __ _ _ _ __  _ _ __   __ _   | |
 #    | | '__/ _` | | '_ \| | '_ \ / _` |  | |
 #    | | | | (_| | | | | | | | | | (_| |  | |
 #    |_|_|  \__,_|_|_| |_|_|_| |_|\__, |  |_|
 #                                  __/ |     
 #                                 |___/      
featureSet1 = [SizeofHand(), HighCount(), LowCount(), Illegality()]

def train1():
    qBot1 = QLearner('qBot1', featureSet1) #default values
    pBot2 = HmmAgent("A2")
    
    random.seed(182)
    g = Game([qBot1, pBot2], True)
    g.playGame(5000)

    # #print stats
    for player in g.players:
        print player.name
        print player.wins
        if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent:
            print np.average(player.validPercentByRound)
        if type(player) == QLearner:
            print player.weights
            print 'Training 1: pickled weights:', pickle.dumps(player.weights)

featureSet2 = [SizeofHand(), OpponentCards(), Illegality()]
def train2():
    qBot1 = QLearner('qBot1', featureSet2) #default values
    pBot2 = RandomAgent("Random2")
    
    random.seed(182)
    g = Game([qBot1, pBot2], True)
    g.playGame(10000)

    # #print stats
    for player in g.players:
        print player.name
        print player.wins
        if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent:
            print np.average(player.validPercentByRound)
        if type(player) == QLearner:
            print player.weights
            print 'Training 1: pickled weights:', pickle.dumps(player.weights)

# see output.py for the pickled output
# train2()