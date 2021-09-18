import sys, getopt

class Configurations():

    N_AGENTS_DEFAULT = 1
    SPEED_DEFAULT = 1

    def __init__(self, argv):
        self.speed = Configurations.SPEED_DEFAULT
        self.n_agents = Configurations.N_AGENTS_DEFAULT
        try:
            opts, _ = getopt.getopt(argv,"hs:v:n:",["help", "server=", "speed=", "n_agents="])
            for opt, val in opts:
                if opt in ('-h', "--help"):
                    self.usage()
                    sys.exit()
                elif opt in ("-v", "--speed"):
                    self.speed = val
                elif opt in ("-s", "--server"):
                    self.server = val
                elif opt in ("-n", "--n_agents"):
                    self.n_agents = val
        except getopt.GetoptError as err:
           print(err)
           self.usage()
           sys.exit(2)

    def usage(self):
        print('''
usage: main.py [options] 

    -h, --help                  print help message and exits

Required:
    -s, --server=SERVER         define the address of the XMPP SERVER

Optinal:
    -n, --agents=N_AGENTS       set the number of agents (N_AGENTS) to be executed, default is the 
                                maximum number available in the dataset file, default is 1
    -v, --speed=SPEED           set the SPEED of the simulation, default is 1 (speed formula:
                                time_per_period_in_seconds / SPEED, the time per period is defined
                                in the dataset)
''')

