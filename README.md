# mao-bot
An AI Framework that plays Mao. Lit.

## instructions to run
* run "python game.py". make modifications to the exact script your running at the bottom
	of game.py

## to-dos
* Constraints are done.
* Effects are done.
* Need to update RandomAgent and HMM Agent to a) change and b) recognize PoisonDist

## Observations -- put things you notice here
* Going second is a big advantage for the learning agents, because they don't have to
  take a shot in the dark.
* Despite that, LearningAgent still oftentimes outperforms HmmAgent, even with HmmBot's 'second' advantage

## architecture

### Files & Classes:
* infrastructure.py
	* Card
		* labelled "C", "H", "D" "S" for suit, & 2-14 for values.
	* Deck 
		* supports shuffling, resetting, and drawing
	* Rule
		* Simple way to identify rules, without passing an entire Constraint Object

* player.py
	* Player
		* Contains the methods the game queries the player during their turn.
		* read the documentation for details
		* at this point: DO NOT CHANGE
	
* game.py
	* Game
		* Contains fundamental logic to the game

* agent.py
	* Agent class (inherits from player?)
		* Computation and decision making on top of player class
		* build off of the abstract class you see
		* MOST OF THE WORK NEEDS TO BE DONE HERE!
		
*  Rules
	* IMPLEMENTED RULES:
		* Basic Rules
			* Value Rule: higher or lower values can be played
			* Cards of the same suit can be played, regardless of value
		* Basic Effects
			* Wild Values: a card of this value can always be played. Defaults as "7"
			* Trump Suit: Can Be played at any time (suit)
	* UNIMPLEMENTED RULES:
		* Talking: Choose from a couple of statements every time x card
		* Skip Rules: Certain cards skip the next player.
			* variant 1: 
		* Face Cards: cards have effects
