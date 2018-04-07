from library import Library, Slot
import os


class Key(object):
	def __init__(self, normal, shift=None, ctrl=None, padded=None, modifier=None):
		self.normalCode = Padded(normal, padded)
		self.shiftCode = Padded(shift, padded)
		self.ctrlCode = Padded(ctrl, padded)

		self.modifier = modifier

	def __eq__(self, key):
		if not isinstance(key, Key):
			raise ValueError("Not a key")

		return (
			self.normalCode == key.normalCode and
			self.shiftCode  == key.shiftCode  and
			self.ctrlCode   == key.ctrlCode   and
			self.modifier   is key.modifier
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


def Ctrl(key):
	if not isinstance(key, Key):
		raise ValueError("Not a key")
	return Key(key.normalCode, shift=key.shiftCode, ctrl=key.ctrlCode, modifier=Ctrl)

def Shift(key):
	if not isinstance(key, Key):
		raise ValueError("Not a key")
	return Key(key.normalCode, shift=key.shiftCode, ctrl=key.ctrlCode, modifier=Shift)


# Via https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)
class KeyCodes(object):
	# Controls
	Escape        = Key(27                                   )
	Backspace     = Key(8,              ctrl=127             )
	Tab           = Key(9,              ctrl=Padded(148, 0)  )
	Enter         = Key(13,             ctrl=10              )
	Space         = Key(32                                   )
	Insert        = Key(82,             ctrl=146, padded=224 )
	Delete        = Key(83,             ctrl=147, padded=224 )

	# Digits
	One           = Key(49,  shift=33                        )
	Two           = Key(50,  shift=64                        )
	Three         = Key(51,  shift=35                        )
	Four          = Key(52,  shift=36                        )
	Five          = Key(53,  shift=37                        )
	Six           = Key(54,  shift=94                        )
	Seven         = Key(55,  shift=38                        )
	Eight         = Key(56,  shift=42                        )
	Nine          = Key(57,  shift=40                        )
	Zero          = Key(48,  shift=41                        )
	Minus         = Key(45,  shift=95                        )
	Plus          = Key(61,  shift=43                        )

	# Random characters
	BracketLeft   = Key(91,  shift=123, ctrl=27              )
	BracketRight  = Key(93,  shift=125, ctrl=29              )
	Colon         = Key(59,  shift=58                        )
	Quote         = Key(39,  shift=34                        )
	Backtick      = Key(96,  shift=126                       )
	Backslash     = Key(92,  shift=124, ctrl=28              )
	Comma         = Key(44,  shift=60                        )
	Dot           = Key(46,  shift=62                        )
	Slash         = Key(47,  shift=63                        )

	# Functional keys
	F1            = Key(59,  shift=84,  ctrl=94,  padded=0   )
	F2            = Key(60,  shift=85,  ctrl=95,  padded=0   )
	F3            = Key(61,  shift=86,  ctrl=96,  padded=0   )
	F4            = Key(62,  shift=87,  ctrl=97,  padded=0   )
	F5            = Key(63,  shift=88,  ctrl=98,  padded=0   )
	F6            = Key(64,  shift=89,  ctrl=99,  padded=0   )
	F7            = Key(65,  shift=90,  ctrl=100, padded=0   )
	F8            = Key(66,  shift=91,  ctrl=101, padded=0   )
	F9            = Key(67,  shift=92,  ctrl=102, padded=0   )
	F10           = Key(68,  shift=92,  ctrl=103, padded=0   )
	F11           = Key(133, shift=135, ctrl=137, padded=224 )
	F12           = Key(134, shift=136, ctrl=138, padded=224 )

	# Navigation
	Home          = Key(71,             ctrl=119, padded=224 )
	ArrowUp       = Key(72,             ctrl=141, padded=224 )
	PageUp        = Key(73,             ctrl=134, padded=224 )
	ArrowLeft     = Key(75,             ctrl=115, padded=224 )
	ArrowRight    = Key(77,             ctrl=116, padded=224 )
	End           = Key(79,             ctrl=117, padded=224 )
	Down          = Key(80,             ctrl=145, padded=224 )
	PageDown      = Key(81,             ctrl=118, padded=224 )


	@classmethod
	def fromChar(cls, char):
		for name in cls.__dict__:
			key = cls.__dict__[name]
			if not isinstance(key, Key):
				continue

			if char == key.normalCode:
				return key
			elif char == key.shiftCode:
				return Shift(key)
			elif char == key.ctrlCode:
				return Ctrl(key)

		return None


# Letters
for letter in range(ord("a"), ord("z") + 1):
	normal = letter
	shift = letter - ord("a") + ord("A")
	ctrl = letter - ord("a") + 1
	if ctrl in [8, 9, 10, 13]:
		# ^H (Backspace), ^I (Tab), ^J (Ctrl+Enter) or ^M(Enter)
		ctrl = None

	setattr(KeyCodes, chr(shift), Key(normal, shift=shift, ctrl=ctrl))


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


	@Slot("KeyCodes", wrapped=True)
	def KeyCodes(slots):
		return KeyCodes

	@Slot("Ctrl", wrapped=True)
	def Ctrl(slots):
		return Ctrl

	@Slot("Shift", wrapped=True)
	def Shift(slots):
		return Shift