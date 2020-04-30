import protocol
import helpers
import hashes as h
import bloom_filter as bf
import garbled_bloom_filter as gbf
import PySimpleGUI as sg

# Turn all debug prints to print in a window
# print = sg.Print

sg.change_look_and_feel('DarkBlue2') 

NumPlayers = 3 
PlayerInputSize = 20 # 10
SecParam = 40
bitLength = 128

# These parameters are meant for illustration and fast execution
# they are not considered secure or optimal
Nmaxones = 80 # 40
p = 0.3 # 0.25 # Fraction of messages to use for Cut and Choose
a = 0.27 # 0.25 # Probability a 1 is chosen by a player

perform_protocol = sg.ReadButton('Perform Protocol', font=('Segoe UI', 12), key='-RUN-')
stepTracker = 0
Protocol = None

layout = [ 
            [sg.Text('Efficient Multi-Party PSI', size=(50,1), justification='left', font=('Segoe UI', 20))],
            [sg.Text('By Malia Kency and John Owens', font=('Segoe UI', 13))],
            [ 
                sg.Text('Number of players:'), sg.Input('3', key='-NUMPLAYERS-')
            ],
            [ 
                sg.Text('Constant protocol parameters that will be used:', font=('Segoe UI', 12), size=(55,1)),
                sg.Text('Parameters that will be calculated:', font=('Segoe UI', 12)),
            ],
           
            [ sg.Listbox(
                    values = [
                        'NumPlayers      = Total number of players, P\N{LATIN SUBSCRIPT SMALL LETTER I}',
                        'PlayerInputSize = Size of the players input sets',
                        'SecParam (kappa)   = Security Paramter = 40 as described',
                        'bitLength       = length of random generated strings = 128 as described',
                        'Nmaxones        = Max number of ones a player is allowed after cut-and-choose',
                        'p               = Percentage of total messages to be used for cut-and-choose',
                        'a               = Sampling weight of 1s vs. 0s for every P\N{LATIN SUBSCRIPT SMALL LETTER I}'],
                    size=(85,8), font=('Consolas', 10)),
                sg.Listbox(
                    values = [
                        'Not       = Total number of Random Oblivious Transfer',
                        'Nbf       = Size of the player\'s bloom_filter. Calculated on initalization',
                        'k         = Number of hash functions to use. Calculated on initalization',
                        'm\N{LATIN SUBSCRIPT SMALL LETTER h}        = The number of 1s a player chooses',
                        'gamma     = Verifies the correct relationship between p, k, m\N{LATIN SUBSCRIPT SMALL LETTER h}',
                        'gammaStar = Verifies the correct relationship between p, k, Not'],
                        size=(85,8), font=('Consolas', 10))
            ],
            [sg.Output(key='-OUTPUT-', size=(300, 20), font=('Consolas', 10))],
            [perform_protocol],
            [sg.Button('Exit', font=('Segoe UI', 12))],
         ]

window = sg.Window('Private Set Intersection', layout, default_element_size=(50,1) )

while True:
    # Read the event that happened and the values dictionary
    event, values = window.read()
    # print(event, values)
    if event in (None, 'Exit'): 
        break
    if event == '-RUN-':
        perform_protocol.Update("Button clicked {} times".format(stepTracker) )
        if stepTracker == 0:
            window['-OUTPUT-'].update('')
        stepTracker += 1
        if stepTracker == 1:
            # Initialize the protocol by calculating parameters,
            # creating the players, and generating random inputs
            # Note: at least 1 shared value is guaranteed
            NumPlayers = int(values['-NUMPLAYERS-'], 10)
            Protocol = protocol.new(NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a)
            print("k = {}".format(Protocol.params.k))
            print("Not = {}".format(Protocol.params.Not))
            print("gamma = {}".format(Protocol.params.gamma))
            print("gammaStar = {}".format(Protocol.params.gammaStar))
            print("\nSimulating players joining protocol. Total: {}".format(Protocol.params.NumPlayers))
        
        if stepTracker == 2:
            # Perform the random oblivious transfer simulation for P0...Pt
            print("\nPerforming Random Oblivious Transfer simulation. {} transfers in total:".format(Protocol.params.Not))
            Protocol.perform_RandomOT()
            output = Protocol.print_PlayerROTTable()
            print(output)
            print("\nCounting each player's \"1s\":")
            output = Protocol.print_PlayerMessageStats()
            print(output)
        elif stepTracker == 3:
            # Perform cut-and-choose simulation for P0...Pt
            print("\nPerforming Cut and Choose simulation. Size of c: {}. Size of j: {}".format(Protocol.params.C, Protocol.params.Not - Protocol.params.C))
            Protocol.perform_CutandChoose()
        elif stepTracker == 4:
            # Create bloom filters for P1...Pt
            print("\nCreating Bloom Filters. BF length: {}".format(Protocol.params.Nbf))
            Protocol.create_BloomFilters()
        elif stepTracker == 5:
            # Create P1...Pt's injective functions
            print("\nCreating injective functions for every Pi:")
            output = Protocol.create_InjectiveFunctions()
            print(output)

            # Instantiate P0's and P1's rGBF objects
            print("\nCreating randomized GBF for every Pi")
            Protocol.create_RandomizedGBFs()

            # P0 performs XOR summation on its own j_messages[injective_func] where bit=1
            # P1 performs XOR summation on all P1...Pt's j_messages[injective_func] where bit = P1...Pt's choice
            Protocol.perform_XORsummation()

            # P0 calculates summary values for all elements of its input set
            # P1 calculates summary values for all elements of its input set (Every P1...Pt input values)
            Protocol.perform_SummaryValues()

            # P1 receives P0s summary values, compares them to its own
            # Intersections are recorded and output
            output = Protocol.perform_Output()
            print(output)
            stepTracker = 0
window.close()