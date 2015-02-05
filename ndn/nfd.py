#!/usr/bin/python

import time

class Nfd:
    def __init__(self, node):
        self.node = node
        self.isRunning = False

        # Create home directory for a node
        node.cmd("cd /tmp && mkdir %s" % node.name)
        node.cmd("cd %s" % node.name)

        self.homeFolder = "/tmp/%s" % node.name
        self.confFile = "%s/%s.conf" % (self.homeFolder, node.name)
        self.logFile = "%s/%s.log" % (self.homeFolder, node.name)
        self.sockFile = "/var/run/%s.sock" % node.name
        self.ndnFolder = "%s/.ndn" % self.homeFolder
        self.clientConf = "%s/client.conf" % self.ndnFolder

        # Copy file that checks FIB
        node.cmd("sudo cp ~/mn-ndn/ccn_utils/checkFIB %s/checkFIB" % self.homeFolder)

        # Copy nfd.conf file from mn-ndn/ccn_utils to the node's home
        node.cmd("sudo cp ~/mn-ndn/ccn_utils/nfd.conf %s" % self.confFile)

        # Open the conf file and change socket file name
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.confFile))

        # Make NDN folder
        node.cmd("sudo mkdir %s" % self.ndnFolder)

        # Copy the client.conf file and change the unix socket
        node.cmd("sudo cp ~/mn-ndn/ccn_utils/client.conf.sample %s" % self.clientConf)
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.clientConf))

        # Copy NLSR configuration file before changing home folder
        node.cmd("sudo cp ~/mn-ndn/ccn_utils/nlsr.conf %s/nlsr.conf" % self.homeFolder)

        # Change home folder
        node.cmd("export HOME=%s" % self.homeFolder)

    def start(self):
        self.node.cmd("sudo nfd --config %s 2>> %s &" % (self.confFile, self.logFile))
        time.sleep(2)

        self.node.cmd("nrd --config %s 2>> %s &" % (self.confFile, self.logFile))
        time.sleep(2)

        self.isRunning = True

    def stop(self):
        if self.isRunning is True:
            self.node.cmd('nfd-stop')

        self.isRunning = False

    def setStrategy(self, name, strategy):
        node.cmd("nfdc set-strategy %s ndn:/localhost/nfd/strategy/%s" % (name, strategy))
        time.sleep(0.5)
