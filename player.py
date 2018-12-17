from infrastructure import *
import random

class Player(object):
    def __init__(self, name):
        self.hand = []
        self.name = name
        
        self.wins = 0
    
    def __str__(self):
        return str(self.name)
    
    # gives a card back to a player
    def takeCard(self, card):
        if card != None:
            self.hand.append(card)
        else:
            print "takeCard: no card drawn. This seems like trouble -- investigate"
        
    def won(self):
        if len(self.hand) == 0:
            self.wins += 1
            return True
        else:
            return False
            
    def clearHand(self, deck=None):
        """
        If there is a deck, return the card to it.
        Else, simply clear the hand
        """
        if (deck == None):
            self.hand = []
        else:
            for card in self.hand:
                deck.append(card)
    
    # THIS IS WHAT THE GAME CALLS TO ASK FOR A PLAYER'S ACTION
    # removes and returns a card
    def takeAction(self, lastCard):
        """
        the Game class calls this method on the player when it wants the player
        to submit a card for legality evaluation.
        the "last card" -- ie, the most recent faceup card -- is supplied as an argument.
        
        this method also handles modification of the player's "hand"
        
        returns the card that was chosen.
        """
        card = self.chooseCard(lastCard)
        self.hand.remove(card)
        return card
    
    # Agent Method
    def modifyRule(self, game):
        """
        The Game calls this method when a player wins, and is allowed to change a rule
        """
        pass
        
    #AI METHOD HERE. Returns a card. DOES NOT REMOVE IT!
    def chooseCard(self, lastCard):
        """
        AI implemented method for determining which card to return
        Default behavior: returns first card
        
        Return 
        """
        pass
        
    def screwOpponent(self, playerList):
        """
        AI implemented method -- let's players screw over an opponent
        """
        pass

    # AI IMPLEMENTED METHOD
    def notify(self, notification, game):
        """
        notified when the state of the game changes, allows for analysis opportunity (ie updating beliefs)
        """
        pass
        
    def getFeedback(self, isLegal):
        """
        the player gets feedback from the game on whether their card was legal or not
        """
        pass
    


#tests

# basic player taking action
# d = Deck()
# p = Player("j", True)
# p.takeCard(d.drawCard())
# p.takeCard(d.drawCard())
# print p.takeAction()
