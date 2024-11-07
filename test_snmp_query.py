from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

# This is a minimal script to test the basic SNMP GET
iterator = getCmd(
    SnmpEngine(),
    CommunityData('public'),
    UdpTransportTarget(('demo.snmplabs.com', 161)),
    ContextData(),
    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
)

errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

if errorIndication:
    print("Error:", errorIndication)
else:
    print("SNMP GET successful:", varBinds)