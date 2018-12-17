from infrastructure import *

    
    
# CRUCIAL METHOD
def featureDict(featureList, fstate, action, combo):
    """
    fstate : Fstate -- the feature state
    action : Card -- the card you are trying to play
    combo  : Combostate -- the combined state of rules and effects
    
    given a list of features, returns a dictionary mapping:
        feature -> featureActivity (given fstate, action, and combo)
    """
    featureDict = {}
    for feature in featureList:
        featureDict[feature] = feature.f(fstate,action,combo)
    return featureDict
    

class Feature(object):
    
    def f(fstate, action, combostate):
        pass

class SizeofHand(Feature):
    
    def f(self, fstate, action, combostate):
        try:
            return len(fstate.hand) # remove self -- just depends on arguments
        except:
            print "just dodged a bullet!"
# if basicValueRule.setting == True: 2, 3, 4, 5. Else, 11, 12 ,13 ,14
class HighCount(Feature):

    def f(self, fstate, action, combostate):
        #if greater is more powerful
        highCards = 0
        if (combostate.state.basicValueRule.setting == True):            
            for card in fstate.hand:
                if card.value >= 11:
                    highCards += 1 
        else:
            for card in fstate.hand:
                if card.value <= 5:
                    highCards += 1 
        return highCards    

class LowCount(Feature):
    
    def f(self, fstate, action, combostate):
        #if greater is more powerful
        lowCards = 0
        if (combostate.state.basicValueRule.setting == True):            
            for card in fstate.hand:
                if card.value <= 5:
                    lowCards += 1 
        else:
            for card in fstate.hand:
                if card.value >= 11:
                    lowCards += 1 
        return lowCards

# dosen't depend on state
class MedCount(Feature):

    def f(self, fstate, action, combostate):
        medCards = 0
        for card in fstate.hand:
            if card.value >= 6:
                if card.value <= 10:
                    medCards += 1 
        return medCards

# checker if it works with rule state
# check against last card and make sure it works 
class Illegality(Feature):
    def __init__ (self):
        self.checker = Checker()

    def f(self, fstate, action, combostate):
        actionCard = action
        lastCard = fstate.lastCard
        constraintState = combostate.state
        isLegalGivenState = self.checker.isConsistent(Notification(LEGAL, actionCard, lastCard), constraintState)
        if not isLegalGivenState:
            return 1
        else:
            return 0


## THESE NEED TO BE REDONE! -- remove init (unless it's absolutely necessary),
#    and migrate stuff to f


class WildValue(Feature):
    def f(self, fstate, action, combostate):
        wildvals = 0
        for card in fstate.hand:
            if card.value == combostate.state.wildValueRule.setting:
                wildvals += 1 
        return wildvals

class MajorityPercent(Feature):
    def f(self, fstate, action, combostate):
        c = 0
        s = 0
        h = 0
        d = 0
        maxsuit = 0 
        for card in fstate.hand:
            if card.suit == "C":
                c += 1 
            if card.suit == "D":
                d += 1 
            if card.suit == "S":
                s += 1 
            if card.suit == "H":
                h += 1 
        maxsuit = max([c,s,h,d])
        return (maxsuit/float(len(fstate.hand)))

class SkipCount(Feature):

    def f(self, fstate, action, combostate):
        skipCards = 0
        for card in fstate.hand:
            if card.value == combostate.effectState.skipPlayerRule.setting:
                skipCards += 1 
        return skipCards

class ScrewCount(Feature):

    def f(self, fstate, action, combostate):
        screwCards = 0
        for card in fstate.hand:
            if card.value == combostate.effectState.screwOpponentRule.setting:
                screwCards += 1 
        return screwCards

class PoisonCount(Feature):
    
    def f(self, fstate, action, combostate):
        poisonCards = 0
        for card in fstate.hand:
            if card.value == combostate.effectState.poisonCardRule.setting:
                poisonCards += 1 
        return poisonCards

class WildSuit(Feature):
    
    def f(self, fstate, action, combostate):
        trumpSuit = 0
        if combostate.state.wildSuitRule.setting != None:
            for card in fstate.hand:
                if card.suit == combostate.state.wildSuitRule.setting:
                    trumpSuit += 1 
        return trumpSuit


class AceCount(Feature):
    
    def f(self, fstate, action, combostate):
        aces = 0
        for card in fstate.hand:
            if card.value == 14:
                aces += 1 
        return aces

class TwoCount(Feature):
    def f(self, fstate, action, combostate):
        twos = 0
        for card in fstate.hand:
            if card.value == 2:
                twos += 1 
        return twos


class OpponentCards(Feature):
    
    def f(self, fstate, action, combostate):
        #num cards in opponent's hand
        return len(fstate.opponentHand)

# \\\\\\\\\\\\\\\\
# 
# Testing stuff
# 
# ////////////////

# Fake rules gethhelelp
# bvRule = Rule('basicValueRule', 2)
# wvRule = Rule('wildValueRule', 8)
# wsRule = Rule('wildSuitRule', 'C')
# pdRule = Rule('poisonDistRule', 9)
# 
# # fake effects (not inited)
# pcRule = Rule('poisonCardRule', 14)
# soRule = Rule('screwOpponentRule', 99)
# spRule = Rule('skipPlayerRule', 99)
# 
# # fake state
# ruleState = State(bvRule, wvRule, wsRule, pdRule)
# effectState = EffectState(pcRule, soRule,spRule)
# 
# # combined
# combostate = CombinedState(ruleState,effectState)
# 
# # Cards
# card1 = Card(2, "C")
# card2 = Card(13, "H")
# card4 = Card(8, "H")
# card3 = Card(14, "C")
# 
# testFstate = Fstate([card1, card3], card2, [card4])
# testAction = card2
# 
# # print WildSuit(testFstate, testAction, combostate).f()
# 
# print featureDict([MajorityPercent(), PoisonCount()], testFstate, testAction, combostate)
