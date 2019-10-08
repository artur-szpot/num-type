import pygame
from pygame.time import get_ticks

from Globals import SPACER
from Globals import FONT_SIZE
from Globals import BG_COLOR

from Color import Color

# ===================================================================================

class Displayable:
    """ Display a static entity on the screen. """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set_position(self, x, y):
        """ Set the display position of the instance. """
        self.x = x
        self.y = y

    def get_position(self):
        """ Get the display position of the instance. """
        return (self.x, self.y)

    def draw(self):
        """ Draw the instance on the screen. """
        print('draw() method has not been overwriteen.')

# ===================================================================================

class DisplayableText(Displayable):
    """ Display a static text on the screen. """

    def __init__(self, font, value='', color=Color(rgb=Color.WHITE),  \
                 owner_rect=pygame.Rect(0,0,0,0), align='lc'):
        """ Set initial values for the instance. """
        super().__init__()
        self.value = str(value)
        self.color = color
        self.opacity = 1
        self.align = align
        self.font = font
        self.owner_rect = owner_rect
        self.set_values()

    def set_position(self, x, y):
        """ Set the display position of the instance. """
        super().set_position(x, y)
        self.set_values()

    def set_values(self, value=None, font=None, owner_rect=None, align=None):
        """
        Change any values of the instance that affect its target display rectangle.

        To set any value to null, use:
        text.value = ''
        text.set_values()
        """
        if align:
            self.align = align
        if font:
            self.font = font
        if owner_rect:
            self.owner_rect = owner_rect
        if value:
            self.value = str(value)
        
        text = self.font.render(self.value, True, Color.WHITE)
        text_rect = text.get_rect()

        if text_rect:
            if self.align[0] == 'l':
                text_rect.x = self.owner_rect.left
            elif self.align[0] == 'c':
                text_rect.centerx = self.owner_rect.left + self.owner_rect.width/2
            elif self.align[0] == 'r':
                text_rect.x = self.owner_rect.left + self.owner_rect.width - text_rect.width
            else:
                raise ValueError
                
            if self.align[1] == 't':
                text_rect.y = self.owner_rect.top
            elif self.align[1] == 'c':
                text_rect.centery = self.owner_rect.top + self.owner_rect.height/2
            elif self.align[1] == 'b':
                text_rect.y = self.owner_rect.top + self.owner_rect.height - text_rect.height
            else:
                raise ValueError
        else:
            text_rect = pygame.Rect(0,0,0,0)

        text_rect.left += self.x
        text_rect.top += self.y
        self.text_rect = text_rect

    def draw(self):
        """ Draw the instance on the screen. """
        text_color = self.color.apply_opacity(BG_COLOR, self.opacity).to_tuple()
        text = self.font.render(self.value, True, text_color)    
        window_surface.blit(text, self.text_rect)

# ===================================================================================

class FadingText(DisplayableText):
    """ Display a text with the fading effect. """

    def __init__(self, font, value, color=Color(rgb=Color.WHITE), \
                 owner_rect=pygame.Rect(0,0,0,0), align='lc', opacity=0):
        """ Set initial values for the instance. """
        super().__init__(value=value, font=font, color=color, \
                         owner_rect=owner_rect, align=align)
        self.fadeout_active = False
        self.fadein_active = False
        self.opacity = opacity

    def activate(self):
        """ Make the text fully visible. """
        self.opacity = 1
        self.fadeout_active = False
        self.fadein_active = False

    def deactivate(self):
        """ Make the text fully invisible. """
        self.opacity = 0
        self.fadeout_active = False
        self.fadein_active = False

    def fadein(self):
        """ Begin the fade-in effect. """
        self.fadein_start = get_ticks()
        self.fadeout_active = False
        self.fadein_active = True

    def fadeout(self):
        """ Begin the fade-out effect. """
        self.fadeout_start = get_ticks()
        self.fadeout_active = True
        self.fadein_active = False

    def update(self):
        """ Change the opacity based on the active effect. """
        if self.fadeout_active:
            self.opacity = 1 - (get_ticks() - self.fadeout_start)/500
            if self.opacity <= 0:
                self.opacity = 0
                self.fadeout_active = False
        elif self.fadein_active:
            self.opacity = (get_ticks() - self.fadein_start)/500
            if self.opacity >= 1:
                self.opacity = 1
                self.fadein_active = False

