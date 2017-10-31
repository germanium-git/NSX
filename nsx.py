"""
===================================================================================================
   Author:         Petr Nemec
   Description:    NSX Class definition
   Date:           2017-10-04
===================================================================================================
"""

import requests
from pprint import pprint
from jinja2 import Template
import yaml
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import sys
import getopt

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def getiventories(mypath):
    """
    :param argv: Path to inventory files
    :return:     list of inventories
    """

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    inv_list = []
    for file in onlyfiles:
        inv_list.append(file.split('_')[-1][:-4])
    return inv_list


def seldc(argv):
    """
    :param argv: Command line argumets
    :return:     Name of the inventory file
    """
    inp = ''
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print 'Use this script with inventory parameter'
            print(' -i myvmware - for MyVMware lab ')
            sys.exit()
        elif opt in ("-i"):
            if arg in getiventories(mypath):
                inp = arg
            else:
                print('Invalid argument')
                print('Only these inventories are valid: ', getiventories(mypath))
                sys.exit()
    if not(opts):
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    return inp



def credentials(inputfile):
    """
    :param:	    path to an inventory file
    :return:    tuple with (ip, account, password)
    """
    # Import credentials from YAML file
    with open(inputfile, 'r') as f:
        s = f.read()

    # Read the directory of credentials from file
    nsx_cred = yaml.load(s)

    nsx_ip = raw_input("NSX manager IP [%s]: " % nsx_cred['nsx_ip']) or nsx_cred['nsx_ip']
    account = raw_input("Account [%s]: " % nsx_cred['account']) or nsx_cred['account']
    if 'passw' in nsx_cred:
        passw = getpass.getpass(prompt='Use the stored password or enter new one: ', stream=None) or nsx_cred['passw']
        passw = nsx_cred['passw']
    else:
        passw = 'None'
        while passw == 'None' or passw == '':
            passw = getpass.getpass(prompt='Password: ', stream=None)

    return nsx_ip, account, passw



def createbody(template, vars):
    """
    :param:	    path to a Jinja2 template file and directory of variables
    :return:    The output rendered from the template
    """
    # CREATE Body with Jinja2 template
    with open(template) as f:
        s = f.read()
    template = Template(s)

    # Define XML Body - Global Routing > router ID
    xml_body = template.render(vars)

    return xml_body



