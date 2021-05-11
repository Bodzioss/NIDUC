import random
import time


class GilbertModel:
    def __init__(self, flowEfficiency, flipToGood, flipToBad):
        self.flowEfficiency = flowEfficiency
        self.flipToGood = flipToGood
        self.flipToBad = flipToBad
        self.state = 0
        random.seed()

    def _distortByte(self, byte):
        distortMask = 0b00000000
        for i in range(0, 7):
            distortMask = 0b00000000
            if (random.random() <= self.flowEfficiency):
                distortMask = 1 << i
                byte = (byte ^ distortMask)  # negacja bitu bajtu, na pozycji i
        return byte

    def _distortPrimitiveFrame(self, primitiveFrame):
        self.tryState()
        print(self.state)
        if (self.state):
            if (random.random() <= self.flowEfficiency):
                primitiveFrame.sequenceBit = primitiveFrame.sequenceBit ^ 1

            if (random.random() <= self.flowEfficiency):
                primitiveFrame.parityBit = primitiveFrame.parityBit ^ 1

            primitiveFrame.payload = self._distortByte(primitiveFrame.payload)

        return primitiveFrame

    def transmitPrimitiveFrame(self, primitiveFrame):
        time.sleep(0.043)
        return self._distortPrimitiveFrame(primitiveFrame)

    def tryState(self):
        if (self.state):
            if (random.random() <= self.flipToBad):
                self.state = 0
        else:
            if (random.random() <= self.flipToGood):
                self.state = 1
