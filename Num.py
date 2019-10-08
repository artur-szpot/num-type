import pygame
import sys
from pygame.locals import *
from pygame.time import get_ticks
import random
from Globals import Trigger as TR
from Globals import Action as AC
from Globals import Attribute as AT
from Globals import SPACER, window_surface, BASIC_FONT, ValueStrategy, TargetType, BG_COLOR, \
     ANIMATION_LENGTH, STRENGTH_INCREASE, VICTORY_POINTS
import Globals
import Gui
import TargetModule
from TargetModule import Target, TargetBlueprint
from TargetFactory import TargetFactory
from Color import Color

# ===================================================================================

class Game:
    """ Run the main game loop. """

    def __init__(self):
        """ Start the game running. """
        # Load the globally-shared variables.
        global window_surface
        
        # Set up pygame.
        pygame.init()

        # Set up the window.
        self.window_size = (640, 480)
        window_surface = pygame.display.set_mode(self.window_size, 0, 32)
        pygame.display.set_caption('num.type - a numerical typing game')

        # Set up fonts.
        global BASIC_FONT
        BASIC_FONT = pygame.font.SysFont('Consolas', 48)

        # Share the global variables.
        Gui.window_surface = window_surface
        TargetModule.window_surface = window_surface

        # Set up the screens.
        self.screens = {}
        self.screens['welcome_screen'] = WelcomeScreen(self)
        self.current_screen = self.screens['welcome_screen']

    def begin_game(self):
        self.score_keeper = ScoreKeeper()
        self.screens['main_screen'] = MainScreen(self)
        self.current_screen = self.screens['main_screen']

    def finish(self, victory=False):
        self.score_keeper.finish(victory)
        self.screens['end_screen'] = EndScreen(self)
        self.screens['end_screen'].setup(self.score_keeper)
        self.current_screen = self.screens['end_screen']

    def mainmenu(self):
        self.current_screen = self.screens['welcome_screen']
        
    def main(self):
        """ Keep the game running. """
        while True:
            self.current_screen.events()
            self.current_screen.update()
            self.current_screen.draw()

    def close(self):
        """ Exit the game. """
        pygame.quit()
        sys.exit()

# ===================================================================================

class GameScreen:
    """ Base class for every screen in the game. """

    def __init__(self, owner):
        """ Initialize the variables of the screen. """
        self.gui = []
        self.gui_updatable = []
        self.key_events = {KEYUP:{}, KEYDOWN:{}}
        # functions
        self.owner = owner
        self.setup()

    def setup(self):
        """ Screen-specific preparation. """
        pass

    def add_gui(self, new_gui):
        """ Add a new GUI element to the drawing queue. """
        self.gui.append(new_gui)

    def add_gui_updatable(self, new_gui):
        """ Add a new GUI element to the updatable drawing queue. """
        self.add_gui(new_gui)
        self.gui_updatable.append(new_gui)

    def remove_gui(self, garbage):
        """ Remove a GUI from the drawing queue(s). """
        if garbage in self.gui_updatable:
            self.gui_updatable.remove(garbage)
        if garbage in self.gui:
            self.gui.remove(garbage)

    def events(self):
        """ Process events (mostly keystrokes). """
        events_to_process = pygame.event.get()
        for event in events_to_process:
            if event.type == QUIT:
                self.owner.close()
        return events_to_process

    def update(self):
        """ Update GUI from the updatable queue. """
        for updatable in self.gui_updatable:
            updatable.update()       
        
    def draw(self):
        """ Draw GUI on the screen. """
        window_surface.fill((0, 0, 0))
        for element in self.gui:
            element.draw()
        pygame.display.update()

# ===================================================================================

class Collector:
    """ Store temporarily the values of user's keystrokes. """

    def __init__(self, update_function=None):
        """ Initialize the variables. """
        self.collected = []
        self.update_function = update_function

    def collect(self, value):
        """ Add a new digit to the end of the list. """
        self.collected.append(value)
        if self.update_function:
            self.update_function()

    def backspace(self):
        """ Remove the last element from the list. """
        if len(self.collected):
            self.collected.pop()
        if self.update_function:
            self.update_function()

    def pop(self):
        """ Return the list contents and clear them. """
        retval = ''.join(self.collected)
        self.collected = []
        if self.update_function:
            self.update_function()
        return retval

# ===================================================================================

