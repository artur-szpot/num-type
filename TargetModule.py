import pygame
from pygame.time import get_ticks

from Globals import Trigger as TR
from Globals import Action as AC
from Globals import Attribute as AT
from Globals import ValueStrategy
from Globals import TargetType
from Globals import BG_COLOR

import random

from Color import Color

import Gui

# ===================================================================================

class TargetBlueprint:
    """ Set and pass further the desired events and attributes of a Target. """

    def __init__(self, events={}, attributes={}):
        """ Set initial values for the instance. """
        self.events = events.copy()
        self.attributes = attributes.copy()
        if not AT.VALUE_STRATEGY in self.attributes:
            self.attributes[AT.VALUE_STRATEGY] = ValueStrategy.PRESET

# ===================================================================================

class Target(Gui.GUIRectWithText):
    """ Display a target for the player to destroy by typing. """

    def __init__(self, blueprint, font):
        """ Set initial values for the instance based on the blueprint. """
        BA = blueprint.attributes
        text = Gui.DisplayableText(value=BA[AT.VALUE],
                                   font=font,
                                   color=BA[AT.COLORS]['text'],
                                   align='cc')
        super().__init__(width=BA[AT.WIDTH],
                         text=text)

        self.events = blueprint.events.copy()
        
        self.attributes = attr = BA.copy()
        attr[AT.TIME_CREATED] = get_ticks()
        attr[AT.GARBAGE] = False
        if not AT.TIME_TO_BE_SHOWN in attr:
            attr[AT.TIME_TO_BE_SHOWN] = 0
        if AT.FRAME_WIDTH in attr:
            self.frame_width = attr[AT.FRAME_WIDTH]
        self.colors = self.attributes[AT.COLORS]

    def __str__(self):
        """ Return a string identifying the Target by its value. """
        return 'Target with value ' + str(self.attributes[AT.VALUE])

    def matches(self, value):
        """ Check whether the Target's value is equal to the expected. """
        return value == self.attributes[AT.VALUE]

    def exists(self):
        """ Check whether the Target is OK to be used. """
        if self.attributes[AT.GARBAGE]:
            return False
        if get_ticks() < self.attributes[AT.TIME_TO_BE_SHOWN]:
            return False
        return True

    def fire_trigger(self, trigger):
        """ Process events to happen upon certain trigger being fired. """
        if not self.exists():
            return
        if trigger in self.events:
            for action in self.events[trigger]:
                action(requestor=self)

    def calculate_reward(self):
        """ Return calculated value of this Target's reward. """
        if AT.REWARD not in self.attributes:
            return (0, 1)
        return self.attributes[AT.REWARD].calculate(self)

    def calculate_penalty(self):
        """ Return calculated value of this Target's penalty. """
        if AT.PENALTY not in self.attributes:
            return (0, 1)
        return self.attributes[AT.PENALTY].calculate(self)

    def calculate_time_percentage_left(self):
        """ Return a 0-1 value representing the Target's time left. """
        time_left = self.calculate_time_left()
        return time_left / self.attributes[AT.TIME_TO_EXPIRE]

    def calculate_time_left(self):
        """ Return number of milliseconds the Target has left. """
        time_left = self.attributes[AT.TIME_CREATED] \
                    + self.attributes[AT.TIME_TO_EXPIRE] \
                    - get_ticks()
        if time_left < 0:
            time_left = 0
        return time_left

    def update(self):
        """ React to time passing. """
        if not self.exists:
            return
        if AT.TIME_TO_EXPIRE in self.attributes:
            if not self.calculate_time_left():
                self.fire_trigger(TR.TIME_EXPIRED)

    def draw(self):
        """ Draw the instance on the screen. """
        if not self.exists:
            return
        if self.attributes[AT.TARGET_TYPE] == TargetType.TIMED:
            self.draw_frame_timed(self.text.opacity / 2 + 0.5)
        else:
            self.draw_frame(0.5)
        self.text.draw()

    def draw_frame_timed(self, opacity):
        """ Draw a frame that shows how much time has elapsed. """
        percent_left = self.calculate_time_percentage_left()
        width_left = self.width * percent_left
        width_gone = self.width - width_left - 1
            
        if percent_left:
            pygame.draw.rect(window_surface,
                             self.colors['text'].apply_opacity(BG_COLOR, opacity).to_tuple(),
                             (self.x, self.y, width_left, self.height)
                             )
        opacity_gone = 0.2 + opacity/5
        pygame.draw.rect(window_surface,
                         self.colors['frame'].apply_opacity(BG_COLOR, opacity_gone).to_tuple(),
                         (self.x + width_left + 1, self.y, width_gone, self.height)
                         )
            
        if percent_left:
            pygame.draw.rect(window_surface,
                             self.colors['text'].apply_opacity(BG_COLOR, 0.15).to_tuple(),
                             (self.x+3, self.y+3, width_left-3, self.height-6)
                             )
        pygame.draw.rect(window_surface,
                         self.colors['bg'].to_tuple(),
                         (self.x + width_left + 1, self.y + 3, width_gone - 3, self.height - 6)
                         )
