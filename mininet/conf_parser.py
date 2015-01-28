import ConfigParser, re

class confCCNHost():

    def __init__(self, name, app='', uri_tuples='', cpu=None, cores=None, cache=None, radius=None, angle=None):
        self.name = name
        self.app = app
        self.uri_tuples = uri_tuples
        self.cpu = cpu
        self.cores = cores
	self.cache = cache
	self.radius = radius
	self.angle = angle

    def __repr__(self):
        return 'Name: ' + self.name + ' App: ' + self.app + ' URIS: ' + str(self.uri_tuples) + ' CPU:' + str(self.cpu) + ' Cores:' +str(self.cores) + ' Cache: ' + str(self.cache) + ' Radius: ' + str(self.radius) + ' Angle: ' + str(self.angle)

class confCCNLink():

    def __init__(self,h1,h2,linkDict=None):
        self.h1 = h1
        self.h2 = h2
        self.linkDict = linkDict

    def __repr__(self):
        return 'h1: ' + self.h1 + ' h2: ' + self.h2 + ' params: ' + str(self.linkDict)

def parse_hosts(conf_arq):
    'Parse hosts section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    hosts = []

    items = config.items('nodes')
	
	#makes a first-pass read to hosts section to find empty host sections
    for item in items:
	name = item[0]
	rest = item[1].split()
	if len(rest) == 0:
		config.set('nodes', name, '_')
	#updates 'items' list
    items = config.items('nodes')

	#makes a second-pass read to hosts section to properly add hosts
    for item in items:

        name = item[0]

        rest = item[1].split()

        app = rest.pop(0)

        uris = rest
        uri_list=[]
        cpu = None
        cores = None
	cache = None
	radius = None
	angle = None

        for uri in uris:
            if re.match("cpu",uri):
                cpu = float(uri.split('=')[1])
            elif re.match("cores",uri):
                cores = uri.split('=')[1]
	    elif re.match("cache",uri):
		cache = uri.split('=')[1]
	    elif re.match("mem",uri):
		mem = uri.split('=')[1]
	    elif re.match("radius",uri):
		radius = float(uri.split('=')[1])
	    elif re.match("angle",uri):
		angle = float(uri.split('=')[1])
            else:
                uri_list.append((uri.split(',')[0],uri.split(',')[1]))

        hosts.append(confCCNHost(name , app, uri_list,cpu,cores,cache,radius,angle))

    return hosts

def parse_links(conf_arq):
    'Parse links section from the conf file.'
    arq = open(conf_arq,'r')

    links = []

    while True:
        line = arq.readline()
        if line == '[links]\n':
            break

    while True:
        line = arq.readline()
        if line == '':
            break

        args = line.split()
	
	#checks for non-empty line
	if len(args) == 0:
		continue

        h1, h2 = args.pop(0).split(':')

        link_dict = {}

        for arg in args:
            arg_name, arg_value = arg.split('=')
            key = arg_name
            value = arg_value
            if key in ['bw','jitter','max_queue_size']:
                value = int(value)
            if key in ['loss']:
                value = float(value)
            link_dict[key] = value

        links.append(confCCNLink(h1,h2,link_dict))


    return links
