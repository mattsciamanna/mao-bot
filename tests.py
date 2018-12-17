import subprocess
import sys
import random
from game import *

random.seed(22)
playStyle = None
agent1 = None
agent2 = None
agent3 = None
agent4 = None
# if they've provided us one argument at least
if len(sys.argv) >= 2:
    playStyle = sys.argv[1]
if len(sys.argv) >= 3: 
    numGames = sys.argv[2]
if len(sys.argv) >= 4:
    agent1 = sys.argv[3]
if len(sys.argv) >= 5:
    agent2 = sys.argv[4]
if len(sys.argv) >= 6:
    agent3 = sys.argv[5]
if len(sys.argv) >= 7:
    agent4 = sys.argv[6]

def usage():
    print "A simple way to test the features of our agents"
    print "USAGE: tests.py [playstyle] [# of games] [agent1] [agent 2] [agent3] [agent 4]\n MANDATORY ARGS: \n playstyle:       [montecarlo] - Montecarlo test on an agent starting with each of 14 cards \n                  [playing] - Runs two or more agents against each other \n                  [all] - a quick example of all current testing\n"
    print " # of games:            an integer number of games to play\n"
    # CHANGE WITH NEW AGENTS!
    print " OPTIONAL ARGS: \n  agent1:         [human] - Real Player \n                  [hmm] - Hidden Markov AI agent\n                  [simple] - Simple AI agent\n                  [cardcounter] - Expectimax Strategy Agent"
    print "  agent2:         Same options as agent1 "
    print "  agent3:         Same options as agent1 "
    print "  agent4:         Same options as agent1 "

# takes a list of the agnets input, maps it to real agents
def cliToPlayer(cli):
    agents = []
    for i, agent in enumerate(cli):
        # CHANGE WITH NEW AGENTS!
        if agent == "human":
            namestr = "Human Player%s" % (i,)
            agents.append(HumanAgent(namestr))
        elif agent == "hmm":
            namestr = "Hmm AI Player%s" % (i,)
            agents.append(HmmAgent(namestr))
        elif agent == "simple":
            namestr = "Simple AI Player%s" % (i,)
            agents.append(LearningAgent(namestr))
        elif agent == "cardcounter":
            namestr = "Expectimax Player%s" % (i,)
            agents.append(cardCounter(namestr))
        elif agent == "qlearn":
            namestr = "RL Player%s" % (i,)
            agents.append(qLearner(namestr))
        elif agent == None:
            continue
        else:
            print "Error: Incorrect Agent Specified!"
    return agents


# If the user has requested help or provided no arguments
if playStyle == "--help" or playStyle == "-h":
    usage()
elif playStyle == None:
    usage()
else:
    cli = [agent1, agent2, agent3, agent4]
    gameAgents = cliToPlayer(cli)
    if playStyle == "playing":
        try:
            g = Game(gameAgents, True)
            g.playGame(int(numGames))
            for player in g.players:
                print player.name
                print player.wins
                if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent:
                    print np.average(player.validPercentByRound)
        except:
            print "Something went wrong, be sure to check your agents and number of games "
    elif playStyle == "montecarlo":
        # @TD
        print "Montecarlo requested"
    elif playStyle == "all":
        print "Human Agent Vs AI"
        agent1 = HumanAgent("Human Player1")
        agent2 = qLearner("Q-Learned Player")
        g = Game([agent1, agent2], False)
        g.playGame(int(numgames))
        print "AI vs AI"
        agent1 = qLearner("Q-Learned Player1")
        agent2 = qLearner("Q-Learned Player2")
        g = Game([agent1, agent2], True)
        g.playGame(int(numGames))
        for player in g.players:
                print player.name
                print player.wins
        print "AI VS Adverserial"
        agent1 = qLearner("Q-Learned Player1")
        agent2 = cardCounter("Q-Learned Player2")
        g = Game([agent1, agent2], True)
        g.playGame(int(numGames))
        for player in g.players:
                print player.name
                print player.wins
