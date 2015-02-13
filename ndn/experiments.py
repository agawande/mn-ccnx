#!/usr/bin/python

from ndn.nlsr import Nlsr

import time

class HyperbolicExperiment:

    def __init__(self, net, nodes, convergenceTime, nPings):
        self.net = net
        self.nodes = nodes
        self.convergenceTime = convergenceTime
        self.nPings = nPings

    def run(self):
        for host in self.net.hosts:

            # Schedule convergence check
            #host.cmd("./checkFIB "+ self.nodes + " " + host.name + " " + str(self.convergenceTime) + " &")

            # Set strategy
            host.cmd("nfdc set-strategy /ndn/edu ndn:/localhost/nfd/strategy/ncc &")

            # Start ping server
            host.cmd("ndnpingserver /ndn/edu/"+str(host)+" > ping-server &")

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


	# Checking for convergence
	for host in self.net.hosts:
            statusRouter = host.cmd("nfd-status -b | grep /ndn/edu/%C1.Router/cs/")  # This check will be after the time out
            statusPrefix = host.cmd("nfd-status -b | grep /ndn/edu/")
            list_node = self.nodes.split(",")
            convergence = True
            for node in list_node:
                    if "/ndn/edu/%C1.Router/cs/"+node not in statusRouter:
                        convergence = False
                    if str(host) != node and "/ndn/edu/"+node not in statusPrefix:
                        convergence = False

	    host.cmd("echo " + str(convergence) + " > result &")


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
                #host.cmd("sudo kill `ps aux | grep nfd| grep sudo | grep csu | awk '/csu.conf/ { print $2}'`")
		print("bringing csu down")
		#pid = host.cmd("head -n 1 nfd-pid")
		#print(len(pid))
		#print(host.nfd.nfdpid.pid)
		host.cmd("sudo kill " + host.nfd.nfdpid + " &")
		#print(host.nfd.nfdpid.terminate())
		#print(host.cmd("ps aux | grep nfd | wc -l"))
		#host.nfd.nfdpid.terminate()
                break

        # CSU is down for 2 minutes
        time.sleep(120)

        # Bring CSU back up
        for host in self.net.hosts:
            if host.name == "csu":
		print("csu up")
                host.cmd("sudo nfd --config csu.conf 2>> csu2.log &")
                time.sleep(2)
                host.cmd("nrd --config csu.conf 2>> csu-nrd.log &")
                time.sleep(2)
                host.cmd("nlsr -d")
                host.cmd("nfdc set-strategy /ndn/edu ndn:/localhost/nfd/strategy/ncc &")
                #host.cmd("nfdc set-strategy /ndn/edu/"+str(host)+" ndn:/localhost/nfd/strategy/ncc > strategy &")
                host.cmd("ndnpingserver /ndn/edu/" + str(host) + " > ping-server &")
		#print(host.cmd("ps aux | grep nfd | wc -l"))
                break

        # Collect pings for 1 minute
        time.sleep(60)
