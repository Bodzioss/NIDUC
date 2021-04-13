from channel_sim import BinarySymmetricChannel
import time
import threading

def generateParityBit(byte):
	
	parityBit = False
	while byte:
		parityBit = not parityBit
		byte = byte & (byte - 1)

	return int(parityBit)

class Sender:
	def __init__(self, ackWaitTime):
		self._ackReceived = False
		self._ackSequence = 0
		self._ackWaitTime = ackWaitTime

	def openConnection(self, receiver, channel):
		self._connection = Connection(self, receiver, channel)

	#brak sprawdzania poprawnosci ACK, receiver nie nadaje nic innego
	def receiveACK(self, ackFrame):
		self._ackReceived = True

	def sendData(self, inputFilename):
		with open(inputFilename) as inputFile:
			sequenceCounter = 0
			buff = inputFile.read(1)
			while(buff != ""):
				while(self._ackReceived == False):
					primitiveFrame = PrimitiveFrame(sequenceCounter % 2, ord(buff))
					threading.Thread(target=self._connection, args=(primitiveFrame,)).start()
					time.sleep(self._ackWaitTime)

				self._ackReceived = False
				sequenceCounter = sequenceCounter ^ 1
				buff = inputFile.read(1)
				
class Receiver:
	def __init__(self):
		self._sequenceCounter = 0

	def receiveFrame(self, primitiveFrame):
		if(primitiveFrame.check(self._sequenceCounter % 2)):
			self.writeOutput(primitiveFrame.payload)
			self._connection.writeACK(PrimitiveFrame.makeAckFrame())
			self._sequenceCounter = self._sequenceCounter ^ 1

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

	def __call__(self, primitiveFrame):
		self.writeFrame(primitiveFrame)

	def writeACK(self, ackFrame):
		self._sender.receiveACK(self._channel.transmitPrimitiveFrame(ackFrame))

	def writeFrame(self, primitiveFrame):
		self._receiver.receiveFrame(self._channel.transmitPrimitiveFrame(primitiveFrame))
		
#ACK to 0 w payload, sequenceBit oraz 1 w parityBit
class PrimitiveFrame:
	def __init__(self, sequenceBit, byte):
		self.sequenceBit = sequenceBit
		self.parityBit = generateParityBit(byte)
		self.payload = byte

	def makeAckFrame():
		frame = PrimitiveFrame(0, 0)
		frame.parityBit = 1
		return frame

	def check(self, expectedSequenceBit):
		if(generateParityBit(self.payload) != self.parityBit or self.sequenceBit != expectedSequenceBit):
			return False
		return True

fileName = input("Input file name(in pwd): ")

bitFlipChance = input("Crossover chance(decimal): ")

bscInstance = BinarySymmetricChannel(float(bitFlipChance))

sender = Sender(0.08)

sender.openConnection(Receiver(), bscInstance)

sender.sendData(fileName)