class ScoreKeeper():
    """ Store the data about user performance. """

    def __init__(self):
        """ Initialize the variables. """
        self.points_gained = 0
        self.points_lost = 0
        self.targets_shot = 0
        self.targets_timed_out = 0
        self.misses = 0

    def begin(self):
        self.time_began = get_ticks()

    def finish(self, victory):
        self.victory = victory
        time_elapsed_seconds = (get_ticks() - self.time_began) // 1000
        time_elapsed_minutes = time_elapsed_seconds // 60
        time_elapsed_seconds -= time_elapsed_minutes * 60
        time_elapsed = ''
        if time_elapsed_minutes:
            time_elapsed = '{} minute'.format(time_elapsed_minutes) \
                           + ('s ' if time_elapsed_minutes > 1 else ' ')
        if time_elapsed_seconds:
            time_elapsed += '{} second'.format(time_elapsed_seconds) \
                            + ('s ' if time_elapsed_seconds > 1 else ' ')
        self.time_elapsed = time_elapsed
        accuracy = 0
        effectiveness = 0
        if self.targets_shot:
            accuracy = int((self.targets_shot / (self.targets_shot + self.misses)) * 100)
            effectiveness = int((self.targets_shot / (self.targets_shot + self.targets_timed_out)) * 100)
        self.accuracy = accuracy
        self.effectiveness = effectiveness

# ===================================================================================

class WelcomeScreen(GameScreen):
    """ Display and control the main menu of the game. """

    def setup(self):
        """ Initialize the GUI and place it properly. """
        # Create the main menu font.
        WELCOME_FONT_TITLE = pygame.font.SysFont('Consolas', 28)
        WELCOME_FONT_INSTRUCTIONS = pygame.font.SysFont('Consolas', 20)
        
        # Create the title display.
        self.title_display = Gui.DisplayableText(value='num.type',
                                                 font=WELCOME_FONT_TITLE,
                                                 color=Color(rgb=Color.WHITE),
                                                 align='cc')
        self.title_display.set_position(640/2, 40)
        self.add_gui(self.title_display)
        self.title_colors = [Color(rgb=(200, 20, 20)),
                             Color(rgb=(200, 200, 20)),
                             Color(rgb=(20, 200, 20)),
                             Color(rgb=(20, 200, 200)),
                             Color(rgb=(20, 20, 200)),
                             Color(rgb=(200, 20, 200))]
        self.title_color_current = 0
        self.title_color_next = 1
        self.title_color_current_began_at= get_ticks()
        
        # Create the subtitle display.
        self.subtitle_display = Gui.DisplayableText(value='a numerical typing game',
                                                    font=WELCOME_FONT_TITLE,
                                                    color=Color(rgb=Color.WHITE),
                                                    align='cc')
        self.subtitle_display.set_position(640/2, 70)
        self.add_gui(self.subtitle_display)
        self.subtitle_color_current = 1
        self.subtitle_color_next = 2
        
        # Create the instructions display.
        self.instr_displays = []
        instructions = ['Attempt to type in numbers as fast as you can.',
                        'You can only use the numeric keyboard.',
                        'Every time you "shoot" a target in time, it will grant',
                        'you points.',
                        'Every time you miss, you will lose one heart,',
                        'so type carefully.',
                        'You can use backspace if you mistype.',
                        'If a target times out, you will lose points.',
                        'The game will become progressively harder as you play.',
                        'Win by accumulating {} points.'.format(VICTORY_POINTS),
                        'Lose by going below 0 points or losing all hearts.',
                        '',
                        'Press ENTER to begin.',
                        'Pressing ESCAPE at any time will end the game in defeat.',
                        'Good luck!'
                        ]
        for instruction in instructions:
            new_display = Gui.DisplayableText(value=instruction,
                                              font=WELCOME_FONT_INSTRUCTIONS,
                                              color=Color(rgb=Color.WHITE),
                                              align='lc')
            new_display.set_position(20, 120 + 23 * len(self.instr_displays))
            self.instr_displays.append(new_display)
            self.add_gui(new_display)

    def events(self):
        """ Process events (mostly keystrokes). """
        events_to_process = super().events()
        for event in events_to_process:
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.owner.close()
                elif event.key == K_RETURN or event.key == 271:
                    self.owner.begin_game()

    def update(self):
        """ Make the title and subtitle change colors. """
        super().update()
        percent = (get_ticks() - self.title_color_current_began_at) / 3000
        while percent > 1:
            self.title_color_current = self.increase_color_index(self.title_color_current)
            self.title_color_next = self.increase_color_index(self.title_color_next)
            self.subtitle_color_current = self.increase_color_index(self.subtitle_color_current)
            self.subtitle_color_next = self.increase_color_index(self.subtitle_color_next)
            percent -= 1
            self.title_color_current_began_at = get_ticks()
        self.title_display.color = Color.weighted_average(self.title_colors[self.title_color_current],
                                                          self.title_colors[self.title_color_next],
                                                          percent)
        self.subtitle_display.color = Color.weighted_average(self.title_colors[self.subtitle_color_current],
                                                             self.title_colors[self.subtitle_color_next],
                                                             percent)

    def increase_color_index(self, color):
        """ Helper function for increasing color indices. """
        color += 1
        if color == len(self.title_colors):
            return 0
        return color

