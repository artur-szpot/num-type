import Gui
import random
from Globals import Trigger as TR
from Globals import Action as AC
from Globals import Attribute as AT
from Globals import BASIC_FONT, SPACER, ValueChanger, RewardStrategy, PenaltyStrategy, \
     ANIMATION_LENGTH, STRENGTH_INCREASE
from Color import Color
from TargetModule import *

def not_implemented_yet(requestor):
    """ Allow for creating actions in the enum before coding their behavior. """
    raise ValueError('Call to an action that was not implemented yet.')

def random_length(length):
    """ Produce a random integer of a given length. """
    return str(random.randint((10 ** length) // 9, 10 ** length - 1))

def random_text_color():
    """ Produce a random color that has a minimum average RGB value and is not too reddish. """
    minimum_average = 125
    green = random.randint(0, 255)
    blue = random.randint(int(minimum_average * 2 - green), 255)
    current_average = (green + blue) / 2
    red = random.randint(0, int(max(green, blue) * 0.66))
    color_array = [red, green, blue]
    below_min = 3 * minimum_average - sum(color_array)
    while below_min > 1:
        color_array = [round(x + min(below_min / 3, 255 - x)) for x in color_array]
        below_min = 3 * minimum_average - sum(color_array)
    return Color(rgb=tuple(color_array))

class TargetFactory:
    """ Provide the utility necessary for producing new Targets. """

    def __init__(self, functions, after_adder, board_position, board_width, font):
        """ Initialize necessary values for the factory. """
        self.targets = []
        self.after_adder = after_adder
        self.board_position = board_position
        self.board_width = board_width
        self.font = font

        self.actions = {}
        for action in AC:
            if action in functions:
                self.actions[action] = functions[action]
            else:
                self.actions[action] = not_implemented_yet

    def create(self, blueprint):
        """ Create a new Target based on the blueprint. """
        if AT.POSITION not in blueprint.attributes:
            blueprint.attributes[AT.POSITION] = len(self.targets)
            
        creator = {TargetType.NORMAL: self.create_normal,
                   TargetType.TIMED: self.create_timed,
                   TargetType.DYING_ANIMATION: self.create_dying_animation
                   }.get(blueprint.attributes[AT.TARGET_TYPE], self.create_normal)
        new_blueprint = creator(blueprint)

        # Temporary application of the attribute; it is intended to mean something else in the future.
        new_blueprint.attributes[AT.WIDTH] = self.board_width

        if new_blueprint.attributes[AT.VALUE_STRATEGY] == ValueStrategy.RANDOM_BY_STRENGTH:
            new_blueprint.attributes[AT.VALUE] = random_length(int(new_blueprint.attributes[AT.STRENGTH]))

        new_target = Target(new_blueprint, self.font)
        add_y = (Gui.GUIRect.HEIGHT + SPACER) * (new_blueprint.attributes[AT.POSITION] + 1)
        new_target.set_position(x = self.board_position[0],
                                y = self.board_position[1] + add_y)

        self.targets.append(new_target)
        self.after_adder(new_target)
       
    def create_normal(self, blueprint):
        """ Create a most basic Target. """
        attr = blueprint.attributes

        # WHEN SHOT AT
        # ===================================================================
        actions = [self.actions[AC.REWARD],
                   self.actions[AC.SPAWN],
                   self.actions[AC.DESPAWN_GOOD]
                   ]
        blueprint.events[TR.SHOT_AT] = actions[:]

        # COLOR
        # ===================================================================
        text_color = random_text_color()
        attr[AT.COLORS] = {'frame': text_color,
                           'bg': Color(rgb=Color.BLACK),
                           'text': text_color}

        # INTERACTIONS
        # ===================================================================
        attr[AT.VALUE_STRATEGY] = ValueStrategy.RANDOM_BY_STRENGTH

        vc = ValueChanger()
        vc.strategy = RewardStrategy.HARD_SET
        vc.stiff_value = 10
        vc.base_value = 0
        vc.base_multiplier = 1
        attr[AT.REWARD] = vc

        vc = ValueChanger()
        vc.strategy = PenaltyStrategy.HARD_SET
        vc.stiff_value = -1
        vc.base_value = 0
        vc.base_multiplier = 1
        attr[AT.PENALTY] = vc

        # SPAWN
        # ===================================================================
        
        spawn_blueprint = TargetBlueprint()
        spawn_attr = spawn_blueprint.attributes
        spawn_attr[AT.TARGET_TYPE] = TargetType.TIMED
        spawn_attr[AT.STRENGTH] = 4
        spawn_attr[AT.POSITION] = attr[AT.POSITION]
        attr[AT.SPAWN_BLUEPRINT] = spawn_blueprint
        
        return blueprint
    
    def create_timed(self, blueprint):
        """ Create a Target that disappears after some time. """
        attr = blueprint.attributes

        # WHEN SHOT AT
        # ===================================================================
        actions = [self.actions[AC.REWARD],
                   self.actions[AC.SPAWN],
                   self.actions[AC.DESPAWN_GOOD]
                   ]
        blueprint.events[TR.SHOT_AT] = actions[:]

        # WHEN TIMED OUT
        # ===================================================================
        actions = [self.actions[AC.SPAWN],
                   self.actions[AC.PENALTY],
                   self.actions[AC.DESPAWN_BAD]
                   ]
        blueprint.events[TR.TIME_EXPIRED] = actions[:]

        # COLOR
        # ===================================================================
        attr[AT.COLORS] = {'frame': Color(rgb=Color.WHITE),
                           'bg': Color(rgb=Color.BLACK),
                           'text': random_text_color()}

        # INTERACTIONS
        # ===================================================================
        attr[AT.VALUE_STRATEGY] = ValueStrategy.RANDOM_BY_STRENGTH
        
        vc = ValueChanger()
        vc.strategy = RewardStrategy.TIME_LEFT
        strength = int(attr[AT.STRENGTH])
        vc.stiff_value = max(1, 20 * (strength - 3) * (1 + strength/10))
        vc.base_value = 20 + strength * 10
        vc.base_multiplier = 1
        attr[AT.REWARD] = vc

        vc = ValueChanger()
        vc.strategy = PenaltyStrategy.HARD_SET
        vc.stiff_value = strength * strength * -1
        vc.base_value = strength * -5
        vc.base_multiplier = 1
        attr[AT.PENALTY] = vc
        attr[AT.TIME_TO_EXPIRE] = (strength + 1) * 1500

        # SPAWN
        # ===================================================================
        spawn_blueprint = TargetBlueprint()
        spawn_attr = spawn_blueprint.attributes
        spawn_attr[AT.TARGET_TYPE] = TargetType.TIMED
        spawn_attr[AT.STRENGTH] = min(attr[AT.STRENGTH] + STRENGTH_INCREASE, 9)
        spawn_attr[AT.POSITION] = attr[AT.POSITION]
        attr[AT.SPAWN_BLUEPRINT] = spawn_blueprint
        
        return blueprint

    def create_dying_animation(self, blueprint):
        """ Create a Target whose sole purpose is being an animation for another disappearing Target. """
        blueprint.events[TR.TIME_EXPIRED] = [self.actions[AC.DESPAWN_NONENTITY]]
        attr = blueprint.attributes
        attr[AT.VALUE_STRATEGY] = ValueStrategy.PRESET
        attr[AT.TIME_TO_EXPIRE] = ANIMATION_LENGTH
        return blueprint
