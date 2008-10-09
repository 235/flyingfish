import RDF
from flyingfish.utils import modeldump, sparql, str_scalar_or_list
from flyingfish.client import RDFconnection

connection = RDFconnection(model="sample_storage", storage="postgresql", startnew=False,
                           options = "host='127.0.0.1',database='ffish',user='root','password=''")
client = connection.client()

print modeldump(client.model)
