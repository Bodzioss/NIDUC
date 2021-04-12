from channel_sim import BinarySymmetricChannel
import time

class Sender:
	def __init__(self):
		self._ackReceived = False
		self._ackWaitTime = 0.08

	def openConnection(self, receiver, channel):
		self._connection = Connection(self, receiver, channel)

	def receiveACK(self, ackFrame):
		self._ackReceived = True

	def sendData(self, inputFilename):
		with open(inputFilename) as inputFile:
			sequenceCounter = 0
			buff = inputFile.read(1)
			while(buff != ""):
				while(self._ackReceived == False):
					primitiveFrame = PrimitiveFrame(sequenceCounter % 2, ord(buff))
					self._connection.writeFrame(primitiveFrame)
					time.sleep(self._ackWaitTime)

				self._ackReceived = False
				++sequenceCounter
				buff = inputFile.read(1)
				
class Receiver:
	def __init__(self):
		self._sequenceCounter = 0

	def receiveFrame(self, primitiveFrame):
		if(primitiveFrame.check(self._sequenceCounter % 2)):
			self.writeOutput(primitiveFrame.payload)
			self._connection.writeACK(PrimitiveFrame.makeAckFrame())
			++self._sequenceCounter

	def acceptConnection(self, connection):
		self._connection = connection
		self._outputFile = open("outputFile", "w")

	def writeOutput(self, byte):
		try:
			self._outputFile.write(chr(byte))
		except OSError as os:
			print("Operating system error")


#abstrakcja polaczenia miedzy Sender a Receiver, poprzez channel
class Connection:
	def __init__(self, sender, receiver, channel):
		self._sender = sender
		self._receiver = receiver
		self._receiver.acceptConnection(self)
		self._channel = channel

	def writeACK(self, ackFrame):
		self._sender.receiveACK(self._channel.transmitPrimitiveFrame(ackFrame))

	def writeFrame(self, primitiveFrame):
		self._receiver.receiveFrame(self._channel.transmitPrimitiveFrame(primitiveFrame))
		
#aby nie symulowac czterech warstw OSI, ACK to 0 w payload, sequenceBit
#oraz 1 w parityBit
class PrimitiveFrame:
	def __init__(self, sequenceBit, byte):
		self.sequenceBit = sequenceBit
		self.parityBit = byte % 2
		self.payload = byte

	def makeAckFrame():
		frame = PrimitiveFrame(0, 0)
		frame.parityBit = 1
		return frame

	def check(self, expectedSequenceBit):
		if(self.payload % 2 != self.parityBit or self.sequenceBit != expectedSequenceBit):
			return False
		return True

fileName = input("Input file name(in pwd): ")

bitFlipChance = input("Crossover chance(decimal): ")

bscInstance = BinarySymmetricChannel(float(bitFlipChance))

sender = Sender()

sender.openConnection(Receiver(), bscInstance)

sender.sendData(fileName)