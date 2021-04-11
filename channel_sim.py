import random

class BinarySymmetricChannel:
	def __init__(self, p):
		self.p = p
		random.seed()

	def _distortChar(self, char):
		return chr(self.distortByte(ord(char)))
		#ord zwraca int ktory mozna traktowac jako bajt, dopoki
		#nie zostanie przekroczona maksymalna wartosc bajtu

	def _distortByte(self, byte):
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
		listOfChars = [self.distortChar(char) for char in message]
		
		returnString = "".join(listOfChars)

		return returnString

	def _distortPrimitiveFrame(self, primitiveFrame):
		if(random.random() <= self.p):
			primitiveFrame.sequenceBit = primitiveFrame.sequenceBit ^ 1
		
		if(random.random() <= self.p):
			primitiveFrame.parityBit = primitiveFrame.parityBit ^ 1
		
		primitiveFrame.payload = self._distortByte(primitiveFrame.payload)

		return primitiveFrame

	def transmitPrimitiveFrame(self, primitiveFrame):
		return self._distortPrimitiveFrame(primitiveFrame)
