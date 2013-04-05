from CubeDataStream import CubeDataStream

# A dictionary of version num and client connectors
client_connectors = {}

def get_client_connector(data):
    cds = CubeDataStream(data)
    
    message_type = cds.getint()
    mycn = cds.getint()
    protocol_version = cds.getint()
    
    if protocol_version in client_connectors:
        return client_connectors[protocol_version]
    else:
        raise Exception("Unknown protocol version: {}".format(protocol_version))
        
    return None