class NSX:

    def __init__(self, nsx_ip, login, pswd):
        self.nsx_ip = nsx_ip
        self.login = login
        self.pswd = pswd
        self.headers = {'Content-Type': 'application/xml', 'Accept': "application/json"}


    def getswitches(self):
        """
        :param:
        :return:    It prints out all logical switches
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/2.0/vdn/virtualwires', auth=(self.login, self.pswd),
                             verify=False, headers=self.headers)
            pprint(r.text)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        for i in r.json()['dataPage']['data']:
            print(i['name'], i['objectId'], i['vdnId'])



    def findswitch(self, swname):
        """
        It searches for virtualwire-x and vni associated with a logical switch
        :param:	    Name of the logical switch
        :return:    virtualwire-x and vni referring to the switch
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/2.0/vdn/virtualwires?startindex=0&pagesize=1024',
                             auth=(self.login, self.pswd), verify=False, headers=self.headers)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        switchid=''
        vni = ''
        for i in r.json()['dataPage']['data']:
            if i['name'] == swname:
                switchid = i['objectId'].replace('virtualwire-', '')
                vni = i['vdnId']

        return switchid, vni


    def createsw(self, cfg, tzone):
        """
        It creates new logical switch in a specific transport zone
        :param:	    Name of the logical switch
        :return:    virtualwire-x and vni referring to the switch
        """
        try:
            r = requests.post('https://' + self.nsx_ip + '/api/2.0/vdn/scopes/' + tzone + '/virtualwires', data=cfg,
                              auth=(self.login, self.pswd), verify=False, headers=self.headers)
            pprint(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))


    def delsw(self, switchid):
        """
        It deletes a logical switch
        :param:	    virtualwire-x
        :return:    it prints HTTP return code
        """
        try:
            r = requests.delete('https://' + self.nsx_ip + '/api/2.0/vdn/virtualwires/virtualwire-' + switchid,
                              auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def createedge(self, cfg):
        """
        It creates an edge
        :param:	    xml body of the POST call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.post('https://' + self.nsx_ip + '/api/4.0/edges', data=cfg,
                              auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def getedges(self):
        """
        It retrieves all edges
        :param:
        :return:    Directory of edges; it prints HTTP return code
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges', auth=(self.login, self.pswd),
                             verify=False, headers=self.headers)
            pprint(r.text)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return r.raw()



    def findedge(self, edgename):
        """
        It searches for edge-x associated with an edge
        :param:	    Name of the edge
        :return:    edge-x referring to the edge
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges', auth=(self.login, self.pswd),
                             verify=False, headers=self.headers)
            # pprint(r.text)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        edgeid=''
        for i in r.json()['edgePage']['data']:
            if i['name'] == edgename:
                edgeid = i['id'].replace('edge-', '')

        return edgeid


    def deledge(self, edgeid):
        """
        It deletes an edge
        :param:	    edge-x
        :return:    it prints HTTP return code
        """
        try:
            r = requests.delete('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid,
                                auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def getuplinkip(self, edgeid):
        """
        It gets the IP address assigned to the uplink interface - vnic0
        :param:	    edge-x
        :return:    the ip address, it prints HTTP return code
        """
        ip = 'None'
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid,
                             auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)
            i = r.json()
            if i['vnics']['vnics'][0]['addressGroups']['addressGroups']:
                ip = i['vnics']['vnics'][0]['addressGroups']['addressGroups'][0]['primaryAddress']

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))
            
        return ip


    def cfgbgp(self, cfg, edgeid):
        """
        it configures BGP
        :param:	    edge-x, xml body of the PUT call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/routing/config/bgp',
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def getbgp(self, edgeid):
        """
        It gets the BGP configuration of an edge
        :param:	    edge-x
        :return:    the response body; it prints HTTP return code
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/routing/config/bgp',
                                 auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

            xmlbody = r

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return xmlbody



    def cfgstatic(self, cfg, edgeid):
        """
        it configures Static routing
        :param:	    edge-x, xml body of the PUT call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/routing/config/static',
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def getstatic(self, edgeid):
        """
        It gets the Static routing configuration of an edge
        :param:	    edge-x
        :return:    list of static routes; it prints HTTP return code
        """
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/routing/config/static',
                                 auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)
            routes = r.json()['staticRoutes']['staticRoutes']
            statics = []
            for route in routes:
                old_route = {}
                old_route['vnic'] = int(route['vnic'].encode('ascii','ignore'))
                old_route['next_hop'] = route['nextHop'].encode('ascii','ignore')
                old_route['route'] = route['network'].encode('ascii','ignore')
                old_route['admin_distance'] = int(route['adminDistance'])
                statics.append(old_route)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))

        return statics        


    def cfgglobrouting(self, cfg, edgeid):
        """
        it configures Global routing parameters such as router id
        :param:	    edge-x, xml body of the PUT call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/routing/config/global',
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def cfgha(self, cfg, edgeid):
        """
        it configures HA
        :param:	    edge-x, xml body of the PUT call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/highavailability/config',
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



    def cfgappliances(self, cfg, edgeid):
        """
        WIP - it re-configures appliances of an edge
        :param:	    edge-x, xml body of the PUT call
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/appliances',
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))


    def getappliances(self, edgeid):
        """
        WIP - it gets appliances' configuration of an edge
        :param:	    edge-x
        :return:    it prints HTTP return code
        """
        # It returns haIndex
        try:
            r = requests.get('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/appliances',
                                 auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))


    def cfghaAdminState(self, cfg, edgeid, haindex):
        """
        WIP - it fails over the active HA appliance of and edge
        :param:	    edge-x, xml body of the PUT calll
        :return:    it prints HTTP return code
        """
        try:
            r = requests.put('https://' + self.nsx_ip + '/api/4.0/edges/edge-' + edgeid + '/appliancesi/' + haindex,
                                 data=cfg, auth=(self.login, self.pswd), verify=False, headers=self.headers)
            print(r)

        except requests.exceptions.Timeout as e:
            print('connect - Timeout error: {}'.format(e))
        except requests.exceptions.HTTPError as e:
            print('connect - HTTP error: {}'.format(e))
        except requests.exceptions.ConnectionError as e:
            print('connect - Connection error: {}'.format(e))
        except requests.exceptions.TooManyRedirects as e:
            print('connect - TooManyRedirects error: {}'.format(e))
        except (ValueError, KeyError, TypeError) as e:
            print('connect - JSON format error: {}'.format(e))



