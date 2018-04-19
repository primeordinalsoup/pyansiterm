#!/usr/bin/env python3
""" simple multi-line terminal output with colour, for console app progress bars, simple text boxes etc. """

from enum import Enum
import sys, time
import subprocess

class Colour(Enum):
    DEFAULT        = 0
    BLACK          = 1
    RED            = 2
    GREEN          = 3
    YELLOW         = 4
    BLUE           = 5
    MAGENTA        = 6
    CYAN           = 7
    WHITE          = 8

class Move(Enum):
    UP      = 0x41
    DOWN    = 0x42
    FORWARD = 0x43
    BACK    = 0x44

class EraseRegion(Enum):
    CSR_TO_END   = 0
    CSR_TO_START = 1
    ALL          = 2

class ANSICode(object):
    # constant class variables
    CSI = "\x1b["    # Control Sequence Introducer, see https://en.wikipedia.org/wiki/ANSI_escape_code
    fg_map = {
        "BLACK":   "30",
        "RED":     "31",
        "GREEN":   "32",
        "YELLOW":  "33",
        "BLUE":    "34",
        "MAGENTA": "35",
        "CYAN":    "36",
        "WHITE":   "37",
        "DEFAULT": "39",
        }
    bg_map = {
        "BLACK":   "40",
        "RED":     "41",
        "GREEN":   "42",
        "YELLOW":  "43",
        "BLUE":    "44",
        "MAGENTA": "45",
        "CYAN":    "46",
        "WHITE":   "47",
        "DEFAULT": "49",
        }

    def __enter__(self):
        """method to make this class a 'context manager', i.e. it
        can be used in a with clause and the __exit__ method will
        always be invoked on leaving, even for exceptions."""
        return self
       
    def __exit__(self, etype, value, traceback):
        """method to make this class a 'context manager', i.e. it
        can be used in a with clause and the __exit__ method will
        always be invoked on leaving, even for exceptions."""
        self.resetTerm()
        return True

    def resetTerm(self):
        """reset the terminal to defaults.  NOTE the 'RIS' command
        does not seem to work, so we just unconditionally set all
        attributes OFF."""
        # output the ANSI 'RIS' sequence, Reset to Initial State
        #sys.stdout.write("\x1bc")
        # output 'all attributes OFF' sequence
        sys.stdout.write("\x1b[0m")
        
    def colour2fgCode(self, colour):
        try:
            return self.fg_map[colour.name] 
        except (AttributeError, TypeError):
            raise AssertionError('Input variable must be Colour enum')

    def colour2bgCode(self, colour):
        try:
            return self.bg_map[colour.name] 
        except (AttributeError, TypeError):
            raise AssertionError('Input variable must be Colour enum')

    def put(self):
        sys.stdout.write(self._cmnd)
        sys.stdout.flush()

    def __str__(self):
        """string representation, used in direct print() calls with object, and
        to support our add/radd operators."""
        # now return the ANSI code to erase
        return self._cmnd

    def __call__(self):
        """we act as a string in default case, so we can instantiate and print."""
        return self.__str__()
    
    def __radd__(self, other):
        """we can mix and match strings and Font() objects to compose our output."""
        return other + str(self)

    def __add__(self, other):
        """we can mix and match strings and Font() objects to compose our output."""
        return str(self) + other

class Move(ANSICode):
    def __init__(self, up=None, down=None, left=None, right=None):
        self._cmnd = ""
        if up is not None:
            self._cmnd += self._moveSeq(up, "A")
        if down is not None:
            self._cmnd += self._moveSeq(down, "B")
        if left is not None:
            self._cmnd += self._moveSeq(left, "D")
        if right is not None:
            self._cmnd += self._moveSeq(right, "C")

    def _moveSeq(self, dist, cmnd):
        return self.CSI + "{}{}".format(dist, cmnd)

class HideCursor(ANSICode):
    def __init__(self):
        self._cmnd = self.CSI + "?25l"

class ShowCursor(ANSICode):
    def __init__(self):
        self._cmnd = self.CSI + "?25h"

class EraseLine(ANSICode):
    def __init__(self, region):
        assert isinstance(region, EraseRegion)
        self._cmnd = self.CSI + "{}K".format(region.value)

class EraseScreen(ANSICode):
    def __init__(self, region):
        self._cmnd = self.CSI + "{}J".format(region.value)

class Reset(ANSICode):
    def __init__(self):
        """reset the terminal to defaults.  NOTE the 'RIS' command
        does not seem to work, so we just unconditionally set all
        attributes OFF."""
        # output the ANSI 'RIS' sequence, Reset to Initial State
        #sys.stdout.write("\x1bc")
        # output 'all attributes OFF' sequence
        self._cmnd = "\x1b[0m"
        
class GotoXY(ANSICode):
    def __init__(self, x, y):
        self._cmnd = self.CSI + "{};{}H".format(x, y)

