from channel_sim import BinarySymmetricChannel
			
message = input("String to transmit:\n")

bscInstance = BinarySymmetricChannel(0.01)

receivedMessage = bscInstance.transmitString(message)

print("|\n|\n|\n" + receivedMessage)