# ===================================================================================

class EndScreen(GameScreen):
    """ Display and control the message once the game is over. """

    def __init__(self, owner):
        """ Initialize the variables of the screen. Overwritten for modified setup call. """
        self.gui = []
        self.gui_updatable = []
        self.key_events = {KEYUP:{}, KEYDOWN:{}}
        self.owner = owner

    def setup(self, score_keeper):
        """ Initialize the GUI and place it properly. """        
        # Create the scores font.
        SCORE_FONT = pygame.font.SysFont('Consolas', 28)
        
        # Create the main message.
        self.message = Gui.DisplayableText(value='VICTORY' if score_keeper.victory else 'DEFEAT',
                                           font=BASIC_FONT,
                                           color=Color(rgb=Color.WHITE),
                                           align='cc')
        self.message.set_position(640/2, 40)
        self.add_gui(self.message)
        
        # Create the instructions display.
        self.score_displays = []
        scores = ['Final point score: {}'.format(score_keeper.points_gained - score_keeper.points_lost),
                  'Total points gained: {}'.format(score_keeper.points_gained),
                  'Total points lost: {}'.format(score_keeper.points_lost),
                  'Total targets shot: {}'.format(score_keeper.targets_shot),
                  'Total targets timed out: {}'.format(score_keeper.targets_timed_out),
                  'Total misses: {}'.format(score_keeper.misses),
                  'Accuracy: {}%'.format(score_keeper.accuracy),
                  'Effectiveness: {}%'.format(score_keeper.effectiveness),
                  'Time played: {}'.format(score_keeper.time_elapsed),
                  '',
                  'Press ESCAPE to return to main menu.'
                  ]
        for score in scores:
            new_display = Gui.DisplayableText(value=score,
                                              font=SCORE_FONT,
                                              color=Color(rgb=Color.WHITE),
                                              align='lc')
            new_display.set_position(20, 100 + 30 * len(self.score_displays))
            self.score_displays.append(new_display)
            self.add_gui(new_display)

    def events(self):
        """ Process events (mostly keystrokes). """
        events_to_process = super().events()
        for event in events_to_process:
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.owner.mainmenu()
                    
# ===================================================================================

