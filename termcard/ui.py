import os
import re
import unicodedata


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


ANSI_RE = re.compile(r"\033\[[0-9;]*m")
RLE = "\u202B"
PDF = "\u202C"
ZERO_WIDTH = {"\u200e", "\u200f", "\u202a", "\u202b", "\u202c", "\u202d", "\u202e"}


def _strip(s):
    return ANSI_RE.sub("", s)


def disp_width(s):
    w = 0
    for ch in _strip(s):
        if ch in ZERO_WIDTH or unicodedata.combining(ch):
            continue
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def _has_rtl(s):
    for ch in _strip(s):
        cp = ord(ch)
        if (0x0590 <= cp <= 0x05FF or 0x0600 <= cp <= 0x06FF
                or 0x0700 <= cp <= 0x074F or 0x0750 <= cp <= 0x077F
                or 0x08A0 <= cp <= 0x08FF or 0xFB1D <= cp <= 0xFDFF
                or 0xFE70 <= cp <= 0xFEFF):
            return True
    return False


def _wrap_rtl(text):
    return RLE + text + PDF if _has_rtl(text) else text


def color(text, c):
    return f"{c}{text}{C.RESET}"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def width():
    try:
        return min(os.get_terminal_size().columns, 80)
    except OSError:
        return 80


def banner():
    w = width()
    title = "TERMCARD"
    pad = (w - 2 - len(title)) // 2
    print(color("+" + "=" * (w - 2) + "+", C.CYAN))
    print(color("|", C.CYAN) + " " * pad + color(title, C.BOLD + C.WHITE)
          + " " * (w - 2 - pad - len(title)) + color("|", C.CYAN))
    print(color("+" + "=" * (w - 2) + "+", C.CYAN))
    print()


def header(text):
    w = width()
    print(color("-" * w, C.BLUE))
    print(color(" ", C.BLUE) + _wrap_rtl(text))
    print(color("-" * w, C.BLUE))


def success(text): print(color("  [+] ", C.GREEN) + _wrap_rtl(text))
def error(text):   print(color("  [!] ", C.RED)   + _wrap_rtl(text))
def warn(text):    print(color("  [~] ", C.YELLOW) + _wrap_rtl(text))
def info(text):    print(color("  [i] ", C.BLUE)  + _wrap_rtl(text))


def prompt(text):
    return input(color("  ", C.YELLOW) + _wrap_rtl(text))


def pause(msg="Press Enter to continue..."):
    input(color("  ", C.GRAY) + _wrap_rtl(msg))


def box(lines, border_color=C.WHITE, title=None, min_width=0):
    line_w = [disp_width(l) for l in lines]
    content_w = max(line_w, default=0)
    if title:
        content_w = max(content_w, disp_width(title))
    w = max(content_w + 4, disp_width(title or "") + 4 if title else 0, min_width)
    w = min(w, width() - 2)
    inner_w = w - 4

    if title:
        remaining = max(w - 2 - disp_width(title) - 1, 0)
        print(color("+ ", border_color)
              + color(_wrap_rtl(title), border_color + C.BOLD)
              + color(" " + "-" * remaining + "+", border_color))
    else:
        print(color("+" + "-" * (w - 2) + "+", border_color))

    for line, lw in zip(lines, line_w):
        pad = max(inner_w - lw, 0)
        plain = _strip(line)
        if _has_rtl(plain):
            body = " " * pad + RLE + plain + PDF
        else:
            body = plain + " " * pad
        print(color("| ", border_color) + body + color(" |", border_color))

    print(color("+" + "-" * (w - 2) + "+", border_color))
