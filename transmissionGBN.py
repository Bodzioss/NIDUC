import zlib

from channel_sim import BinarySymmetricChannel
from gilbert import GilbertModel
import time
import threading

class Controller():
    def __init__(self):
        self.expectedSeq=0

def generateParityBit(byte):
    parityBit = False
    while byte:
        parityBit = not parityBit
        byte = byte & (byte - 1)

    return int(parityBit)


class Sender():
    def __init__(self, ackWaitTime, winSize):
        self._ackReceived = False
        self._ackSequence = 0
        self._ackWaitTime = ackWaitTime
        self.sleepTime=0.2
        self.winSize = winSize
        self.base = 0
        self.nextSeqNum = 0
        self.sentPackets=0
        self.timeout=0
        self.sequenceCounter=0
        self.end=0
        self.getPackets=0
        self.isInterupted=0

    def __call__(self, buff):
        while(True):
            if(self.sentPackets > len(buff)):
                self.end=1
                break
            while (self.nextSeqNum < self.winSize and self.sentPackets <= len(buff)):
                print("\nWysłano "+str(buff[self.sentPackets]))
                threading.Thread(target=self.sendPacket, args=(buff[self.sentPackets], self.sequenceCounter, self.sentPackets)).start()
                threading.Thread(target=self.checkTimeout, args=(self._ackWaitTime, self.sentPackets)).start()
                self.nextSeqNum += 1
                if (self.sentPackets < len(buff)):
                    self.sentPackets += 1
                time.sleep(self.sleepTime)


    def openConnection(self, receiver, channel):
        self._connection = Connection(self, receiver, channel)

    # brak sprawdzania poprawnosci ACK, receiver nie nadaje nic innego
    def receiveACK(self, ackFrame, seqNumber):
        print("recived ack " + str(seqNumber) +" "+ str(self.base)+" ")
        if(seqNumber==self.base):
            self._ackReceived = True


    def sendDataBSC(self, inputFilename):
        with open(inputFilename) as inputFile:
            buff = inputFile.read()
        threading.Thread(target=self, args=(buff,)).start()
        while (self.end == 0):
            while (self._ackReceived == False and self.timeout == 0 and self.end == 0):
                a = 0
            if (self._ackReceived):
                self.base += 1
                self.getPackets += 1
                self._ackReceived = False
                self.sequenceCounter = self.sequenceCounter ^ 1
                self.nextSeqNum-=1
                if len(buff)-self.getPackets<self.winSize:
                    self.winSize=len(buff)-self.sentPackets
                if self.getPackets==len(buff):
                    self.sentPackets+=1
            else:
                self.isInterupted = self.nextSeqNum-1
                self.nextSeqNum = 0
                self.sentPackets = self.base
                self.timeout = 0


    def sendDataGilbert(self, inputFilename):
        with open(inputFilename) as inputFile:
            buff = inputFile.read()
        threading.Thread(target=self, args=(buff,)).start()
        while (self.end == 0):
            while (self._ackReceived == False and self.timeout == 0 and self.end == 0):
                a = 0
            if (self._ackReceived):
                self.base += 1
                self.getPackets += 1
                self._ackReceived = False
                self.sequenceCounter = self.sequenceCounter ^ 1
                self.nextSeqNum -= 1
                if len(buff) - self.getPackets < self.winSize:
                    self.winSize = len(buff) - self.sentPackets
                if self.getPackets == len(buff):
                    self.sentPackets += 1
            else:
                self.isInterupted = self.nextSeqNum - 1
                self.nextSeqNum = 0
                self.sentPackets = self.base
                self.timeout = 0



    def checkTimeout(self,waitTime,sentPackets):
        time.sleep(waitTime)
        if(sentPackets==self.getPackets and self.isInterupted == 0):
            self.timeout=1
        else:
            if(self.isInterupted>0):
                self.isInterupted-=1


    def sendPacket(self, buff,sequenceCounter,nextSeqNum):
        primitiveFrame = PrimitiveFrame(sequenceCounter % 2, ord(buff))
        self._connection.writeFrame(primitiveFrame,nextSeqNum)


class Receiver:
    def __init__(self):
        self._sequenceCounter = 0

    def receiveFrame(self, primitiveFrame, seqNumber):
        if (primitiveFrame.check(self._sequenceCounter % 2)):
            if(seqNumber==controller.expectedSeq):
                self.writeOutput(primitiveFrame.payload)
                controller.expectedSeq+=1
            self._connection.writeACK(PrimitiveFrame.makeAckFrame(), seqNumber)
            self._sequenceCounter = self._sequenceCounter ^ 1



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
        x= chr(byte)
        x=x.encode('utf-8')
        self.crc32=zlib.crc32(x)
    def makeAckFrame():
        frame = PrimitiveFrame(0, 0)
        frame.parityBit = 1
        return frame

    def check(self, expectedSequenceBit):
        if (self.crc32 != zlib.crc32((chr(self.payload)).encode('utf-8'))):
            return False
        return True


fileName = input("Input file name(in pwd): ")

flowEfficiency = input("Flow efficiency(decimal): ")
flipToGood = input("Flip to good state chance(decimal): ")
flipToWrong = input("Flip to bad state chance(decimal): ")
#bitFlipChance = input("Flip to bad state chance(decimal): ")

#bscInstance = BinarySymmetricChannel(float(bitFlipChance))
gilbertInstance = GilbertModel(float(flowEfficiency),float(flipToGood),float(flipToWrong))
controller=Controller()
sender = Sender(5,3)

#sender.openConnection(Receiver(), bscInstance)
sender.openConnection(Receiver(), gilbertInstance)

 #sender.sendDataBSC(fileName)
sender.sendDataGilbert(fileName)
