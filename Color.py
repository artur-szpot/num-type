""" Provide a Color utility customized to the project needs. """

import random

# ===================================================================================
# deal with hex values

HEX_VALUES = {'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15}

def dehex(_hex):
    """ Translate a two-digit hex value into a decimal value. """
    values_in = [_hex[0], _hex[1]]
    values_out = [0,0]
    for index in (0,1):
        if values_in[index] in HEX_VALUES:
            values_out[index] = HEX_VALUES[values_in[index]]
        else:
            values_out[index] = int(values_in[index])
    return values_out[0] * 16 + values_out[1]

# ===================================================================================
# pseudocolor

class PseudoColor:
    """ Hold temporary, potentially nonsensical values for Color operations. """

    def __init__(self, r, g, b):
        """ Save the values passed to the constructor. """
        self.r = r
        self.g = g
        self.b = b

    def to_tuple(self):
        """ Return a tuple with the color values. """
        return (self.r, self.g, self.b)

    def __str__(self):
        return str(self.to_tuple())

# ===================================================================================
# color

class COL:
    """ Provide a shorthand for creating the most popular Color instances. """
    
    @staticmethod
    def BLACK():
        """ Shorthand for creating one of the most useful colors. """
        return Color(rgb=Color.BLACK)

    @staticmethod
    def WHITE():
        """ Shorthand for creating one of the most useful colors. """
        return Color(rgb=Color.WHITE)

    @staticmethod
    def RED():
        """ Shorthand for creating one of the most useful colors. """
        return Color(rgb=Color.RED)

    @staticmethod
    def GREEN():
        """ Shorthand for creating one of the most useful colors. """
        return Color(rgb=Color.GREEN)

    @staticmethod
    def BLUE():
        """ Shorthand for creating one of the most useful colors. """
        return Color(rgb=Color.BLUE)
    
class Color:
    """ Provide utility necessary for dealing with colors. """

    # =============================================================
    # an enum of ready color tuples
    
    BLACK = (0,   0,   0)
    WHITE = (255, 255, 255)
    RED   = (255, 0,   0)
    GREEN = (0,   255, 0)
    BLUE  = (0,   0,   255)

    # =============================================================
    # a random generator

    @staticmethod
    def random_color():
        """ Generate a totally random color. """
        return Color(random.randint(0,255), random.randint(0,255), random.randint(0,255))

    # =============================================================
    # constructor

    def __init__(self, r=-1, g=-1, b=-1, rgb=(-1,-1,-1), _hex=''):
        """ Read one of the provided values and initialize own RGB values. """
        fail = len(rgb) != 3

        if _hex and _hex[:1] == '#':
            _hex = _hex[1:]
            
        self.r = r
        self.g = g
        self.b = b
        
        if not fail and rgb[0] >= 0 and rgb[1] >= 0 and rgb[2] >= 0:
            self.r = rgb[0]
            self.g = rgb[1]
            self.b = rgb[2]
        elif len(_hex) == 6:
            _hex = _hex.upper()
            self.r = dehex(_hex[0:2])
            self.g = dehex(_hex[2:4])
            self.b = dehex(_hex[4:6])

        self.r = round(self.r)
        self.g = round(self.g)
        self.b = round(self.b)

        for x in (self.r, self.g, self.b):
            if x < 0 or x > 255:
                fail = True

        if fail:
            print('Wrong values passed during Color initialization.')
            print('r = {}, g = {}, b = {}, rgb = {}, _hex = {}'.format(r, g, b, rgb, _hex))
            raise ValueError

    # =============================================================
    # helpers

    def __str__(self):
        return str(self.to_tuple())

    def to_tuple(self):
        """ Return a tuple with the color values. """
        return (self.r, self.g, self.b)

    # =============================================================
    # operations

    def __add__(self, other):
        """ Sum two colors together. """
        return PseudoColor(r = self.r + other.r,
                           g = self.g + other.g,
                           b = self.b + other.b)

    def __sub__(self, other):
        """ Substract another color from self. """
        return PseudoColor(r = self.r - other.r,
                           g = self.g - other.g,
                           b = self.b - other.b)

    def sum(self):
        """ Return a sum of the color values. """
        return self.r + self.g + self.b

    @staticmethod
    def weighted_average(color1, color2, percent):
        return Color(r = color1.r * (1-percent) + color2.r * percent,
                     g = color1.g * (1-percent) + color2.g * percent,
                     b = color1.b * (1-percent) + color2.b * percent)

    # =============================================================
    # corrections

    def apply_opacity(self, bg_color, opacity):
        """ Calculate the color against a background color with given opacity. """
        calc_diff = self - bg_color
        # print('bg_color, opacity, calc_diff = {}, {}, {})'.format(bg_color, opacity, calc_diff))
        return Color(r = bg_color.r + calc_diff.r * opacity,
                     g = bg_color.g + calc_diff.g * opacity,
                     b = bg_color.b + calc_diff.b * opacity)

    def correct_minimum_average(self, minimum):
        """ Correct the color to have an average at the minimum level (0-255). """
        diff = 3 * minimum - self.sum()
        if diff > 0:
            # Apply a bit of randomness to not always produce the same color.
            diff += random.randint(0, 40)
            diff /= 3
            self.r += diff
            self.g += diff
            self.b += diff
            self.correct()

    def correct_maximum_average(self, maximum):
        """ Correct the color to have an average at the maximum level (0-255). """
        diff = 3 * maximum - self.sum()
        if diff < 0:
            # Apply a bit of randomness to not always produce the same color.
            diff -= random.randint(0, 40)
            diff /= 3
            self.r += diff
            self.g += diff
            self.b += diff
            self.correct()

    def correct_avoid_gray(self):
        """ Correct the color to not be gray. """
        diff = abs((self.r-self.g) * (self.r-self.b) * (self.b-self.g))
        if diff < 1000:
            # choose a random color (not red though) and change it by 30-40
            color_index = random.randint(1, 2)
            color_mod = random.randint(30, 40)
            color_mod *= 1 if self.r < 200 else -1
            if color_index == 1:
                self.g += color_mod
            else:
                self.b += color_mod
            self.correct()

    def correct_avoid_red(self):
        """ Correct the color to not be predominantly red. """
        if self.r - self.g > 40 and self.r - self.b > 40:
            self.r = max(self.g, self.b) + 20

    def correct(self):
        """ Check whether manipulating color values hasn't gone too far. """
        for x in (self.r, self.g, self.b):
            if x < 0:
                x = 0
            elif x > 255:
                x = 255
