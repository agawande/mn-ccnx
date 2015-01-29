#!/usr/bin/python

import time

class HyperbolicExperiment:

    def __init__(self, net, nodes, convergenceTime, nPings):
                self.net = net
                self.nodes = nodes
                self.convergenceTime = convergenceTime
                self.nPings = nPings

    def run(self):
        for host in self.net.hosts:

            # Start NLSR
            host.cmd("nlsr -d")

            # Schedule convergence check
            host.cmd("./checkFIB "+ self.nodes + " " + host.name + " " + str(self.convergenceTime) + " &")

            # Set strategy
            #host.cmd("nfdc set-strategy /ndn/edu ndn:/localhost/nfd/strategy/ncc &")

            # Start ping server
            host.cmd("ndnpingserver /ndn/edu/"+str(host)+" &")

            # Create folder to store ping data
            host.cmd("mkdir ping-data")

            # Start ndndump
            #host.cmd("ndndump > dump."+str(host)+" &")

            # Start collecting nfd-status
            #host.cmd("./nfdstatus > status."+str(host) +" &")

        # Wait for convergence time period before starting ping
        print "Waiting " + str(self.convergenceTime) + " seconds for convergence..."
        time.sleep(self.convergenceTime)
        print "...done"

        for host in self.net.hosts:
            for other in self.net.hosts:
                # Do not ping self
                if host.name != other.name:
                    # Use "&" to run in background and perform parallel pings
                    print "Scheduling ping(s) from %s to %s" % (host.name, other.name)
                    host.cmd("ndnping -c "+ str(self.nPings) + " /ndn/edu/" + other.name + " > ping-data/" + other.name + ".txt &")
                    time.sleep(0.2)

        # Collect pings for 1 minute
        time.sleep(60)

class FailureExperiment(HyperbolicExperiment):

    def __init__(self, net, nodes, convergenceTime):
        HyperbolicExperiment.__init__(self, net, nodes, convergenceTime, 300)

    def run(self):
        # Set up experiment (NLSR, pings, etc.)
        HyperbolicExperiment.run(self)

        # Bring down CSU
        for host in self.net.hosts:
            if host.name == "csu":
                host.cmd("sudo kill `ps aux | grep nfd| grep sudo | grep csu | awk '/csu.conf/ { print $2}'`")
                break

        # CSU is down for 2 minutes
        time.sleep(120)

        # Bring CSU back up
        for host in self.net.hosts:
            if host.name == "csu":
                host.cmd("sudo nfd --config csu.conf &")
                time.sleep(1)
                host.cmd("sudo nrd --config csu.conf &")
                time.sleep(1)
                host.cmd("nlsr -d")
                host.cmd("nfdc set-strategy /ndn/edu ndn:/localhost/nfd/strategy/ncc &")
                #host.cmd("nfdc set-strategy /ndn/edu/"+str(host)+" ndn:/localhost/nfd/strategy/ncc > strategy &")
                host.cmd("ndnpingserver /ndn/edu/" + host.name + " &")
                break

        # Collect pings for 1 minute
        time.sleep(60)
