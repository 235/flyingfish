import RDF
from flyingfish.utils import modeldump, sparql, str_scalar_or_list
from flyingfish.client import RDFconnection

print "start"
connection = RDFconnection(model="sample_storage", storage="postgresql", startnew=True,
                           options = "host='127.0.0.1',database='ffish',user='root','password=''")
print "connection created"
client = connection.client()
print "connected"

#test_file='./flyingfish/sample-data/tim.rdf'
#uri=RDF.Uri(string="file:"+test_file)
#parser=RDF.Parser('raptor')
#for s in parser.parse_as_stream(uri,uri):
#    client.model.add_statement(s)

print modeldump(client.model)
