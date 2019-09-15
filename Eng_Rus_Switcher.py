import ctypes
from ctypes import wintypes
import time
import keyboard
import pyperclip

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE = 0  # CONSTANT
INPUT_KEYBOARD = 1  # CONSTANT
INPUT_HARDWARE = 2  # CONSTANT

KEYEVENTF_EXTENDEDKEY = 0x0001  # CONSTANT
KEYEVENTF_KEYUP = 0x0002  # CONSTANT
KEYEVENTF_UNICODE = 0x0004  # CONSTANT
KEYEVENTF_SCANCODE = 0x0008  # CONSTANT

MAPVK_VK_TO_VSC = 0  # CONSTANT

# msdn.microsoft.com/en-us/library/dd375731
VK_CTRL = 0x11 # CONSTANT
VK_C = 0x43 # CONSTANT
VK_V = 0x56 # CONSTANT

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD),
                ("_input", _INPUT))


LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args


user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT,  # nInputs
                             LPINPUT,  # pInputs
                             ctypes.c_int)  # cbSize


# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def CtrlC():
    """
    press ctrl and c;
    up ctrl and c
    """
    PressKey(VK_CTRL)  # Press CTRL
    PressKey(VK_C)  # PRESS C
    ReleaseKey(VK_CTRL)  # Up CTRL
    ReleaseKey(VK_C)  # UP C
def CtrlV():
    """
    press ctrl and c;
    up ctrl and c
    """
    PressKey(VK_CTRL)  # Press CTRL
    PressKey(VK_V)  # PRESS C
    ReleaseKey(VK_CTRL)  # Up CTRL
    ReleaseKey(VK_V)  # UP C
def textToArray(text):
    """
    'abca' -> ['a', 'b', 'c', 'a']
    :param text: string
    :return: array
    """
    output = []
    for i in range(len(text)):
        output.append(text[i])
    return(output)
def keySwitch(text, before, after):
    """
    "Ghbdtn" -> "Привет"
    :param text: string
    :param before: list
    :param after: list
    :return: string
    """
    out = []
    words = text.split()
    for i in range(len(words)):  # replace symbols to same key place symblol form other alphabet
        for j in range(len(words[i])):
            symb = words[i][j]
            if symb in before:
                symbIndex = before.index(symb)
                out.append(after[symbIndex])
            else:
                out.append(symb)
        if i != len(words): out.append(' ')
    return ''.join(out)



ENG = textToArray("qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?") # CONSTANT
RUS = textToArray("йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,") # CONSTANT

if __name__ == "__main__":
    while True: # endless loop
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('q'): # conditions
            CtrlC() # Call Ctrl C Event
            time.sleep(0.15) # Waits 0.15 sec
            text = pyperclip.paste() #cope to variable form buffer
            try:
                result = keySwitch(text, ENG, RUS) if text.split()[0][0] in ENG else keySwitch(text, RUS, ENG)
                pyperclip.copy(result)   # copy result to buffer
            except:
                print('Incorrect values')
            CtrlV()  # Call Ctrl V Event
