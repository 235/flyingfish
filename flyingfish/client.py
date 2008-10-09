import RDF
from model import RDFmodel, shortcut_to_uri
from constants import NAMESPACES
from utilListString import ListString

class RDFconnection:
    def __init__(self, model, storage, startnew, options):
        if startnew: start_new = ",new='yes'"
        else: start_new = ",new='no'"
        
        self.storage = RDF.Storage(storage_name=storage, name=model, options_string=options+start_new)
        self.model = RDF.Model(self.storage)
    
    def client(self):
        return RDFclient(self.model)


class RDFclient:
    def __init__(self, model):
        self.model = model

    def get(self, root_URI, cache = False):
        return RDFmodel(self.model, root_URI, cache)
     
    def type(self, root_type):
        if not root_type:
            return None
        root_type = shortcut_to_uri(root_type)
        qstr = "- [http://www.w3.org/1999/02/22-rdf-syntax-ns#type] [%s]" % (root_type)
        #print "URI %s, query %s" % (self.root_type, qstr) 
        qset = RDF.Query(qstr, query_language="triples") 
        result = []
        for statement in qset.execute(self.model).as_stream():
            result.append(RDFmodel(self.model,statement.subject))
        return result
    
    def query_sparql(self, sparql):
        ''' SPARQL query must return set of "uri" variables '''
        qset = RDF.Query(sparql, query_language="sparql")
        result = ListString()
        for item in qset.execute(self.model):
            result.append(RDFmodel(self.model,item['uri']))         
        return result

    def query(self, root_type, where, prefixes = []):
        sparql = ""
        for pfx in prefixes:
            if NAMESPACES[pfx]:
                sparql += "PREFIX %s: <%s>\n" % (pfx, NAMESPACES[pfx])
            else:
                raise Error
        sparql += "SELECT ?uri WHERE { ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %s . %s }" % (root_type, where)
        #print sparql
        return self.query_sparql(sparql)
    
    def query_triple(self, triple, element = 'object'):
        """ triple - it's a list from 3 elements - subject, predicate, object """
        for i in range(len(triple)):
            if len(triple[i])==0:
                triple[i] = "-"
            else:
                triple[i] = "[" + shortcut_to_uri(triple[i]) + "]"
        qstr = " ".join(triple)
        results = ListString()
        try:
            qset = RDF.Query(qstr, query_language="triples")
            for statement in qset.execute(self.model).as_stream():
                results.append(RDFmodel(self.model, getattr(statement, element)))
        except:
            return results #stay quiet #raise AttributeError, predicate
        return results