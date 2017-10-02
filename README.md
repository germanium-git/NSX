# NSX

NSX edge deployment by using REST API calls initiated by python scripts. There are a few scripts which may help you with

  - Instantiation of an edge
  - High Availability
  - Static routing
  - BGP routing

### Dependencies
These are the python modules needed to run the scrips. Install those by using pip
* jinja2
* yaml
* reqests


### How to use this project
##### Inventory files
All scripts in this repository are ready-to-use. All input parameters including the credentials to authenticate with NSX manager are specified by *.yaml files stored in the input folder. The password is stored there as an optional parameter which can be omited. The password can always be passed as the input parameter at the beginning of script execution.
Update the variables in the file inputs/nsx_mylab.yml and rename it to some other name consisting of two parts such as inputs/nsx_mylab.yml. Note the "mylab" part between underscore and .yml will be used as the argument for specifying the NSX manager. There's the argument -i put when script is being executed. In case of using for instance *_mylab.yml convention the scrips will be executed with -i mylab parameter.

```sh
$ cat inputs/nsx_mylab.yml
---
  # Specify credentials
  nsx_ip: 1.2.3.4
  account: admin
  # Password is optional. Comment it and enter the password in input dialog.
  passw: my_pass                # update it with valid password
  banner: The vSphere in myLab will be modified
  # Specify the Transport zone in which logical switches will be created
  vdnScopeId: vdnscope-1        # put an appropriate Transport zone here
```

##### nsx_switch_create.py
This script creates a logical switch in a specific Transport zone.
No additional parametres are needed but only the name of the logical switch to be created. The transport zone need to be specified prior executing the script in the inputs/nsx_mylab.yml file.
```sh
$ nsx_switch_create.py -i mylab
```

##### nsx_switch_findid.py
This script resolves the name of a logical switch to so called virtualwire-x id the switch refers to. No input parameters are needed.
```sh
$ nsx_switch_findid.py -i mylab
```

##### nsx_edge_create.py
It creates a new instance of the NSX edge following the specified parametres such as:
- SSH access for monitoring and troubleshooting purposes
- BGP routing
- Static routing
- High Availability mode
- Resource pools & datastores where the edge should be deployed.
- Uplink interface - a distributed port group
- Inside interface - logical switch

The parametres are specified in either pe_primary_mylab.yml or pe_secondary_mylab.yml. The specification may be chosen by entering p/s paramter during th einput dialog.

```sh
$ nsx_edge_create.py -i mylab
```

```sh
(rest) nemedpet@TFI-LAB-SERVER-MGMT-01:~/NSX⟫ cat inputs/pe_primary_mylab.yml
---
  username: admin
  passw: Pass123456789!

  localAS: 65001
  remoteAS: 65002
  bgp_md5: someMD5key
  neighbor: 10.0.0.1

  datacenterMoid: datacenter-21 # the datacenter ID
  banner: The NSX in myLAB will be modified

  # Specify the primary Provider Edge
  name: ABC-EDGE-01
  p_resourcePoolId: domain-x   # the resource pool the primary instance should use
  p_datastoreId: datastore-x   # the datastore the primary instance should use
  s_resourcePoolId: domain-y   # the resource pool the secondary instance should use
  s_datastoreId: datastore-y   # the datastore the secondary instance should use

  ha: True
  uplink:
    address: 10.255.0.2
    netmask: 255.255.255.252
  interconnect:
    address: 172.16.10.1
    netmask: 255.255.255.248
  static:
    route1:
      prefix: 192.168.10.1/24
      next-hop: 172.16.10.3
      admin-distance: 1
    route2:
      prefix: 0.0.0.0/0
      next-hop: 172.16.10.2
      admin-distance: 250

  defaultRoute: False
```

More info on how to use the scripts and a few demo examples can be found on https://germanium.cz

