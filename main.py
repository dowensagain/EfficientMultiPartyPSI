import protocol
import helpers
import hashes as h
import bloom_filter as bf
import garbled_bloom_filter as gbf

NumPlayers = 3 
PlayerInputSize = 4
SecParam = 40
# Nmaxones = 3182
bitLength = 128
# p = 0.099 # Fraction of messages to use for Cut and Choose
# a = 0.274 # Probability a 1 is chosen by a player
# b = 0.05 # Desired probability of a bloom-filter false-positive

Protocol = protocol.new(NumPlayers, PlayerInputSize, SecParam, bitLength)
Protocol.perform_RandomOT()
Protocol.get_AllPlayersOnes()
Protocol.create_InjectiveFunctions()

Protocol.players[0].create_RandomizedGBF(Protocol.hashes)
Protocol.players[0].create_XOR_sums([ Protocol.players[1], Protocol.players[2] ])
vals0 = Protocol.players[0].create_SummaryValsToShare( Protocol.hashes )

Protocol.players[1].create_RandomizedGBF(Protocol.hashes)
Protocol.players[1].create_XOR_sums([ Protocol.players[1], Protocol.players[2] ])
vals1 = Protocol.players[1].create_SummaryValsToShare( Protocol.hashes )

for i in range(0, len(vals0)):
    for j in range(0, len(vals1)):
        if vals0[i] == vals1[j]:
            print("Intersection at {}".format(vals0[i]))

# Protocol.players[0].create_XOR_sums([ Protocol.players[1], Protocol.players[2] ])
# Protocol.players[1].create_XOR_sums([ Protocol.players[1], Protocol.players[2] ])

# Protocol.players[0].create_GarbledBloomFilter(Protocol.hashes)
# Protocol.players[0].add_InputsToGBF()





# ngbf.add("testing")
# ngbf.add(753)
# ngbf.add("yessir")
# ngbf.add("foobar")
# r = helpers.int_to_string(ngbf.check("testing"))
# r2 = ngbf.check(753)
# r3 = helpers.int_to_string(ngbf.check("yessir"))
# r4 = helpers.int_to_string(ngbf.check("foobar"))

a=1