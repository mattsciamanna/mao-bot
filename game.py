from infrastructure import *
import constraints
import effects
import numpy as np
import time


import copy
from agents import *    
from qLearner import *


class Game(object):
    def __init__(self, players, autogame = True, TESTCARD = None):
        
        # constraints
        self.basicValueConstraint = constraints.BasicValueConstraint(True)
        self.basicSuitConstraint = constraints.BasicSuitConstraint()
        self.wildValueConstraint = constraints.WildValueConstraint()
        self.wildSuitEffect = constraints.WildSuitEffect()
        self.poisonDistanceConstraint = constraints.PoisonDistanceConstraint()
        
        self.poisonCardEffect = effects.PoisonCardEffect()
        self.skipPlayerEffect = effects.SkipPlayerEffect()
        self.screwOpponentEffect = effects.ScrewOpponentEffect()
        
        
        # player stuff
        self.players = players
        self.activePlayer = 0 # the player after the dealer goes first. keeps track of which player is up
        self.autogame = autogame
        
        #deck stuff
        self.startingHandSize = 5
        self.changeRuleRate = 1 #invariant -- DO NOT CHANGE

        self.deck = Deck() #pre-shuffled deck
        self.pile = [] # a list of discarded cards. DIFFERENT FROM DECK OBJECT. 
        self.lastCard = None
        
        #round stuff
        self.round = 0 # record which round we are on
        self.gameHistory = GameHistory() # records the history of the game for training data
        self.roundHistory = RoundHistory()
        self.heuristicMode = False
        if TESTCARD:
            self.heuristicMode = True
            self.testCard = TESTCARD 
        
    def deliverCombostate(self):
        bVal = Rule(BASICVALUE, self.basicValueConstraint.greater)
        wVal = Rule(WILDVALUE, self.wildValueConstraint.wildValue)
        wSuit = Rule(WILDSUIT, self.wildSuitEffect.wildSuit)
        pDist = Rule(POISONDIST, self.poisonDistanceConstraint.dist)
        
        pCard = Rule(POISONCARD, self.poisonCardEffect.value)
        skip = Rule(SKIPPLAYER, self.skipPlayerEffect.activatingValue)
        screw = Rule(SCREWOPPONENT, self.screwOpponentEffect.activatingValue)
        
        state = State(bVal, wVal, wSuit, pDist)
        effectState = EffectState(pCard, screw, skip)
        
        return CombinedState(state, effectState)
        
    def makeModification(self, ruleTuple):
        rule = ruleTuple.rule
        setting = ruleTuple.setting
        
        if rule == BASICVALUE:
            self.basicValueConstraint.modify(setting)
        elif rule == BASICSUIT:
            pass
        elif rule == WILDSUIT:
            self.wildSuitEffect.modify(setting)
        elif rule == WILDVALUE:
            self.wildValueConstraint.modify(setting)
        elif rule == POISONDIST:
            self.poisonDistanceConstraint.modify(setting)
        elif rule == SCREWOPPONENT:
            self.screwOpponentEffect.modify(setting)
        elif rule == SKIPPLAYER:
            self.skipPlayerEffect.modify(setting)
        elif rule == POISONCARD:
            self.poisonCardEffect.modify(setting)
            
    def isLegal(self, attemptedCard):
        """ 
        Evaluates the card against the current constraints to see whether it is viable or not
        Returns True or False
        """
        
        #poison distance is the most powerful effect
        if self.poisonDistanceConstraint.isActive(attemptedCard):
            if (not self.poisonDistanceConstraint.isLegal(attemptedCard, self.lastCard)):
                return False
        
        #try effects. needs only ONE to return True
        wildConstraints = [self.wildValueConstraint, self.wildSuitEffect]
        
        for effect in wildConstraints:
            if (effect.isActive(attemptedCard)):
                if (effect.isLegal(attemptedCard, self.lastCard)):
                    return True
        
        # try the basics (ie, ordering and other). These are always active
        # need only ONE to pass as true
        basicConstraints = [self.basicValueConstraint, self.basicSuitConstraint]
        
        for constraint in basicConstraints:
            if (constraint.isLegal(attemptedCard, self.lastCard)):
                return True
        return False # if all the constraints pass, return true
        
    
    def notifyAll(self, notification):
        """
        Notifies all players of a change in the gamestate.
        The "game history" is also notified
        """
        # print stuff for human players for human players
        type = notification.type
        
        if not self.autogame and not type == SKIPPLAYER: print self.players[self.activePlayer].name
        if type == LEGAL:
            # self.roundHistory.recordMove(notification)
            if not self.autogame: print "LEGAL CARD PLAYED:", notification.attemptedCard, "\n"
        elif type == PENALTY:
            # self.roundHistory.recordMove(notification)
            if not self.autogame: print "ILLEGAL CARD PLAYED:", notification.attemptedCard, "\n"
        elif type == WON:
            if not self.autogame: print "Player", self.players[self.activePlayer].name, "won!"
        elif type == POISONCARD:
            if not self.autogame: print "PENALTY CARD from:", notification.attemptedCard, "\n"
        elif type == SKIPPLAYER:
            if not self.autogame: 
                print "SKIPPING PLAYER", self.players[self.activePlayer].name, "using", notification.attemptedCard, "\n"
        elif type == SCREWOPPONENT:
            if not self.autogame: print "SCREWING PLAYER using:", notification.attemptedCard, "\n"
        
        
        for player in self.players:
            player.notify(notification, self)
            
    # gets a card from the deck. Resets the pile if necessary.
    # returns None if all the cards are in players hands (god help us)
    def getCardFromDeck(self):
        card = self.deck.drawCard()
        # for durability, reset the deck
        if (card == None):
            assert (len(self.deck.cards) == 0)
            if (len(self.pile) == 0):
                #sheesh. literally all the cards have been played
                return None
            else:
                # NOTE: THESE ARE UNTESTED!!! WATCH OUT FOR THIS SECTION!
                # make a new deck using the pile
                origLen = len(self.pile) # for assert
                self.deck.cards = copy.copy(self.pile) #preserves references I think
                self.pile = []
                assert( origLen == len(self.deck.cards) ) #copying trips me out
                self.deck.shuffle()
                notification = Notification(DECKRESET, None, None)
                self.notifyAll(notification)
                return self.getCardFromDeck() #recurse, try to get another card
        else:
            return card
    
            
    def enactEffects(self, attemptedCard):
        """
        Returns a boolean, "skip_enacted" -- true if skipped, false if not.
          Needed to properly tune activePlayer, because skip does some weird stuff
        """
        
        if self.poisonCardEffect.isActive(attemptedCard):
            self.poisonCardEffect.enactEffect(self, attemptedCard) #includes notification

        if self.screwOpponentEffect.isActive(attemptedCard):
            self.screwOpponentEffect.enactEffect(self, attemptedCard) #includes notification
            

        if self.skipPlayerEffect.isActive(attemptedCard):
            self.skipPlayerEffect.enactEffect(self, attemptedCard) #includes notification
            return True
        
        return False
        
    
    # describes what happens during a player turn
    #    
    # returns WON if a player won, 0 if not
    def playerTurn(self, player):
        """
        Describes and handles logic for a player attempting to place a card
        
        Returns WON if the player won, and 0 if not
        """
        attemptedCard = player.takeAction(self.lastCard) # the player tries to play a card
        lastCard = self.lastCard
        feedback = self.isLegal(attemptedCard) # the CONSTRAINTS for legality
        
        if feedback == LEGAL:
            # game state bookkeeping -- last card, and the pile
            self.pile.append(attemptedCard)
            self.lastCard = attemptedCard
            
            #tell the player their move worked
            player.getFeedback(True)
            
            # notify all players of legality
            notification = Notification(LEGAL, attemptedCard, lastCard)
            self.notifyAll(notification)
            
            #handle win conditions
            if player.won():
                return WON
            else:
                # enact effects
                skipEnacted = self.enactEffects(attemptedCard)
                
                # test that player didn't win by handing off a card
                if player.won():
                    if skipEnacted:
                        # go back a player to handle skip special case (ie, don't screw with player order)
                        self.activePlayer = (self.activePlayer + len(self.players) - 1) % len(self.players)
                    return WON
                
                return 0
        else:
            # return the card to the player, and penalize them with a new card
            player.takeCard(attemptedCard)
            penaltyCard = self.getCardFromDeck()
            if penaltyCard:
                player.takeCard(penaltyCard)
                
            #tell player of illegality
            player.getFeedback(False)
                
            # notify all players of the penalty
            notification = Notification(PENALTY, attemptedCard, lastCard)
            self.notifyAll(notification) 
    
    def playRound(self, prevWinner=0):
        """
        Plays a single round of the Mao card game. 
        Initilalized with whoever the previous winner was
        
        Returns the player number of the winner of the round.
        """
        def initNewRound(prevWinner): # resets the deck and pile after the end of each round
            self.activePlayer = prevWinner
            self.deck = Deck() #maybe not the best, but we can optimize later. ideally we fetch cards from every player
            self.pile = []
            self.roundHistory = RoundHistory() # declare a new round
            
            # initialize the first card that is placed
            initialCard = self.getCardFromDeck()
            self.pile.append(initialCard)
            self.lastCard = initialCard
            self.notifyAll(Notification(NEWROUND, None, None))
            
            for player in self.players:
                # draw 5 cards
                if player.name == "HeuristicTests":
                    player.hand = [self.getCardFromDeck() for i in range(self.startingHandSize - 1)]
                    foo = player.hand
                    foo.append(TESTCARD)
                    player.hand = foo
                else:
                    player.hand = [self.getCardFromDeck() for i in range(self.startingHandSize)]
                
                
        initNewRound(prevWinner)
        
        while True:
            # print "It is the turn of: ", self.players[self.activePlayer].name
            player = self.players[self.activePlayer]
            result = self.playerTurn(player)
            if result == WON:
                notification = Notification(WON, player, None) #hacky notification
                self.notifyAll(notification)
                break
            else:
                self.activePlayer = (1 + self.activePlayer) % len(self.players)
                
        # closing the round off
        self.gameHistory.addRound(self.roundHistory)
        self.round += 1
        
        # modify the rules every few rounds round
        if (self.round % self.changeRuleRate == 0):
            self.players[self.activePlayer].modifyRule(self.makeModification) #pass the method as an argument
        return self.activePlayer
        
    
    def playGame(self, numRounds=10):
        winner = 0
        roundPrint = 16
        for i in range(numRounds):
            if self.round % roundPrint == 0:
                t0 = time.time()
            winner = self.playRound(winner)
            
            if self.round % roundPrint == 0:
                t1 = time.time()
                print "round", self.round, t1-t0

