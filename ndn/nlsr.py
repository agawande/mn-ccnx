#!/usr/bin/python

class Nlsr:
    def __init__(self, node):
        self.node = node
        self.routerName = "/%sC1.Router/cs/%s" % ('%', node.name)
        self.confFile = "/tmp/%s/nlsr.conf" % node.name

        # Make directory for log file
        self.logDir = "/tmp/%s/log" % node.name

        node.cmd("mkdir %s" % self.logDir)

        # Configure basic router information in nlsr.conf based on host name
        node.cmd("sudo sed -i 's|router .*|router %s|g' %s" % (self.routerName, self.confFile))
        node.cmd("sudo sed -i 's|log-dir .*|log-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|seq-dir .*|seq-dir %s|g' %s" % (self.logDir, self.confFile))
        node.cmd("sudo sed -i 's|prefix .*netlab|prefix /ndn/edu/%s|g' %s" % (node.name, self.confFile))

    def start(self):
        self.node.cmd("nlsr -d")
