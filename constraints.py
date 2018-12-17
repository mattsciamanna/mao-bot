#abstract class for a constraint
class Constraint(object):
    # returns a bool. True if the constraint should be activated
    # ex) maybe every time two cards of the same type are placed, the next player is skipped
    def isActive(self, attemptedCard):
        pass
    
    def isLegal(self, attemptedCard, lastCard):
        pass
        


# initial state:
#  State(Rule(BASICVALUE, True), Rule(BASICSUIT, None), Rule(WILDVALUE, None), Rule(WILDSUIT, None))

class BasicValueConstraint(Constraint):
    """
    Tells you if higher or lower cards can be played, init with bool greater
      in general, if card is equal or (greater/less), then it is legal
    """
    def __init__(self, greater): #greater is a boolean to say if greater values are allowed, or lower values are
        self.greater = greater

    # never conditionally active
    def isActive(self, attemptedCard):
        return True
    
    def isLegal(self, attemptedCard, lastCard):
        if self.greater:
            return attemptedCard.value >= lastCard.value
        else:
            return attemptedCard.value <= lastCard.value
    
    def modify(self, greaterBool):
        """
        if greaterBool is true, greater cards now win.
        if greaterBool is false, lower cards now win.
        """
        self.greater = greaterBool
            
class BasicSuitConstraint(Constraint):
    """
    The basic constraint that says cards may be of the same suit 
      as the lastCard (card on top of the deck)
    """
    
    def isActive(self, attemptedCard):
        return True
    
    def isLegal(self, attemptedCard, lastCard):
        return attemptedCard.suit == lastCard.suit
        
    def modify(self):
        pass
        
class WildValueConstraint(Constraint):
    """
    Allows for a "wild value"
    """
    def __init__(self):
        self.wildValue = None #basic game rule
    
    def isActive(self, attemptedCard):
        return self.wildValue != None
    
    def isLegal(self, attemptedCard, lastCard):
        return attemptedCard.value == self.wildValue
    
    def modify(self, value):
        """
        Give it an int between [2,15] or None to change the rank of this constraint
        """
        self.wildValue = value

        
class WildSuitEffect(Constraint):
    """
    Allows for a "Wild Suit" -- this suit trumps all other suits
    """
    def __init__(self):
        self.wildSuit = None
    
    def isActive(self, attemptedCard):
        return self.wildSuit != None
    
    def isLegal(self, attemptedCard, lastCard):
        return attemptedCard.suit == self.wildSuit
    
    def modify(self, suit):
        """
        Give it a suit or None to change the value of this constraint
        """
        self.wildSuit = suit
        
        
class PoisonDistanceConstraint(Constraint):
    """ 
    if you play a card valued that is dist away from the previous card, you have to draw 2
    ex) if a 6 is down, and dist = 1, then playing a 5 or 7 would cause a two card penalty    
    """
    def __init__(self):
        self.dist = None # can be None, 1, or 2
    
    def isActive(self, attemptedCard):
        return self.dist == 1 or self.dist == 2
        
    def isLegal(self, attemptedCard, lastCard):
        return not (abs(attemptedCard.value - lastCard.value) == self.dist)
        
    def modify(self, dist):
        if (dist == 1 or dist == 2) or dist == None:
            self.dist = dist
        else:
            print "invalid setting for rule poisonDistanceConstraint"
    
        
