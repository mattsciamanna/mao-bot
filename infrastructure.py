import random
from collections import namedtuple

import constraints

Card = namedtuple('Card', ['value', 'suit'])

# rule settings
Rule = namedtuple('Rule', ['rule', 'setting'])
BASICVALUE = 1
BASICSUIT = 2 # I don't think there's much we can do with this as of now
WILDVALUE = 3
WILDSUIT = 4
POISONDIST = 5

POISONCARD = 6
SCREWOPPONENT = 7
SKIPPLAYER = 8


# Notification Code for reseting deck from pile
DECKRESET = 10

State = namedtuple('State', ['basicValueRule', 'wildValueRule', 'wildSuitRule', 'poisonDistRule'])

EffectState = namedtuple('EffectState', ['poisonCardRule', 'screwOpponentRule', 'skipPlayerRule'])

CombinedState = namedtuple('CombinedState', ['state', 'effectState'])

Fstate = namedtuple('Fstate', ['hand', 'lastCard', 'opponentHand'])

#initialize a list of states
stateList = []
suits = ['H', 'D', 'C', 'S', None]
for basicValue in [True, False]:
    for i in [2,3,4,5,6,7,8,9,10,11,12,13,14, None]:
        for suit2 in suits:
            for poison in [None, 1, 2]:
                stateList.append(State(Rule(BASICVALUE, basicValue), Rule(WILDVALUE, i), Rule(WILDSUIT, suit2), Rule(POISONDIST, poison)))


#notification types
Notification = namedtuple('Notification', ['type', 'attemptedCard', 'lastCard'])

LEGAL = 1
PENALTY = 2
WON = 3
NEWROUND = 100
# NOTE: These are also used as effect-signalers in notifications
# POISONCARD = 6
# SCREWOPPONENT = 7
# SKIPPLAYER = 8


class Deck(object):
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()

    def build(self):
        """
        Initializes the deck with a fresh set of cards
        """
        self.cards = []
        for s in ["D", "H", "S", "C"]:
            for v in range(2,15):
                self.cards.append(Card(value=v,suit=s))

    def shuffle(self):
        random.shuffle(self.cards)

    # returns a card if the deck is not empty, None if it is empty
    def drawCard(self):
        if len(self.cards) == 0:
            return None
        else:
            return self.cards.pop() #removes the last card ("the top")
    
    
# keeps track of a bunch of round histories
class GameHistory(object):
    def __init__(self):
        self.rounds = []

    def addRound(self, roundHistory):
        self.rounds.append(roundHistory)

# keeps track of the history of a round. further indices are more recent games
class RoundHistory(object):
    def __init__(self):
        self.moves = []

    def recordMove(self, notification):
        self.moves.append(copy.deepcopy(notification)) # watch out. I have a feeling this will slow down things considerably




#copy and paste
class Checker(object):
    def __init__(self):
        self.basicValueConstraint = constraints.BasicValueConstraint(True)
        self.basicSuitConstraint = constraints.BasicSuitConstraint()
        self.wildValueConstraint = constraints.WildValueConstraint()
        self.wildSuitEffect = constraints.WildSuitEffect()
        self.poisonDistanceConstraint = constraints.PoisonDistanceConstraint()
        self.lastCard = None

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

    # returns True if the notification last card and attempted card will be legal, given the ruleState
    def isConsistent(self, notification, ruleState):
        # change the state
        self.lastCard = notification.lastCard
        for rule in ruleState:
            self.makeModification(rule)
        # see if is legal
        return self.isLegal(notification.attemptedCard)
    

# checker tests
# n = Notification(LEGAL, Card(4, "H"), Card(7, "D"))
# s = State(Rule(BASICVALUE, True), Rule(BASICSUIT, None), Rule(WILDVALUE, 5), Rule(WILDSUIT, "H") )
# 
# c = Checker()
# 
# print c.isConsistent(n, s)
#

class Counter(dict):
    """
    A counter keeps track of counts for a set of keys.

    The counter class is an extension of the standard python
    dictionary type.  It is specialized to have number values
    (integers or floats), and includes a handful of additional
    functions to ease the task of counting data.  In particular,
    all keys are defaulted to have value 0.  Using a dictionary:

    a = {}
    print a['test']

    would give an error, while the Counter class analogue:

    >>> a = Counter()
    >>> print a['test']
    0

    returns the default 0 value. Note that to reference a key
    that you know is contained in the counter,
    you can still use the dictionary syntax:

    >>> a = Counter()
    >>> a['test'] = 2
    >>> print a['test']
    2

    This is very useful for counting things without initializing their counts,
    see for example:

    >>> a['blah'] += 1
    >>> print a['blah']
    1

    The counter also includes additional functionality useful in implementing
    the classifiers for this assignment.  Two counters can be added,
    subtracted or multiplied together.  See below for details.  They can
    also be normalized and their total count and arg max can be extracted.
    """
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)

    def incrementAll(self, keys, count):
        """
        Increments all elements of keys by the same count.

        >>> a = Counter()
        >>> a.incrementAll(['one','two', 'three'], 1)
        >>> a['one']
        1
        >>> a['two']
        1
        """
        for key in keys:
            self[key] += count

    def argMax(self):
        """
        Returns the key with the highest value.
        """
        if len(self.keys()) == 0: return None
        all = self.items()
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def sortedKeys(self):
        """
        Returns a list of keys sorted by their values.  Keys
        with the highest values will appear first.

        >>> a = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> a['third'] = 1
        >>> a.sortedKeys()
        ['second', 'third', 'first']
        """
        sortedItems = self.items()
        compare = lambda x, y:  sign(y[1] - x[1])
        sortedItems.sort(cmp=compare)
        return [x[0] for x in sortedItems]

    def totalCount(self):
        """
        Returns the sum of counts for all keys.
        """
        return sum(self.values())

    def normalize(self):
        """
        Edits the counter such that the total count of all
        keys sums to 1.  The ratio of counts for all keys
        will remain the same. Note that normalizing an empty
        Counter will result in an error.
        """
        total = float(self.totalCount())
        if total == 0: return
        for key in self.keys():
            self[key] = self[key] / total

    def divideAll(self, divisor):
        """
        Divides all counts by divisor
        """
        divisor = float(divisor)
        for key in self:
            self[key] /= divisor

    def copy(self):
        """
        Returns a copy of the counter
        """
        return Counter(dict.copy(self))

    def __mul__(self, y ):
        """
        Multiplying two counters gives the dot product of their vectors where
        each unique label is a vector element.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['second'] = 5
        >>> a['third'] = 1.5
        >>> a['fourth'] = 2.5
        >>> a * b
        14
        """
        sum = 0
        x = self
        if len(x) > len(y):
            x,y = y,x
        for key in x:
            if key not in y:
                continue
            sum += x[key] * y[key]
        return sum

    def __radd__(self, y):
        """
        Adding another counter to a counter increments the current counter
        by the values stored in the second counter.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> a += b
        >>> a['first']
        1
        """
        for key, value in y.items():
            self[key] += value

    def __add__( self, y ):
        """
        Adding two counters gives a counter with the union of all keys and
        counts of the second added to counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a + b)['first']
        1
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] + y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = y[key]
        return addend

    def __sub__( self, y ):
        """
        Subtracting a counter from another gives a counter with the union of all keys and
        counts of the second subtracted from counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a - b)['first']
        -5
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] - y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = -1 * y[key]
        return addend