class MainScreen(GameScreen):
    """ Display and control the main screen of the game. """

    def setup(self):
        """ Initialize the GUI and place it properly; initialize the variables. """
        # Set up the collector.
        self.collector = Collector()
        self.collector.update_function = self.update_input_box
        
        # Create a key map.
        keycodes = {256: ['0', (2,1), (18,169,202)],
                    257: ['1', (1,1), (196,170,77)],
                    258: ['2', (1,1), (242,210,72)],
                    259: ['3', (1,1), (45,186,97)],
                    260: ['4', (1,1), (121,124,125)],
                    261: ['5', (1,1), (133,145,115)],
                    262: ['6', (1,1), (196,52,92)],
                    263: ['7', (1,1), (245,245,252)],
                    264: ['8', (1,1), (206,224,182)],
                    265: ['9', (1,1), (244,124,124)],
                    266: ['.', (1,1), (255,255,255)],
                    267: ['/', (1,1), (255,255,255)],
                    268: ['*', (1,1), (255,255,255)],
                    269: ['-', (1,1), (255,255,255)],
                    270: ['+', (1,2), (255,255,255)],
                    271: ['e', (1,2), (255,255,255)],
                    300: ['n', (1,1), (255,255,255)]
                    }

        # Create the key displays.
        self.keys = {}
        for code in keycodes:
            self.keys[code] = Gui.KeyButton(value=keycodes[code][0],
                                            font=BASIC_FONT,
                                            size=keycodes[code][1],
                                            color=Color(rgb=keycodes[code][2]))
            if code >= 256 and code <=265:
                self.keys[code].keyup_function = self.collector.collect
        
        layout = ((300, 267, 268, 269),
                  (263, 264, 265, 270),
                  (260, 261, 262),
                  (257, 258, 259, 271),
                  (256, 266))
        x = SPACER
        y = SPACER
        for row in layout:
            for col in row:
                self.keys[col].set_position(x, y)
                self.add_gui_updatable(self.keys[col])
                x += self.keys[col].width + SPACER
            y += Gui.GUIRect.HEIGHT + SPACER
            x = SPACER

        # Create the score display.
        self.hp_display = Gui.DisplayableText(value='♥♥♥',
                                              font=BASIC_FONT,
                                              color=Color(rgb=Color.WHITE),
                                              align='rc')
        self.hp_display.set_position(640 - SPACER, 400)
        self.add_gui(self.hp_display)

        # Create the HP display.
        self.score_display = Gui.DisplayableText(value='Score: 0',
                                                 font=BASIC_FONT,
                                                 color=Color(rgb=Color.WHITE),
                                                 align='lc')
        self.score_display.set_position(SPACER, 400)
        self.add_gui(self.score_display)

        # Create the HP lost display.
        self.hp_lost_display = Gui.FadingText(value='♥',
                                              font=BASIC_FONT,
                                              color=Color(rgb=Color.RED),
                                              align='lc')
        self.hp_lost_display.deactivate()
        self.add_gui(self.hp_lost_display)
        self.add_gui_updatable(self.hp_lost_display)

        # Create the input box.
        self.input_box = Gui.InputBox(width=self.owner.window_size[0] - 4 * Gui.KeyButton.WIDTH - 6 * SPACER,
                                      font=BASIC_FONT)
        self.input_box.set_position(x=4 * (Gui.GUIRect.WIDTH + SPACER) + SPACER,
                                    y=SPACER,
                                    margin_x=5)
        self.add_gui(self.input_box)

        # Set up the TargetFactory.
        func_dict = {AC.REWARD: self.reward,
                     AC.PENALTY: self.penalty,
                     AC.DESPAWN_GOOD: self.despawn_good,
                     AC.DESPAWN_BAD: self.despawn_bad,
                     AC.DESPAWN_NONENTITY: self.despawn_nonentity,
                     AC.SPAWN: self.spawn}
        self.target_factory = TargetFactory(functions=func_dict,
                                            after_adder=self.after_adder,
                                            board_position=self.input_box.get_position(),
                                            board_width=self.input_box.width,
                                            font=BASIC_FONT)

        # Set up a simple game.
        self.score = 0
        self.hp = 10
        for i in range(4):
            blueprint = TargetBlueprint()         
            blueprint.attributes[AT.TARGET_TYPE] = TargetType.TIMED
            blueprint.attributes[AT.STRENGTH] = 3 - STRENGTH_INCREASE
            self.target_factory.create(blueprint)
        self.owner.score_keeper.begin()

        # Set up the key events map.
        for code in keycodes:
           self.key_events[KEYUP][code] = [self.keys[code].keyup]
           self.key_events[KEYDOWN][code] = [self.keys[code].keydown]
        self.key_events[KEYUP][K_ESCAPE] = [self.clear_or_surrender]
        self.key_events[KEYUP][8] = [self.collector.backspace]       # backspace
        self.key_events[KEYUP][271].append(self.shoot_target)        # enter
        # Below function disabled in the current one-mode-only game.
        # self.key_events[KEYUP][270].append(self.add_target)        # +
        self.key_events[KEYUP][46] = self.key_events[KEYUP][266]     # .=,
        self.key_events[KEYDOWN][46] = self.key_events[KEYDOWN][266] # .=,

        # Perform the first update to show GUI properly.
        self.update_score()

    def events(self):
        """ Process events (mostly keystrokes). """
        events_to_process = super().events()
        for event in events_to_process:
            if event.type in self.key_events:
                if event.key in self.key_events[event.type]:
                    for action in self.key_events[event.type][event.key]:
                        action()

    def update(self):
        """ Perform garbage collection and update the updatable GUI. """
        super().update()
        garbage = []
        for target in self.target_factory.targets:
            if target.attributes[AT.GARBAGE]:
                garbage.append(target)
        while len(garbage):
            target = garbage.pop()
            self.remove_gui(target)

    def remove_gui(self, garbage):
        """ Remove the element from the drawing queue(s) and from the list of Targets, if applicable. """
        super().remove_gui(garbage)
        if garbage in self.target_factory.targets:
            self.target_factory.targets.remove(garbage)   

    # GAME LOGIC
    # =================================================================================

    def clear_or_surrender(self):
        if len(self.collector.collected):
            self.collector.pop()
            self.update_input_box()
        else:
            self.owner.finish(False)

    def update_input_box(self):
        """ Update the value displayed in the input box. """
        self.input_box.set_value(''.join(self.collector.collected))

    def add_target(self):
        """ Add a new Target at user's behest. """
        # Temporarily unused, as there is one mode only.
        blueprint = TargetBlueprint()
        blueprint.attributes[AT.TARGET_TYPE] = TargetType.TIMED
        blueprint.attributes[AT.STRENGTH] = 4
        self.target_factory.create(blueprint)

    def spawn(self, requestor):
        """ Spawn a new Target. """
        RA = requestor.attributes
        if not RA[AT.GARBAGE]:
            blueprint = RA[AT.SPAWN_BLUEPRINT]
            blueprint.attributes[AT.TIME_TO_BE_SHOWN] = get_ticks() + ANIMATION_LENGTH
            self.target_factory.create(blueprint)
        
    def after_adder(self, new_target):
        """ Add the new Target to the GUI queues of the screen. """
        self.gui.append(new_target)
        self.gui_updatable.append(new_target)
        
    def shoot_target(self):
        """ Attempt to shoot a Target. If successful, receive reward; otherwise, lose HP. """
        value = self.collector.pop()
        if not value:
            return
        found = None
        for target in self.target_factory.targets:
            if target.matches(value):
                found = target
                break
        if found:
            self.owner.score_keeper.targets_shot += 1
            found.fire_trigger(TR.SHOT_AT)
        else:
            self.owner.score_keeper.misses += 1
            self.lose_hp()

    def lose_hp(self):
        """ Lose 1 point of HP. """
        self.hp_lost_display.set_position(self.hp_display.x - self.hp_display.text_rect.width,
                                          self.hp_display.y)
        self.hp_lost_display.activate()
        self.hp_lost_display.fadeout()
        self.hp -= 1
        self.update_score()
        self.check_end()

    def update_score(self):
        """ Display the current score and HP. """
        self.score_display.set_values(value='Score: {}'.format(self.score))
        self.hp_display.set_values(value='♥' * self.hp)

    def score_change(self, value=0, multiplier=1):
        """ Change the user's score. """
        if value > 0:
            self.owner.score_keeper.points_gained += value
        else:
            self.owner.score_keeper.points_lost -= value
        self.score += value
        self.score *= multiplier
        self.score = int(self.score)
        self.update_score()
        self.check_end()

    def reward(self, requestor):
        """ Process a reward from a shot Target. """
        value, multiplier = requestor.calculate_reward()
        self.score_change(value, multiplier)

    def penalty(self, requestor):
        """ Process a penalty from a timed-out Target. """
        value, multiplier = requestor.calculate_penalty()
        self.score_change(value, multiplier)

    def despawn_good(self, requestor):
        """ Mark a shot Target as garbage and display its dying animation. """
        requestor.attributes[AT.GARBAGE] = True
        blueprint = TargetBlueprint()
        attr = blueprint.attributes
        attr[AT.TARGET_TYPE] = TargetType.DYING_ANIMATION
        attr[AT.VALUE] = requestor.attributes[AT.REWARD].display
        attr[AT.COLORS] = {'frame': Color(rgb=Color.BLACK),
                           'bg': requestor.colors['text'],
                           'text': Color(rgb=Color.BLACK)}
        attr[AT.POSITION] = requestor.attributes[AT.POSITION]
        self.target_factory.create(blueprint)

    def despawn_bad(self, requestor):
        """ Mark a timed-out Target as garbage and display its dying animation. """
        self.owner.score_keeper.targets_timed_out += 1
        requestor.attributes[AT.GARBAGE] = True               
        blueprint = TargetBlueprint()
        attr = blueprint.attributes
        attr[AT.TARGET_TYPE] = TargetType.DYING_ANIMATION
        attr[AT.VALUE] = requestor.attributes[AT.PENALTY].display
        attr[AT.COLORS] = {'frame': Color(rgb=Color.RED),
                           'bg': Color(rgb=(120, 0, 0)),
                           'text': Color(rgb=Color.RED)}
        attr[AT.POSITION] = requestor.attributes[AT.POSITION]
        self.target_factory.create(blueprint)

    def despawn_nonentity(self, requestor):
        """ Mark an animation-only Target as garbage. """
        requestor.attributes[AT.GARBAGE] = True

    def check_end(self):
        """ Checks whether any game-end condition has been reached. """
        if not self.hp or self.score < 0:
            self.owner.finish(False)
        elif self.score >= VICTORY_POINTS:
            self.owner.finish(True)

# ===================================================================================

""" Run the game. """
if __name__ == '__main__':
    game = Game()
    game.main()
