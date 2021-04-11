from channel_sim import BinarySymmetricChannel

#nadajacy reprezentuje plik
class Sender:
	def __init__(self, inputFileName):
		self._inputFileName = inputFileName

	def readInput(self):
		inputString = ""
		with open(self._inputFileName) as inputFile:
			inputString = inputFile.read()

		return inputString

class Receiver:
	def __init__(self, outputFileName):
		self._outputFileName = outputFileName
		self._receiverBuffer = ""

	def receive(self, primitiveFrame):
		charPayload = chr(primitiveFrame.payload)
		self._receiverBuffer = self._receiverBuffer + charPayload

	def writeOutput(self):
		with open(self._outputFileName, "w") as outputFile:
			outputFile.write(self._receiverBuffer)

#abstrakcja polaczenia miedzy Sender a Receiver, poprzez channel
class Connection:
	def __init__(self, sender, receiver, channel):
		self._sender = sender
		self._receiver = receiver
		self._channel = channel

	def transferData(self):
		senderInput = self._sender.readInput()
		senderInputCharList = [char for char in senderInput]
		iterator = 0
		for char in senderInputCharList:
			primitiveFrame = PrimitiveFrame(iterator % 2, ord(char))
			transferedData = self._channel.transmitPrimitiveFrame(primitiveFrame)
			self._receiver.receive(transferedData)
			++iterator
		self._receiver.writeOutput()



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

fileName = input("Input file name(in pwd): ")

bscInstance = BinarySymmetricChannel(0.01)

Connection(Sender(fileName), Receiver("output.txt"), bscInstance).transferData()