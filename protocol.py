import parameters as pm
import players
import hashes
import bloom_filter as bf
import random_oblivious_transfer as rot
import math
import PySimpleGUI as sg

# Turn all debug prints to print in a window
print = sg.Print

class protocol(object):
    def __init__(self, NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a):
        self.players = []
        self.params = pm.Paramaters(NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a)
        self.create_Players()
        self.hashes = hashes.new(self.params.k)
        self.sumVals = []
    
    def create_Players(self):
        p0 = players.PlayerHub(0, self.params)
        p1 = players.PlayerHub(1, self.params)
        self.players.append(p0)
        self.players.append(p1)

        for i in range(2, self.params.NumPlayers):
            p = players.PlayerSpoke(i, self.params)
            self.players.append(p)
    
    def create_BloomFilters(self):
        for player in self.players:
            player.create_BloomFilter(self.hashes)
            # player.bloom_filter.print("Player {}: ".format(player.id))

    def perform_RandomOT(self):
        sender = self.players[0]
        receivers = []
        for i in range(1, len(self.players)):
            receivers.append(self.players[i])

        self.randomOT = rot.random_ot(sender, receivers)
        self.randomOT.performTransfers()

    def perform_CutandChoose(self):
        for player in self.players:
            for i in range(0, -1):
                player.c_messages.append(player.messages[i])
                totalOnes = 0
                if player.id != 0:
                    for m in player.c_messages:
                        totalOnes += 1 if m.bit == 1 else 0
                    if totalOnes > self.params.Nmaxones:
                        print("Protocol aborted: Player {} has {} ones, which is more than {}".format(player.id, totalOnes, player.params.Nmaxones))
            for i in range(self.params.C, len(player.messages)):
                player.j_messages.append(player.messages[i])

    def create_InjectiveFunctions(self):
        forPrint = ""
        for player in self.players:
            if player.id != 0:
                player.create_InjectiveFunction()
                forPrint += "\nPlayer {}'s Injective function: {}".format(player.id, player.injective_function)
        return forPrint
        
    
    def create_RandomizedGBFs(self):
        for player in self.players[:2]:
            player.create_RandomizedGBF(self.hashes)

    def perform_XORsummation(self):
        Pi = self.players[1:]
        for player in self.players[:2]:
            player.create_XOR_sums(Pi)

    def perform_SummaryValues(self):
        self.sumVals = []
        for player in self.players[:2]:
            self.sumVals.append(player.create_SummaryValsToShare(self.hashes))

    def perform_Output(self):
        forPrint = ""
        output = self.players[1].find_Intersections(self.sumVals[0])
        for player in self.players:
            forPrint += "\nPlayer {}'s input set: {}".format(player.id, player.inputSet)
        forPrint += "\n"
        for index, _ in enumerate(self.sumVals):
            pstr ="["
            for elem in self.sumVals[index]:
                elemm = int.from_bytes(elem, 'big')
                pstr += "{:7.7}..., ".format(str(elemm))
            pstr += "]"
            forPrint += "\nPlayer {}'s summary values: {}".format(index, pstr)
        
        forPrint += "\n\nIntersections found at these values: {}".format(output)
        return forPrint

    def print_PlayerROTTable(self):
        self.randomOT.getAllTransfersFromPlayers()
        forPrint = self.randomOT.printAllTransfers()
        return forPrint
    
    def print_PlayerMessageStats(self):
        forPrint = ""
        for player in self.players:
            ones = player.getTotalOnes()
            ideal = self.params.Not * self.params.a
            forPrint += "\nP{} has {} ones. a * Not: {}".format(player.id, ones, ideal)
        return forPrint


def new(NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a):
        return protocol(NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a)
        