class Font(ANSICode):
    def __init__(self, fg=None, bg=None, bold=None, italic=None, underline=None, reverse=None, blink=None):
        self._fg = Colour.DEFAULT
        self._bg = Colour.DEFAULT
        self._bold = False
        self._italic = False
        self._underline = False
        self._reverse = False
        self._blink = False

        if fg is not None:
            self._fg = fg
        if bg is not None:
            self._bg = bg
        if bold is not None:
            self._bold = bold
        if italic is not None:
            self._italic = italic
        if underline is not None:
            self._underline = underline
        if reverse is not None:
            self._reverse = reverse
        if blink is not None:
            self._blink = blink

        if self._bold:
            flags = ";1"
        else:
            flags = ";22"
        if self._italic:
            flags += ";3"
        else:
            flags += ";23"
        if self._underline:
            flags += ";4"
        else:
            flags += ";24"
        if self._reverse:
            flags += ";7"
        else:
            flags += ";27"
        if self._blink:
            flags += ";5"
        else:
            flags += ";25"

        self._cmnd = self.CSI + "{}{}m".format(self._fgColourCode(), flags) + self.CSI + "{}m".format(self._bgColourCode()) 

    def _fgColourCode(self):
        return self.colour2fgCode(self._fg)
       
    def _bgColourCode(self):
        return self.colour2bgCode(self._bg)
   
class Screen(object):
    """Abstracts the terminal window, with the width (as cols) and height (as lines)
    given by the terminal window which launched it.  A screen can have widgets added to
    it and it displays them when asket to refresh.  Currently supported widgets are:
       Simple label (text on one line, has position(x,y) and lenght)
       TextBox (2D text area, has origin(x,y) and size(h,w))
    Position/origin can have NEGATIVE INDICES to offset from the bottom/RHS of screen.
    """
    
    def __init__(self, widgets=None):
        self.cols = int(subprocess.check_output(["tput", "cols"]))
        self.lines = int(subprocess.check_output(["tput", "lines"]))
        self._widgets = widgets
        # we hide the cursor while the widgets are active
        HideCursor().put()
    
    def __enter__(self):
        """method to make this class a 'context manager', i.e. it
        can be used in a with clause and the __exit__ method will
        always be invoked on leaving, even for exceptions."""
        return self
       
    def __exit__(self, etype, value, traceback):
        """method to make this class a 'context manager', i.e. it
        can be used in a with clause and the __exit__ method will
        always be invoked on leaving, even for exceptions."""
        sys.stdout.write(str(Reset()))
        ShowCursor().put()
        GotoXY(self.lines, 1).put()
        return True

    def add_widget(self, widget):
        self._widgets.append(widget)
        self.refresh()

    def refresh(self):
        print(EraseScreen(EraseRegion.ALL))
        for w in self._widgets:
            w.draw()

    def banner(self, string):
        text = ' ' + string + ' '
        left = '=' * int((self.cols-len(text)) / 2)
        #s = left + Font() + text
        size = len(left) + len(text)
        s = left + text
        return Font(fg=Colour.GREEN, bold=True) + s + '='*(self.cols-size) + Font()

class Widget(object):
    """base widget class, has common methods"""
    def __init__(self, x, y):
        self.origin_x = x
        self.origin_y = y

    def reset_font(self):
        """write all attributes off"""
        sys.stdout.write("\x1b[0m")
        
    def goto_origin(self):
        GotoXY(self.origin_x, self.origin_y).put()
        
    def draw(self):
        """virtual method!
        Will be called by screen with cursor already set to origin and all
        text attributes reset."""
        assert False  # WRITE ME IN DERIVED CLASS

class Text(Widget):
    """Simple text label"""
    def __init__(self, x, y, text=""):
        super().__init__(x, y) 
        self._text = text

    def draw(self):
        self.goto_origin()
        self.reset_font()
        sys.stdout.write(self._text)
        sys.stdout.flush()

class StaticListBox(Widget):
    """Static list of text in box (no scrolling,
    logically a list of lines, not single blob
    of text)"""
    def __init__(self, x, y, length, width, initial=None, bg=None):
        super().__init__(x, y) 
        # create list with correct number of lines
        self.length = length
        self.width = width
        self._bg = bg or Colour.DEFAULT
        self._font = Font(fg=Colour.GREEN, bg=self._bg)
        self._lines = initial or []
        self._square_out_lines()

    def _square_out_lines(self):
        """condition lines so that the list
        is correct length, and each line is
        padded out with trailing blanks"""
        self._lines += ["" for l in range(self.length)]
        self._lines = self._lines[:self.length]
        trailing_blanks = ' ' * self.width
        self._lines = [ (s + trailing_blanks)[:self.width] for s in self._lines]

    def draw(self):
        self._font.put()
        offset = 0
        for line in self._lines:
            GotoXY(self.origin_x+offset, self.origin_y).put()
            sys.stdout.write(line)
            offset += 1
        self.reset_font()
        sys.stdout.flush()

def demo():
    l1 = Text(15, 13, "Hello Label")
    l2 = Text(7, 5, "seven, three!")
    l3 = Text(3, 2, Font(fg=Colour.RED, bold=True) + "big, bold and RED")
    tb1 = StaticListBox(7, 33, 7, 12, initial=['big', 'pigs', 'oversized', 'hat', 'with','too','many', 'lines'], bg=Colour.BLUE)
    with Screen([l3, l1, l2, tb1]) as s:
       for i in range(7):
           s.refresh()
           tb1._lines = tb1._lines[1:]
           tb1._lines.append("and a {}".format(i))
           tb1._square_out_lines()
           time.sleep(0.4)

    #print(tb1._lines)
    
if __name__ == '__main__':
    demo()
