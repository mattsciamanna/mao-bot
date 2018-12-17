from player import *
import numpy as np
import random
import sys
import copy

# trueState = State(Rule(BASICVALUE, True), Rule(BASICSUIT, "S"), Rule(WILDVALUE, None), Rule(WILDSUIT, None))

class Agent(Player):
    def __init__(self, name):
        super(Player, self).__init__(name)
        # implied self.hand, inherited from class Player
    
    # return the card from your hand you want to play
    def chooseCard(self, lastCard, aggressive=False):
        pass #DO NOT CHANGE
    
    # notified of an event in the game (a penalty, a success, or a win)
    def notify(self, notification, game):
        pass #DO NOT CHANGE
    
    # change a rule via the makeModification function, which takes a "rule" tuple as its only argument
    def modifyRule(self, makeModification):
        return self.modifyRule_(makeModification)
        
    # # choose an opponent index and a card to give an opponent
    # # Note: don't remove the card. Just return it. The game will remove it
    # # return a (targetIndex, unwantedCard) tuple.
    def screwOpponent(self, playerList):
        # instead of pass, we have a failsafe method
        return self.screwOpponent_(playerList)

    # this is how you know if the move you just made is legal or not
    def getFeedback(self, isLegal):
        pass # DO NOT CHANGE

    
    
    ## failsafe methods
    def screwOpponent_(self, playerList):
        targets = []
        for i, player in enumerate(playerList):
            if player.name != self.name:
                targets.append(i)
        if (len(targets) == 0):
            print "this really shouldn't happen -- in screw opponent"
            return (0, random.choice(self.hand)) #error checking
        else:
            return random.choice(targets), random.choice(self.hand)

    def modifyRule_(self, makeModification):
        ruletype = random.choice([BASICVALUE, WILDVALUE, WILDSUIT, POISONDIST, POISONCARD, SCREWOPPONENT, SKIPPLAYER])
        #
        if ruletype == BASICVALUE:
            newGreater = random.choice([True, False])
            rule = Rule(BASICVALUE, newGreater)
            makeModification(rule)
            
        elif ruletype == WILDVALUE or ruletype == POISONCARD or ruletype == SCREWOPPONENT or ruletype == SKIPPLAYER:
            lst = [i + 2 for i in range(13)]
            lst.append(None)
            newValue = random.choice(lst)
            rule = Rule(ruletype, newValue)
            makeModification(rule)
        
        elif ruletype == WILDSUIT:
            newSuit = random.choice(["D", "H", "S", "C", None])
            rule = Rule(WILDSUIT, newSuit)
            makeModification(rule)

        elif ruletype == POISONDIST:
            lst = [1,2]
            lst.append(None)
            newValue = random.choice(lst)
            rule = Rule(POISONDIST, newValue)
            makeModification(rule)


