from library import Library
import os


class Char(object):
	def __init__(self, normal, shift=None, ctrl=None, padded=None, modifier=None):
		self.normalCode = Padded(normal, padded)
		self.shiftCode = Padded(shift, padded)
		self.ctrlCode = Padded(ctrl, padded)

		self.modifier = modifier

	def __eq__(self, char):
		if not isinstance(char, Char):
			raise ValueError("Not a char")

		return (
			self.normalCode == char.normalCode and
			self.shiftCode  == char.shiftCode  and
			self.ctrlCode   == char.ctrlCode   and
			self.modifier   is char.modifier
		)

class Padded(object):
	def __init__(self, code, padded):
		if isinstance(code, Padded):
			self.code = code.code
			self.padded = code.padded
		else:
			self.code = code
			self.padded = padded

	def __eq__(self, code):
		if not isinstance(code, Padded):
			raise ValueError("Not a code")

		return self.code == code.code and self.padded == code.padded


def Ctrl(char):
	if not isinstance(char, Char):
		raise ValueError("Not a char")
	return Char(char.normalCode, shift=char.shiftCode, ctrl=char.ctrlCode, modifier=Ctrl)

def Shift(char):
	if not isinstance(char, Char):
		raise ValueError("Not a char")
	return Char(char.normalCode, shift=char.shiftCode, ctrl=char.ctrlCode, modifier=Shift)


# Via https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)
class KeyCodes(object):
	# Controls
	Escape        = Char(27                                   )
	Backspace     = Char(8,              ctrl=127             )
	Tab           = Char(9,              ctrl=Padded(148, 0)  )
	Enter         = Char(13,             ctrl=10              )
	Space         = Char(32                                   )
	Insert        = Char(82,             ctrl=146, padded=224 )
	Delete        = Char(83,             ctrl=147, padded=224 )

	# Digits
	One           = Char(49,  shift=33                        )
	Two           = Char(50,  shift=64                        )
	Three         = Char(51,  shift=35                        )
	Four          = Char(52,  shift=36                        )
	Five          = Char(53,  shift=37                        )
	Six           = Char(54,  shift=94                        )
	Seven         = Char(55,  shift=38                        )
	Eight         = Char(56,  shift=42                        )
	Nine          = Char(57,  shift=40                        )
	Zero          = Char(48,  shift=41                        )
	Minus         = Char(45,  shift=95                        )
	Plus          = Char(61,  shift=43                        )

	# Random characters
	BracketLeft   = Char(91,  shift=123, ctrl=27              )
	BracketRight  = Char(93,  shift=125, ctrl=29              )
	Colon         = Char(59,  shift=58                        )
	Quote         = Char(39,  shift=34                        )
	Backtick      = Char(96,  shift=126                       )
	Backslash     = Char(92,  shift=124, ctrl=28              )
	Comma         = Char(44,  shift=60                        )
	Dot           = Char(46,  shift=62                        )
	Slash         = Char(47,  shift=63                        )

	# Functional keys
	F1            = Char(59,  shift=84,  ctrl=94,  padded=0   )
	F2            = Char(60,  shift=85,  ctrl=95,  padded=0   )
	F3            = Char(61,  shift=86,  ctrl=96,  padded=0   )
	F4            = Char(62,  shift=87,  ctrl=97,  padded=0   )
	F5            = Char(63,  shift=88,  ctrl=98,  padded=0   )
	F6            = Char(64,  shift=89,  ctrl=99,  padded=0   )
	F7            = Char(65,  shift=90,  ctrl=100, padded=0   )
	F8            = Char(66,  shift=91,  ctrl=101, padded=0   )
	F9            = Char(67,  shift=92,  ctrl=102, padded=0   )
	F10           = Char(68,  shift=92,  ctrl=103, padded=0   )
	F11           = Char(133, shift=135, ctrl=137, padded=224 )
	F12           = Char(134, shift=136, ctrl=138, padded=224 )

	# Navigation
	Home          = Char(71,             ctrl=119, padded=224 )
	ArrowUp       = Char(72,             ctrl=141, padded=224 )
	PageUp        = Char(73,             ctrl=134, padded=224 )
	ArrowLeft     = Char(75,             ctrl=115, padded=224 )
	ArrowRight    = Char(77,             ctrl=116, padded=224 )
	End           = Char(79,             ctrl=117, padded=224 )
	Down          = Char(80,             ctrl=145, padded=224 )
	PageDown      = Char(81,             ctrl=118, padded=224 )


	@classmethod
	def fromChar(cls, key):
		for name in cls.__dict__:
			char = cls.__dict__[name]
			if not isinstance(char, Char):
				continue

			if key == char.normalCode:
				return char
			elif key == char.shiftCode:
				return Shift(char)
			elif key == char.ctrlCode:
				return Ctrl(char)

		return None


# Letters
for letter in range(ord("a"), ord("z") + 1):
	normal = letter
	shift = letter - ord("a") + ord("A")
	ctrl = letter - ord("a") + 1
	if ctrl in [8, 9, 10, 13]:
		# ^H (Backspace), ^I (Tab), ^J (Ctrl+Enter) or ^M(Enter)
		ctrl = None

	setattr(KeyCodes, chr(shift), Char(normal, shift=shift, ctrl=ctrl))


def waitKey():
	result = None
	if os.name == "nt":
		import msvcrt
		result = msvcrt.getch()
	else:
		import termios
		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		try:
			result = sys.stdin.read(1)
		except IOError:
			pass
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

	return result

class KeyPress(Library):
	def beforeLoop(self, instances):
		self.key = None
		self.instances = instances

	def loop(self, instances):
		if self.key is None:
			key = ord(waitKey())
			if key == 224 or key == 0:
				# This means that another key follows
				padded = key
				key = ord(waitKey())
				key = KeyCodes.fromChar(Padded(key, padded))
			else:
				key = KeyCodes.fromChar(Padded(key, None))

			self.key = key

		if self.key == Ctrl(KeyCodes.C):
			raise KeyboardInterrupt

	def getKey(self):
		if self.key is None:
			self.loop(self.instances)
		return self.key