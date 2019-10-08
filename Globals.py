from enum import Enum
from Color import Color

FONT_SIZE = 48
SPACER = 10
window_surface = None
BASIC_FONT = None
BG_COLOR = Color(rgb=Color.BLACK)

# class font (fontsize, font object)

Trigger = Enum('Trigger',' '.join([
    'TIME_EXPIRED',
    'SHOT_AT',
    'SHOT_AT_ANOTHER',
    'SHOT_MISSED',
    'COMBO_BROKEN',
    'LOST_HP',
    'GAINED_HP',
    'SHOWN_UP'
    ]))
Action = Enum('Action',' '.join([
    'REWARD',
    'PENALTY',
    'SPAWN',
    'DESPAWN_GOOD',
    'DESPAWN_BAD',
    'DESPAWN_NONENTITY',
    'WIN_GAME',
    'LOSE_GAME',
    'HEAL_SELF',
    'DAMAGE_SELF',
    'REFRESH_TIMER',
    'HEAL_PLAYER',
    'DAMAGE_PLAYER',
    'CHANGE_SPAWN_RATE',
    'CHANGE_RULES',
    ]))
Attribute = Enum('Attribute',' '.join([
    'GARBAGE',
    'VALUE_STRATEGY',
    'TIME_CREATED',
    'TIME_TO_BE_SHOWN',
    'TIME_TO_EXPIRE',
    'REWARD',
    'PENALTY',
    'STRENGTH',
    'SPAWN_BLUEPRINT',
    'COLORS',
    'FRAME_WIDTH',
    'TARGET_TYPE',
    'WIDTH',
    'VALUE',
    'POSITION'
    ]))
RewardStrategy = Enum('RewardStrategy',' '.join([
    'HARD_SET',
    'TIME_LEFT'
    ]))
PenaltyStrategy = Enum('PenaltyStrategy',' '.join([
    'HARD_SET',
    'TIME_LEFT'
    ]))
ValueStrategy = Enum('ValueStrategy',' '.join([
    'PRESET',
    'RANDOM_BY_STRENGTH'
    ]))
TargetType = Enum('TargetType',' '.join([
    'NORMAL',
    'TIMED',
    'DYING_ANIMATION'
    ]))

ANIMATION_LENGTH = 300
STRENGTH_INCREASE = 0.3
VICTORY_POINTS = 10000

def signed_int(value):
    """ Return the integer value as a string with enforced sign usage. """
    if value < 0:
        return str(value)
    else:
        return '+' + str(value)

class ValueChanger():
    """ Provide the utility for holding properties intended to modify other values. """

    def __init__(self, strategy=None, stiff_value=0, base_value=0, base_multiplier=1, value=0, multiplier=1, display=''):
        """ Initialize the variables for the class instance. """
        self.strategy = strategy
        self.stiff_value = stiff_value
        self.base_value = base_value
        self.base_multiplier = base_multiplier
        self.value = value
        self.multiplier = multiplier
        self.display = display

    def calculate(self, requestor):
        """ Calculate the variable values for being used outside of the class. """
        if self.strategy in RewardStrategy:
            if self.strategy == RewardStrategy.HARD_SET:
                self.value = self.stiff_value + self.base_value
                self.multiplier = self.base_multiplier
            elif self.strategy == RewardStrategy.TIME_LEFT:
                self.value = self.stiff_value + self.base_value * requestor.calculate_time_percentage_left()
                self.multiplier = self.base_multiplier
            self.value = int(self.value)
            self.display = signed_int(self.value)
            return (self.value, self.multiplier)
        
        elif self.strategy in PenaltyStrategy:
            if self.strategy == PenaltyStrategy.HARD_SET:
                self.value = self.stiff_value + self.base_value
                self.multiplier = self.base_multiplier
            elif self.strategy == PenaltyStrategy.TIME_LEFT:
                self.value = self.stiff_value + self.base_value * requestor.calculate_time_percentage_left()
                self.multiplier = self.base_multiplier
            self.value = int(self.value)
            self.display = signed_int(self.value)
            return (self.value, self.multiplier)
            