class RandomAgent(Agent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
        
        self.wins = 0
        self.roundLegals = 0
        self.roundIllegals = 0
        self.validPercentByRound = []
                
    
    def notify(self, notification, game):
        def newRound():
            if self.roundIllegals + self.roundLegals == 0: return #don't divide by 0
            self.validPercentByRound.append(float(self.roundLegals) / (self.roundIllegals + self.roundLegals) )
            self.roundLegals = 0
            self.roundIllegals = 0
            
        if notification.type == WON: #corresponds to "won"
            newRound()
        

    
    def chooseCard(self, lastCard):
        return self.hand[0]
        # return random.choice([self.hand])
    
    def getFeedback(self, isLegal):
        if isLegal:
            self.roundLegals += 1
        else:
            self.roundIllegals += 1

    

class HumanAgent(Agent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
    
    def chooseCard(self, lastCard, aggressive=False):
        def showHand():
            for index, card in enumerate(self.hand):
                print "Index:", index, " -- ", card
        while True:
            # show your hand
            if not aggressive:
                print "the LAST CARD that was played was:", lastCard
            print "your hand is: \n"
            showHand()
            if aggressive:
                print "\nWhich card are you tryna stick your opponent with?"
            else:
                print "\ntype the index of the card you want to play: "
            
            instr = raw_input()
            if instr == "q":
                print "quitting"
                sys.exit()
            try:
                index = int(instr)
                return self.hand[index]
            except:
                print "\n\n**INVALID SELECTION** Try again: \n\n"
        
    def screwOpponent(self, playerList):
        print "choose the opponent you want to screw over (by typing their index)"
        for i, player in enumerate(playerList):
            print "Index:", i, " -- ", player.name, "Tot cards: ", len(player.hand)
        targetIndex = input()
        unwantedCard = self.chooseCard(None, True)
        return (targetIndex, unwantedCard)
        
    def modifyRule(self, makeModification):
        def getActiveValue():
            print "type the value (from 2 to 14) you want to activate, or 0 to inactivate"
            value = int(input())
            if (value >= 2 and value <= 14):
                return value
            elif value == 0:
                return None
            else:
                print "invalid -- try again"
        try:
            print "congrats, you get to change a rule! Please be precise"
            print "type the rule you want to change:"
            print "  1 for basicValue\n  3 for WildValue\n  4 for WildSuit \n  5 for PoisonDist"
            print "  6 for PoisonCard\n  7 for ScrewOpponent\n  8 for SkipPlayer"
            rule = int(input())
            
            if rule == BASICVALUE:
                print "type 0 to make lower cards have priority, and 1 to make higher cards have priority"
                newGreater = int(input())
                newGreater = False if newGreater == 0 else True
                
                ruleTuple = Rule(BASICVALUE, newGreater)
                makeModification(ruleTuple)
                
                return
                
            elif rule == WILDVALUE:
                # print "type in a value between 2 and 14 to make that the new wild value"
                # newValue = int(input())
                newValue = getActiveValue()
                
                ruleTuple = Rule(rule, newValue)
                makeModification(ruleTuple)
                
                return
                
            elif rule == WILDSUIT:
                while True:
                    print "type in S, D, C, or H to change your suit"
                    suit = raw_input().upper()
                    if len(suit) == 1 and suit in "SDCH":
                        
                        ruleTuple = Rule(WILDVALUE, suit)
                        makeModification(ruleTuple)
                        
                        return
                    else:
                        print "invalid character, try again"
                        
            elif rule == POISONDIST:
                print "type 1 or 2 to make either 1 or 2 distance poisonous, and 0 to inactivate"
                result = input()
                if result == 0:
                    value = None
                elif result == 1 or result == 2:
                    value = result
                else:
                    print "invalid selection"
                    return
                makeModification((Rule(POISONDIST, value)))
                return
            
            elif rule == POISONCARD or rule == SKIPPLAYER or rule == SCREWOPPONENT:
                value = getActiveValue() #returns a value between 2-14 or None
                makeModification(Rule(rule, value))
                return
        except:
            print "invalid input -- continuing unchanged"
            return
        
    def notify(self, notification, game):
        pass

class LearningAgent(Agent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
        self.wins = 0
        self.roundLegals = 0
        self.roundIllegals = 0
        self.validPercentByRound = []    
        
        self.beliefs = Counter()

        self.skipBelief = None
        self.screwBelief = None
        self.poisonBelief = None
        
        for state in stateList:
            self.beliefs[state] = 0

    # return the card from your hand you want to play
    def chooseCard(self, lastCard):
        belief_state = self.beliefs.argMax() 
        legal_cards = []
        c = Checker()
        for index, card in enumerate(self.hand):
            notification = Notification(LEGAL, card, lastCard)
            if c.isConsistent(notification, belief_state):
                legal_cards.append(card)

        if len(legal_cards) != 0:
            return random.choice(legal_cards)
        else: 
            return random.choice(self.hand)
    
    # notified of an event in the game (a penalty, a success, or a win)
    def notify(self, notification, game):
    # n = Notification(LEGAL, Card(4, "H"), Card(7, "D"))
        def newRound():
            if self.roundIllegals + self.roundLegals == 0: return #don't divide by 0
            self.validPercentByRound.append(float(self.roundLegals) / (self.roundIllegals + self.roundLegals) )
            self.roundLegals = 0
            self.roundIllegals = 0
        
        if notification.type in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            if notification.type == POISONCARD:
                self.poisonBelief = notification.attemptedCard.value
            elif notification.type == SCREWOPPONENT:
                self.screwBelief = notification.attemptedCard.value
            elif notification.type == SKIPPLAYER:
                self.skipBelief = notification.attemptedCard.value
        elif notification.type in [LEGAL, PENALTY, WON]:
            if notification.type == LEGAL:
                res = True
            elif notification.type == PENALTY:
                res = False
            elif notification.type == WON: #corresponds to "won"
                newRound()
                return

            states_agree = []
            c = Checker()
            for state in stateList:
                # print notification
                if c.isConsistent(notification, state) == res:
                    states_agree.append(state)

            for state in stateList:
                if state in states_agree:
                    self.beliefs[state] += 1.0 / len(states_agree)
                else:
                    self.beliefs[state] = 0

            self.beliefs.normalize()
        else:
            return


    # this is how you know if the move you just made is legal or not
    def getFeedback(self, isLegal):
        if isLegal:
            self.roundLegals += 1
        else:
            self.roundIllegals += 1
        
class HmmAgent(Agent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
        self.checker = Checker()
        self.beliefDistrib = Counter()
        
        self.inDangerOfSettingToNone = {}
        self.believedEffectValues = {}
        for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            self.believedEffectValues[t] = None
            self.inDangerOfSettingToNone[t] = False
            
        
        self.roundIllegals = 0
        self.roundLegals = 0
        self.validPercentByRound = []
        
        # initialize list of states
        initProb = 1 / float(len(stateList))
        for s in stateList:
            self.beliefDistrib[s] = initProb

    
    def getCombinedState(self):
        state = self.beliefDistrib.argMax()
        poison = Rule(POISONCARD, self.getBelievedEffectValue(POISONCARD))
        screw = Rule(SCREWOPPONENT, self.getBelievedEffectValue(SCREWOPPONENT))
        skip = Rule(SKIPPLAYER, self.getBelievedEffectValue(SKIPPLAYER))
        effectState = EffectState(poison, screw, skip)
        return CombinedState(state, effectState)
            
    def getBelievedEffectValue(self, effect):
        return self.believedEffectValues[effect]
    
    # return the card from your hand you want to play
    def chooseCard(self, lastCard):
        belief_state = self.beliefDistrib.argMax() 
        legal_cards = []
        for index, card in enumerate(self.hand):
            notification = Notification(LEGAL, card, lastCard)
            if self.checker.isConsistent(notification, belief_state):
                legal_cards.append(card)
        # random strategy
        # if len(legal_cards) != 0:
        #     return random.choice(legal_cards)
        # else: 
        #     return random.choice(self.hand)

        # naive strategy
        if len(legal_cards) != 0:
            return random.choice(legal_cards)
        else: 
            return random.choice(self.hand)
            
    def getFeedback(self, isLegal):
        if isLegal:
            self.roundLegals += 1
        else:
            self.roundIllegals += 1
    
    # notified of an event in the game (a penalty, a success, or a win)
    def notify(self, notification, game):
        if notification.type == WON:
            try:
                self.validPercentByRound.append(float(self.roundLegals) / (self.roundIllegals + self.roundLegals) )
            except:
                print "div by 0"
            self.roundLegals = 0
            self.roundIllegals = 0
            
            #reset 
            for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
                self.inDangerOfSettingToNone[t] = False

            ## super wacky -- we need know if we won the game, so we put "player" as "attemptedCard"
            # immutable names is mostly great. Except when it isn't
            if notification.attemptedCard == self: 
                return
                
                
            # simulate dynamics -- occurs only on new round change
            #naive dynamics: reset the list
            # uniformProb = 1.0 / float(len(stateList))
            # for state in stateList:
            #     self.beliefDistrib[state] = uniformProb # naive
            # return
        
            #complex dynamics:
            # for each state with non-zero probability
              # find successor states, and add them as possiblities. But weight towards current state
              # then, renormalize the entire thing
              
              
              # State = namedtuple('State', ['basicValueRule', 'wildValueRule', 'wildSuitRule', 'poisonDist'])
            def isPossibleChild(stateA, stateB):
                total = 0
                for ruleA, ruleB in zip(stateA, stateB):
                    if ruleA.setting == ruleB.setting:
                        total += 1
                if total >= 3:
                    return True
                else:
                    return False
                    
            # get a list of states with non-zero probabilities
            possiblePriorStates = []
            for state in stateList:
                if self.beliefDistrib[state] != 0:
                    possiblePriorStates.append(state)

            newBeliefs = Counter()
            
            
            pTransition = 1.0 / 25.0 * 4.0 / 7.0 # each state has 25 successors (2 + 15 + 3 + 5), and there is a 4/7 chance an effect was not chosen
            for tMinusOne in possiblePriorStates:
                newBeliefs[tMinusOne] += 3.0 / 7.0 * self.beliefDistrib[tMinusOne]
                for successorState in stateList:
                    if isPossibleChild(successorState, tMinusOne):
                        newBeliefs[successorState] += pTransition
            
            newBeliefs.normalize()
            self.beliefDistrib = newBeliefs
            return   
            
            
        elif notification.type in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            type = notification.type
            # print "setting value of ", type
            self.believedEffectValues[type] = notification.attemptedCard.value
            self.inDangerOfSettingToNone[type] = False     
            
        elif notification.type in [LEGAL, PENALTY]:
            if notification.type == LEGAL:
                res = True
                
                for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
                    # if we haven't received a notification when we were expecting it, set a notification to None
                    if self.inDangerOfSettingToNone[t]:
                        # print "dismayed", t
                        self.believedEffectValues[t] = None
                    
                    # set up the expectation of an effect notification 
                    v = self.believedEffectValues[t]
                    if v == notification.attemptedCard.value:
                        # print "we expect a notification", t
                        self.inDangerOfSettingToNone[t] = True
                        
            elif notification.type == PENALTY:
                res = False
            # update probabilities based on state dynamics
            for state in stateList: #same thing as belief distribution
                if self.beliefDistrib[state] == 0:
                    continue
                else:
                    if self.checker.isConsistent(notification, state) == res:
                        continue
                    else:
                        self.beliefDistrib[state] = 0
            self.beliefDistrib.normalize()
            return

    def modifyRule(self, makeModification):

        ruletype = random.choice([BASICVALUE, WILDVALUE, WILDSUIT, POISONDIST, POISONCARD, SCREWOPPONENT, SKIPPLAYER])
        #
        if ruletype == BASICVALUE:
            newGreater = random.choice([True, False])
            rule = Rule(BASICVALUE, newGreater)
            makeModification(rule)
            
        elif ruletype == WILDVALUE or ruletype == POISONCARD or ruletype == SCREWOPPONENT or ruletype == SKIPPLAYER:
            lst = [i + 2 for i in range(13)]
            lst.append(None)
            newValue = random.choice(lst)
            rule = Rule(ruletype, newValue)
            makeModification(rule)
        
        elif ruletype == WILDSUIT:
            newSuit = random.choice(["D", "H", "S", "C", None])
            rule = Rule(WILDSUIT, newSuit)
            makeModification(rule)

        elif ruletype == POISONDIST:
            lst = [1,2]
            lst.append(None)
            newValue = random.choice(lst)
            rule = Rule(POISONDIST, newValue)
            makeModification(rule)

        newBeliefs = Counter()
        
        if rule.rule == BASICVALUE: 
            for state in self.beliefDistrib:
                state_val = self.beliefDistrib[state]
                new_state = State(rule, state.wildValueRule, state.wildSuitRule, state.poisonDistRule)
                newBeliefs[new_state] += state_val  
        
        elif rule.rule == WILDSUIT:
            for state in self.beliefDistrib:
                state_val = self.beliefDistrib[state]
                new_state = State(state.basicValueRule, state.wildValueRule, rule, state.poisonDistRule)
                newBeliefs[new_state] += state_val 
        
        elif rule.rule == POISONDIST:
            for state in self.beliefDistrib:
                state_val = self.beliefDistrib[state]
                new_state = State(state.basicValueRule, state.wildValueRule, state.wildSuitRule, rule)
                newBeliefs[new_state] += state_val 
        
        elif rule.rule == WILDVALUE:
            for state in self.beliefDistrib:
                state_val = self.beliefDistrib[state]
                new_state = State(state.basicValueRule, rule, state.wildSuitRule, state.poisonDistRule)
                newBeliefs[new_state] += state_val 

        elif rule.rule in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            ### TODO #### Account for effect card distributions
            # print rule.rule
            self.believedEffectValues[rule.rule] = rule.setting
            return

        else:
            ### TODO #### Account for effect card distributions
            return

        # NONETYPE -- possible error here, need to return
        newBeliefs.normalize()
        self.beliefDistrib = newBeliefs

class HeuristicAgent(HmmAgent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
        self.checker = Checker()
        self.beliefDistrib = Counter()
        
        self.inDangerOfSettingToNone = {}
        self.believedEffectValues = {}
        for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            self.believedEffectValues[t] = None
            self.inDangerOfSettingToNone[t] = False
            
        
        self.roundIllegals = 0
        self.roundLegals = 0
        self.validPercentByRound = []
        
        # initialize list of states
        initProb = 1 / float(len(stateList))
        for s in stateList:
            self.beliefDistrib[s] = initProb
    # a naive heuristic to judge the best card to play
    def naiveHeuristic(self, legalCards, effects):
        # basic progression of card strength from best to worst:
        # ScrewOppponent Cards -> Skip Player Cards -> Lowest Value Legal Cards
        if len(effects) == 3:
            poisonValue = effects.poisonCardRule.setting
            skipCard = effects.skipPlayerRule.setting
            screwCard = effects.screwOpponentRule.setting
        else: 
            poisonValue = 999
            skipCard = 999
            screwCard = 999
            # if effects is malformed we can't easily pick a good card

        for card in legalCards:
            if card.value == screwCard:
                return card
        
        for card in legalCards:
            if card.value == skipCard:
                return card

        # Checks for smallest valued legal card
        smallestCard = 15
        smallestIndex = 0
        for indx, card in enumerate(legalCards):
            if card.value < smallestCard:
                smallestCard = card.value
                smallestIndex = indx

        return legalCards[smallestIndex]

  # return the card from your hand you want to play
    def chooseCard(self, lastCard):
        combinedstate = self.getCombinedState()
        belief_state = self.beliefDistrib.argMax() 
        legal_cards = []
        for index, card in enumerate(self.hand):
            notification = Notification(LEGAL, card, lastCard)
            if self.checker.isConsistent(notification, combinedstate.state):
                legal_cards.append(card)
        # raturn random.choice(self.hand)

        # naive strategy
        if len(legal_cards) != 0:
            return self.naiveHeuristic(legal_cards, combinedstate.effectState)
        else: 
            return random.choice(self.hand)

# Card Counting Agent that plays expectimax type solution
class cardCounter(HmmAgent):
    def __init__(self, name):
        super(Agent, self).__init__(name)
        
        self.checker = Checker()
        self.beliefDistrib = Counter()
        
        self.inDangerOfSettingToNone = {}
        self.believedEffectValues = {}
        for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            self.believedEffectValues[t] = None
            self.inDangerOfSettingToNone[t] = False
            
        
        self.roundIllegals = 0
        self.roundLegals = 0
        self.validPercentByRound = []
        
        # initialize list of states
        initProb = 1 / float(len(stateList))
        for s in stateList:
            self.beliefDistrib[s] = initProb
        
        self.wonLast = 1
        self.justShuffled = 0
        self.discard = []
        self.cardsAtLarge = []
        self.opHandSize = len(self.hand)
        self.cardBelief = {}
        
        self.total_cards = []
        for s in ["D", "H", "S", "C"]:
            for v in range(2,15):
                self.total_cards.append(Card(v,s))
                self.cardBelief[Card(v,s)] = 0

        # for card in self.cardsAtLarge: 
        #     self.cardBelief[card] = self.opHandSize/len(self.cardsAtLarge)
        # for card in self.hand:
        #     self.cardBelief[card] = 0

    # TakeCard Method from Player Class to update when cards are in your hand
    # def takeCard(self, card):
    #     if card != None:
    #         self.hand.append(card)
    #         # If taking a card, it is impossible for opponent to have same card
    #         self.cardBelief[card] = 0
    #     else:
    #         print "takeCard: no card drawn. This seems like trouble -- investigate"

    def notify(self, notification, game):
        if notification.type == WON:
            try:
                self.validPercentByRound.append(float(self.roundLegals) / (self.roundIllegals + self.roundLegals) )
            except:
                print "div by 0"
            self.roundLegals = 0
            self.roundIllegals = 0
            
            #reset 
            for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
                self.inDangerOfSettingToNone[t] = False

            ## super wacky -- we need know if we won the game, so we put "player" as "attemptedCard"
            # immutable names is mostly great. Except when it isn't
            if notification.attemptedCard == self: 
                return
                
                
            # simulate dynamics -- occurs only on new round change
            #naive dynamics: reset the list
            # uniformProb = 1.0 / float(len(stateList))
            # for state in stateList:
            #     self.beliefDistrib[state] = uniformProb # naive
            # return
        
            #complex dynamics:
            # for each state with non-zero probability
              # find successor states, and add them as possiblities. But weight towards current state
              # then, renormalize the entire thing
              
              
              # State = namedtuple('State', ['basicValueRule', 'wildValueRule', 'wildSuitRule', 'poisonDist'])
            def isPossibleChild(stateA, stateB):
                total = 0
                for ruleA, ruleB in zip(stateA, stateB):
                    if ruleA.setting == ruleB.setting:
                        total += 1
                if total >= 3:
                    return True
                else:
                    return False
                    
            # get a list of states with non-zero probabilities
            possiblePriorStates = []
            for state in stateList:
                if self.beliefDistrib[state] != 0:
                    possiblePriorStates.append(state)

            newBeliefs = Counter()
            
            
            pTransition = 1.0 / 25.0 * 4.0 / 7.0 # each state has 25 successors (2 + 15 + 3 + 5), and there is a 4/7 chance an effect was not chosen
            for tMinusOne in possiblePriorStates:
                newBeliefs[tMinusOne] += 3.0 / 7.0 * self.beliefDistrib[tMinusOne]
                for successorState in stateList:
                    if isPossibleChild(successorState, tMinusOne):
                        newBeliefs[successorState] += pTransition
            
            newBeliefs.normalize()
            self.beliefDistrib = newBeliefs
            
            
            
        elif notification.type in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
            type = notification.type
            # print "setting value of ", type
            self.believedEffectValues[type] = notification.attemptedCard.value
            self.inDangerOfSettingToNone[type] = False     
            
        elif notification.type in [LEGAL, PENALTY]:
            if notification.type == LEGAL:
                res = True
                
                for t in [POISONCARD, SCREWOPPONENT, SKIPPLAYER]:
                    # if we haven't received a notification when we were expecting it, set a notification to None
                    if self.inDangerOfSettingToNone[t]:
                        # print "dismayed", t
                        self.believedEffectValues[t] = None
                    
                    # set up the expectation of an effect notification 
                    v = self.believedEffectValues[t]
                    if v == notification.attemptedCard.value:
                        # print "we expect a notification", t
                        self.inDangerOfSettingToNone[t] = True
                        
            elif notification.type == PENALTY:
                res = False
            # update probabilities based on state dynamics
            for state in stateList: #same thing as belief distribution
                if self.beliefDistrib[state] == 0:
                    continue
                else:
                    if self.checker.isConsistent(notification, state) == res:
                        continue
                    else:
                        self.beliefDistrib[state] = 0
            self.beliefDistrib.normalize()
            

        if self.wonLast == 1 and notification.type != NEWROUND:
            self.discard = [notification.lastCard]
            self.cardsAtLarge = []
            self.opHandSize = 0
            for player in game.players:
                if player != self:
                    self.opHandSize += len(player.hand) 
            self.cardBelief = {}
            self.cardBelief[notification.lastCard] = 0
            
            for s in ["D", "H", "S", "C"]:
                for v in range(2,15):
                    if Card(v,s) not in self.hand:
                        self.cardsAtLarge.append(Card(v,s))

            self.cardsAtLarge.remove(notification.lastCard)

            for card in self.cardsAtLarge: 
                self.cardBelief[card] = self.opHandSize/len(self.cardsAtLarge)
            
            for card in self.hand:
                self.cardBelief[card] = 0
            self.wonLast = 0

        
        ####### WIN LOGIC ######

        if notification.type == WON:
            self.wonLast = 1
            return


        ###### DECK RESET LOGIC #####
        if notification.type == DECKRESET:
            self.cardsAtLarge = copy.copy(self.discard)
            self.discard = []

        if game.players[game.activePlayer] != self:
        # If opponent just played
            cardPlayed = notification.attemptedCard

            # if legal move played, card no longer in hand
            if notification.type == LEGAL:
                self.discard.append(cardPlayed)
                if cardPlayed in self.cardsAtLarge:
                    self.cardsAtLarge.remove(cardPlayed)
                self.cardBelief[cardPlayed] = 0

            # if penalty, card returned to op hand 
            elif notification.type == PENALTY:
                self.cardBelief[cardPlayed] = 1
                if cardPlayed in self.cardsAtLarge:
                    self.cardsAtLarge.remove(cardPlayed)
 
        #Case if you just played
        else:
            

            cardPlayed = notification.attemptedCard
            if notification.type == LEGAL:
                self.discard.append(cardPlayed)

        for card in self.hand:
            if card in self.cardsAtLarge:
                self.cardsAtLarge.remove(card)
            self.cardBelief[card] = 0


        # Size of opponent hands combined
        self.opHandSize = 0
        for player in game.players:
            if player != self:
                self.opHandSize += len(player.hand)

        spotsAtLarge = self.opHandSize
        for card in self.cardBelief:
            if self.cardBelief[card] > 0.99:
                spotsAtLarge -= 1
                if card in self.cardsAtLarge:
                    self.cardsAtLarge.remove(card)
                
        
        for card in self.cardsAtLarge:
            self.cardBelief[card] = spotsAtLarge / float(len(self.cardsAtLarge))

        

    def screwOpponent(self, playerList):
        targets = []
        targetCards = []
        for i, player in enumerate(playerList):
            if player.name != self.name:
                targets.append(i)
                targetCards = len(player.hand)
        
        if (len(targets) == 0):
            print "this really shouldn't happen -- in screw opponent"
            return (0, random.choice(self.hand)) #error checking
        else:
            giveCard = random.choice(self.hand)
            giveTarget = targets[np.argmax(targetCards)]
            self.cardBelief[giveCard] = 1
            return giveTarget, giveCard

    def chooseCard(self, lastCard):
        belief_state = self.beliefDistrib.argMax() 
        legal_cards = []
        for index, card in enumerate(self.hand):
            notification = Notification(LEGAL, card, lastCard)
            if self.checker.isConsistent(notification, belief_state):
                legal_cards.append(card)

        if len(legal_cards) != 0:
            counterPlays = []
            for card in legal_cards:
                counterPlay = 0
                for counterCard in self.total_cards:
                    if self.cardBelief[counterCard] > 0:
                        notification2 = Notification(LEGAL, counterCard, card)
                        if self.checker.isConsistent(notification, belief_state):
                            constant = 0
                            if self.believedEffectValues[SKIPPLAYER] == counterCard.value:
                                constant += 2
                            if self.believedEffectValues[POISONCARD] == counterCard.value:
                                constant -= 2
                            if self.believedEffectValues[SCREWOPPONENT] == counterCard.value:
                                constant += 2
                            counterPlay += 1*self.cardBelief[counterCard] *constant
                counterPlays.append(counterPlay)
            return legal_cards[np.argmin(counterPlays)]
        else: 
            counterPlays = []
            for card in self.hand:
                counterPlay = 0
                for counterCard in self.total_cards:
                    if self.cardBelief[counterCard] > 0:
                        notification2 = Notification(LEGAL, counterCard, card)
                        if self.checker.isConsistent(notification, belief_state):
                            constant = 0
                            if self.believedEffectValues[SKIPPLAYER] == counterCard.value:
                                constant += 2
                            if self.believedEffectValues[POISONCARD] == counterCard.value:
                                constant -= 2
                            if self.believedEffectValues[SCREWOPPONENT] == counterCard.value:
                                constant += 2
                            counterPlay += 1*self.cardBelief[counterCard]
                counterPlays.append(counterPlay)
            return self.hand[np.argmin(counterPlays)]
