from channel_sim import BinarySymmetricChannel
from gilbert import GilbertModel
import time
import threading


def generateParityBit(byte):
    parityBit = False
    while byte:
        parityBit = not parityBit
        byte = byte & (byte - 1)

    return int(parityBit)


class Sender:
    def __init__(self, ackWaitTime, winSize):
        self._ackReceived = True
        self._ackSequence = 0
        self._ackWaitTime = ackWaitTime
        self.winSize = winSize
        self.base = 0
        self.nextSeqNum = 0
        self.sentPackets=0

    def __call__(self, buff,sequenceCounter,nextSeqNum):
        self.sendPacket(buff,sequenceCounter,nextSeqNum)
        time.sleep((nextSeqNum-self.base)*10)###
        print(buff)

    def openConnection(self, receiver, channel):
        self._connection = Connection(self, receiver, channel)

    # brak sprawdzania poprawnosci ACK, receiver nie nadaje nic innego
    def receiveACK(self, ackFrame, seqNumber):
        if (seqNumber == self.base):
            self._ackReceived = True

    def sendDataBSC(self, inputFilename):
        with open(inputFilename) as inputFile:
            buff = inputFile.read()
        sequenceCounter = 0

        while (self.nextSeqNum < self.base + self.winSize and self.sentPackets<len(buff)):
            threading.Thread(target=self, args=(buff[self.sentPackets],sequenceCounter, self.nextSeqNum)).start()
            self.nextSeqNum += 1
            self.sentPackets += 1
            if (self.nextSeqNum == self.base + self.winSize):
                time.sleep(self._ackWaitTime)
                if (self._ackReceived):
                    self.base+=1
                    #self._ackReceived=False
                    sequenceCounter = sequenceCounter ^ 1
                else:
                    self.nextSeqNum -= self.winSize
                    self.sentPackets -= self.winSize


    def sendDataGilbert(self, inputFilename):
        with open(inputFilename) as inputFile:
            buff = inputFile.read()
        sequenceCounter = 0

        while (self.nextSeqNum < self.base + self.winSize and self.sentPackets < len(buff)):
            threading.Thread(target=self, args=(buff[self.sentPackets], sequenceCounter, self.nextSeqNum)).start()
            self.nextSeqNum += 1
            self.sentPackets += 1
            if (self.nextSeqNum == self.base + self.winSize):
                time.sleep(self._ackWaitTime)
                if (self._ackReceived):
                    self.base += 1
                    # self._ackReceived=False
                    sequenceCounter = sequenceCounter ^ 1
                else:
                    self.nextSeqNum -= self.winSize
                    self.sentPackets -= self.winSize



    def sendPacket(self, buff,sequenceCounter,nextSeqNum):
        primitiveFrame = PrimitiveFrame(sequenceCounter % 2, ord(buff))
        self._connection.writeFrame(primitiveFrame,nextSeqNum)


class Receiver:
    def __init__(self, winSize):
        self._sequenceCounter = 0
        self.sentCounter = 0
        self.winSize = winSize
        self.bytes = []

    def receiveFrame(self, primitiveFrame, seqNumber):
        if (primitiveFrame.check(self._sequenceCounter % 2)):
          #  self.bytes.append(chr(primitiveFrame.payload()))
            self.writeOutput(primitiveFrame.payload)
            self.sentCounter+=1
            self._connection.writeACK(PrimitiveFrame.makeAckFrame(), seqNumber)
            self._sequenceCounter = self._sequenceCounter ^ 1

       # if (self.sentCounter == self.winSize):
       #     self.writeOutput( bytes)
       #    self.sentCounter = 0
       #     self.bytes.clear()

    def acceptConnection(self, connection):
        self._connection = connection
        self._outputFile = open("outputFile", "w")

    def writeOutput(self, bytes):
        try:
            self._outputFile.write(chr(bytes))
        except OSError as os:
            print("Operating system error")


# abstrakcja polaczenia miedzy Sender a Receiver, poprzez channel
class Connection:
    def __init__(self, sender, receiver, channel):
        self._sender = sender
        self._receiver = receiver
        self._receiver.acceptConnection(self)
        self._channel = channel

    def __call__(self, primitiveFrame, seqNumber):
        self.writeFrame(primitiveFrame, seqNumber)

    def writeACK(self, ackFrame, seqNumber):
        self._sender.receiveACK(self._channel.transmitPrimitiveFrame(ackFrame), seqNumber)

    def writeFrame(self, primitiveFrame, seqNumber):
        self._receiver.receiveFrame(self._channel.transmitPrimitiveFrame(primitiveFrame), seqNumber)


# ACK to 0 w payload, sequenceBit oraz 1 w parityBit
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
        if (generateParityBit(self.payload) != self.parityBit or self.sequenceBit != expectedSequenceBit):
            return False
        return True


fileName = input("Input file name(in pwd): ")

flowEfficiency = input("Flow efficiency(decimal): ")
flipToGood = input("Flip to good state chance(decimal): ")
flipToWrong = input("Flip to bad state chance(decimal): ")
#bitFlipChance = input("Flip to bad state chance(decimal): ")

#bscInstance = BinarySymmetricChannel(float(bitFlipChance))

gilbertInstance = GilbertModel(float(flowEfficiency),float(flipToGood),float(flipToWrong))

sender = Sender(0.08,5)

#sender.openConnection(Receiver(5), bscInstance)
sender.openConnection(Receiver(5), gilbertInstance)

#sender.sendDataBSC(fileName)
sender.sendDataGilbert(fileName)