# /////////
# 
# Commenting out for use in tests.py
# 
# \\\\\\\\\

##
# Q-Learning Agent
def playTest():
    qBot = QLearner('qBot', [SizeofHand(), HighCount(), LowCount(), Illegality()])

    ##


    pHuman = HmmAgent("Learner")
    pBot0 = RandomAgent("A1")
    pBot2 = RandomAgent("A2")
    # pBot = LearningAgent("Learner2")
    pBot1 = RandomAgent("NaiveTests")

    # g = Game([pHuman, pBot, pBotw, pBot1, pBot2], True)
    g = Game([qBot, pBot1], True)
    g.playGame(500)

    # #print stats
    for player in g.players:
        print player.name
        print player.wins
        if type(player) == LearningAgent or type(player) == RandomAgent or type(player) == HmmAgent or type(player) == HeuristicAgent:
            print np.average(player.validPercentByRound)
        if type(player) == QLearner:
            print player.weights

        
    
# tests
# pHuman = RandomAgent("J")
# # pBotw = RandomAgent("A1")
# # pBot2 = RandomAgent("A2")
# # pBot = LearningAgent("Learner2")
# pBot1 = HmmAgent("Learner")

# g = Game([pHuman, pBot, pBotw, pBot1, pBot2], True)


# #print stats
# for player in g.players:
#     print player.name
#     print player.wins
#     if type(player) == cardCounter or type(player) == RandomAgent or type(player) == HmmAgent:
#         try:
#             print g.players[1].getCombinedState()
#             print np.average(player.validPercentByRound)
#         except:
#             print 'div by zero'


# player_names = ['J', 'lerner']
# player_wins = [[],[]]
# player_valid = [[],[]]


# for game in range(500):
#     pHuman = HmmAgent("J")
# # pBotw = RandomAgent("A1")
# # pBot2 = RandomAgent("A2")
# # pBot = LearningAgent("Learner2")
#     pBot1 = cardCounter("Learner")
#     print "game:", game
#     g = Game([pHuman, pBot1], True)
#     g.playGame(20)
#     for i in range(len(g.players)):
#         player_wins[i].append(g.players[i].wins)
#         player_valid[i].append(np.average(g.players[i].validPercentByRound))
# #print stats

# for i in range(2):
#     print player_names[i]
#     print np.sum(player_wins[i])
#     print np.mean(player_valid[i])
        




#