# ===================================================================================

class GUIRect(Displayable):
    """ Display a colored rectangle on the screen. """

    # Set up widely-used constants.
    WIDTH = FONT_SIZE * 1.2
    HEIGHT = FONT_SIZE + 12
    
    def __init__(self, x=0, y=0, width=1, height=1):
        """ Set initial values for the instance. """
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.colors = {'frame': Color(rgb=Color.WHITE),
                       'bg': Color(rgb=Color.BLACK),
                       'text': Color(rgb=Color.WHITE)}
        self.frame_width = 3

    def draw(self):
        if not window_surface:
            return
        
        """ Draw the instance on the screen. """
        self.draw_frame()

    def draw_frame(self, opacity=1):
        """ Draw the frame and inside of the rectangle. """       
        rect_color = self.colors['frame'].apply_opacity(BG_COLOR, opacity).to_tuple()
        rect_space = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(window_surface, rect_color, rect_space)

        rect_color = self.colors['bg'].to_tuple()
        f_width = self.frame_width
        f_width2 = self.frame_width * 2
        rect_space = (self.x + f_width,
                      self.y + f_width,
                      self.width - f_width2,
                      self.height - f_width2)
        pygame.draw.rect(window_surface, rect_color, rect_space)

# ===================================================================================

class GUIRectWithText(GUIRect):
    """ Display a colored rectangle with text inside on the screen. """

    def __init__(self, width=1, font=None, text=None):
        """ Set initial values for the instance. """
        if not font and not text:
            raise ValueError
        if not text:
            text = DisplayableText(font)
            
        super().__init__()
        self.text = text
        self.value = text.value
        self.width = width;
        self.height = GUIRect.HEIGHT
        self.opacity = 0.5
        self.set_position(0, 0)

    def set_position(self, x, y, margin_x=0, margin_y=0, margin_all=0):
        """ Set the display position of the instance. """
        super().set_position(x, y)
        owner_rect=pygame.Rect(x+margin_x+margin_all,
                               y+margin_y+margin_all,
                               self.width-2*(margin_x+margin_all),
                               self.height-2*(margin_y+margin_all))
        self.text.set_values(owner_rect=owner_rect)
        
    def set_value(self, value):
        """ Pass value to be set to the child. """
        self.text.set_values(value=value)
        
    def draw(self):
        """ Draw the instance on the screen. """
        self.draw_frame(self.text.opacity / 2 + 0.5)
        self.text.draw()

# ===================================================================================

class KeyButton(GUIRectWithText):
    """ Add a key-connection layer to the rectangle with text. """

    def __init__(self, font, value, color, size=(1,1), keyup_function=None):
        """ Set initial values for the instance. """
        super().__init__(text=FadingText(font=font, value=value, color=color, align='cc'))
        self.width = size[0] * GUIRect.WIDTH + (size[0]-1) * SPACER
        self.height = size[1] * GUIRect.HEIGHT + (size[1]-1) * SPACER
        self.keyup_function = keyup_function
        self.set_position(0, 0)
        
    def keydown(self):
        """ React to the key having been pressed. """
        self.text.activate()

    def keyup(self):
        """ React to the key having been let up. """
        self.text.fadeout()
        if self.keyup_function:
            self.keyup_function(self.value)

    def update(self):
        """ Allow the children to update. """
        self.text.update()

    def draw(self):
        """ Draw the instance on the screen. """
        self.draw_frame(self.text.opacity / 2 + 0.5)
        self.text.draw()

# ===================================================================================

class InputBox(GUIRectWithText):
    """ Accept and display text input. """

    MAX_LEN = 12
        
    def set_value(self, value):
        """ Pass value to be set to the child. """
        self.value = value
        if len(value) > InputBox.MAX_LEN:
            value = value[-12:]
        if value:
            self.text.set_values(value=value)
        else:
            self.text.value = ''
            self.text.set_values()
        self.opacity = 1 if value else 0.5
