from agents import *
from features import *

def calculateReward(fstate, action, combo, nextFstate):
    if len(nextFstate.hand) == 0:
        # you won!
        return 15
    elif len(nextFstate.opponentHand) == 0:
        # you lost!
        return -15
            
    # if you lose cards, + reward. if you gain cards, - reward
    return len(fstate.hand) - len(nextFstate.hand) - len(fstate.opponentHand) + len(nextFstate.opponentHand)

#NOTE: Inspired by PSet 3 QLearning framework -- THANK YOU BERKELEY!
class QLearner(Agent):
    """
    In general:
    state : Fstate
    action : card
    """
    def __init__(self, name, features, alpha=0.01, epsilon=0.2, gamma=0.8):
        super(Agent, self).__init__(name)
        self.weights = Counter()
        self.features = features
        for feature in features:
            self.weights[feature] = -1.0
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        
        self.gameRef = None
        self.lastAction = None
        self.lastFstate = None
        self.combostate = None
        self.opponent = None
    
    def getQValue(self, fstate, action):
        """
        Q(s, a) = w_1 f_1 + w_2 f_2 + ... + w_n f_n
        """
        qValue = 0.0
        featuresToActivity = featureDict(self.features, fstate, action, self.combostate)
        for feature, featureActivity in featuresToActivity.iteritems():
            qValue = qValue + self.weights[feature] * featureActivity
        return qValue
    
    def update(self, fstate, action, nextFstate, reward):
        """
        updates the weights, in response to an episode
        
        for each self.weights[feature]:
            w_i = w_i + alpha * diff * featureActivity
                diff = reward + gamma * V(s') - Q(s, a)
                    NOTE: V(s') = max_a' Q(s', a')
        """
        diff = reward + self.gamma * self.getStateValue(nextFstate) - self.getQValue(fstate, action)

        featuresToActivity = featureDict(self.features, fstate, action, self.combostate)
        
        for feature, featureActivity in featuresToActivity.iteritems():
            self.weights[feature] = self.weights[feature] + self.alpha * diff * featureActivity

    def getStateValue(self, fstate):
        """
        Given a state, tells you the value of that state -- primarily used in diff
        """
        return self.computeQVals(fstate, True)

    def getBestAction(self, fstate):
        """
        Given a state, tells you the best action you can take
        """
        return self.computeQVals(fstate, False)

    def computeQVals(self, state, doReturnState): #else, return the best action
        """
        takes a state, and a doReturnState boolean
            if doReturnState == True, then returns the value of that state
            else, returns the best action you can take, given a state
            
        value of state: V(S) = max_a Q(S, A)
        best action: state with best Q value.
        """
        valuesForActions = Counter()
        for action in self.getLegalActions(state):
            valuesForActions[action] = self.getQValue(state,action)
        if (doReturnState):
            return valuesForActions[valuesForActions.argMax()]
        else:
            return valuesForActions.argMax()
        
    def getLegalActions(self, state):
        return state.hand
        # return a list of legal actions! -- ie, cards that can be played
    
    def getAction(self, state):
        # Pick Action
        legalActions = self.getLegalActions(state)
        randomAction = random.choice(legalActions)
        bestAction = self.getBestAction(state)

        if random.random() < self.epsilon:
            return randomAction
        else:
            return bestAction

    def chooseCard(self, lastCard, aggressive=False):
        #place where we set a state
        if not aggressive:
            currentFstate = Fstate(self.hand[:], lastCard, self.opponent.hand[:])
            # choose a card
            cardToPlay = self.getAction(currentFstate)
            
            #this is NOT our first move
            if self.lastFstate != None:
                # calcuate the reward and update
                reward = calculateReward(self.lastFstate, self.lastAction, self.combostate, currentFstate)
                self.update(self.lastFstate, self.lastAction, currentFstate, reward)            
            
            self.lastFstate = currentFstate
            self.lastAction = cardToPlay
            return cardToPlay
        else:
            return random.choice(self.hand)


    def notify(self, notification, game):
        # if I just played a card
        if notification.type == NEWROUND:
            
            self.gameRef = game
            self.combostate = game.deliverCombostate()
            self.lastAction = None
            self.lastFstate = None
            
            # set the opponent
            for player in game.players:
                if player != self:
                    self.opponent = player
                    break
            
        if notification.type == WON:
            finalFstate = Fstate(self.hand[:], game.lastCard, self.opponent.hand[:])
            reward = calculateReward(self.lastFstate, self.lastAction, self.combostate, finalFstate)
            self.update(self.lastFstate, self.lastAction, finalFstate, reward) 

            self.gameRef = None # to prevent circular reference counting
            


#
class QPlayer(HmmAgent):
    def __init__(self, name, features, weights, opponent):
        super(Agent, self).__init__(name)
        
        #Q-Setup
        self.opponent = opponent
        self.features = features
        self.weights = weights
        assert(len(features) == len(weights))
        
        #HMM setup
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
            
  # return the card from your hand you want to play
    def chooseCard(self, lastCard, aggressive=False):
        if not aggressive:
            currentFstate = Fstate(self.hand[:], lastCard, self.opponent.hand[:])
            if random.random() > 0.975: #add stochastism to avoid certain rare corner cases
                return self.getBestAction(currentFstate)
            else:
                return random.choice(self.hand)
        else:
            return random.choice(self.hand)
            
    def getLegalActions(self, state):
        return state.hand
            
    def getQValue(self, fstate, action):
        qVal = 0.0
        featuresToActivity = featureDict(self.features, fstate, action, self.getCombinedState())
        for feature, featureActivity in featuresToActivity.iteritems():
            qVal = qVal + self.weights[feature] * featureActivity
        return qVal
    
    def getStateValue(self, fstate):
        return self.computeQVals(fstate, True)

    def getBestAction(self, fstate):
        return self.computeQVals(fstate, False)

    def computeQVals(self, state, doReturnState): #else, return the best action
        valuesForActions = Counter()
        for action in self.getLegalActions(state):
            valuesForActions[action] = self.getQValue(state,action)
        if (doReturnState):
            return valuesForActions[valuesForActions.argMax()]
        else:
            return valuesForActions.argMax()
