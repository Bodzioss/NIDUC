import random

class BinarySymmetricChannel:
	def __init__(self, p):
		self.p = p
		random.seed()

	#def openConnection(self, source, destination):

	def distortChar(self, char):
		return chr(self.distortByte(ord(char)))#ord zwraca int ktory mozna traktowac jako bajt, tak dlugo jak nie zostanie przekroczona maksymalna wartosc bajtu

	def distortByte(self, byte):
		distortMask = 0b00000000
		for i in range(0, 7):
			distortMask = 0b00000000
			if(random.random() <= self.p):
				distortMask = 1 << i
				byte = (byte ^ distortMask)#negacja bitu bajtu, na pozycji i

		return byte

	def transmitByte(self, byte):
		return self.distortByte(byte)

	def transmitString(self, message):
		listOfChars = [self.distortChar(letter) for letter in message]
		
		returnString = "".join(listOfChars)

		return returnString