# flyingfish

## <a name="This_project_about:"></a>This project about:[](#This_project_about:)

*   **Python** language
*   **RDF**-databases ([Redland](http://librdf.org/))
*   **mapping** RDF data to Python classes

Flyingfish is written and tested as a part of Django-based site, used in [ExtMem.com](http://www.extmem.com/) project. 

## <a name="Functionality"></a>Functionality[](#Functionality)

The lib binds Redland (RDF triple storage) to hi-level python classes. Current version is typeless and doesn't care about RDF-schema. 


```python
from flyingfish.client import RDFconnection
#to inticialize DB run once with startnew=True
connection = RDFconnection(model="test_storage1", storage="postgresql", startnew=False,
                           options = "host='127.0.0.1',database='rdfdb',user='root','password=''")
client = connection.client()


URI = "http://www.pleso.net/rdf/#"
#create named resource
root = client.get(URI + 'root')

person1 = client.get(URI + 'p1')
#attribute access to statements, useful for rendering in templates
person1.rdf_type = 'foaf:Person'
person1.foaf_name = 'Alex'
person1.ext_tag = 'developer'

person2 = client.get(URI + 'p2')
person2['rdf:type'] = 'foaf:Person'
person2['foaf:name'] = 'Nick'
person2['ext:tag'] = 'developer'
person2['ext:tag'] = 'designer'

person1['foaf:knows'] = person2

root.ext_all = URI + 'p1'
root['ext:all'] = person2

from flyingfish.utils import modeldump
print 'FULL DUMP \n', modeldump(client.model)

#get resource  by URI
resource = client.get(URI + 'p1')
print 'INTROSPECT RESOURCE BY URI \n',resource.cache_introspect()

people = client.query('foaf:Person', '?uri foaf:name "Nick"',["foaf"])
print 'SIMPLE QUERY RESULT \n', people
```

## Output: 
```
FULL DUMP 
Statement: {[http://www.pleso.net/rdf/#p1], [http://www.w3.org/1999/02/22-rdf-syntax-ns#type], [http://xmlns.com/foaf/0.1/Person]}
Statement: {[http://www.pleso.net/rdf/#p1], [http://xmlns.com/foaf/0.1/name], "Alex"}
Statement: {[http://www.pleso.net/rdf/#p1], [http://extmem.com/rdfs/ext/tag], "developer"}
Statement: {[http://www.pleso.net/rdf/#p2], [http://www.w3.org/1999/02/22-rdf-syntax-ns#type], [http://xmlns.com/foaf/0.1/Person]}
Statement: {[http://www.pleso.net/rdf/#p2], [http://xmlns.com/foaf/0.1/name], "Nick"}
Statement: {[http://www.pleso.net/rdf/#p2], [http://extmem.com/rdfs/ext/tag], "developer"}
Statement: {[http://www.pleso.net/rdf/#p2], [http://extmem.com/rdfs/ext/tag], "designer"}
Statement: {[http://www.pleso.net/rdf/#root], [http://extmem.com/rdfs/ext/all], "http://www.pleso.net/rdf/#p1"}
Statement: {[http://www.pleso.net/rdf/#root], [http://extmem.com/rdfs/ext/all], (r1229485140r7596r1)}
Statement: {[http://www.pleso.net/rdf/#p1], [http://xmlns.com/foaf/0.1/knows], (r1229485451r7881r1)}


INTROSPECT RESOURCE BY URI 
http://www.pleso.net/rdf/#p1 {
foaf:knows:                                     (r1229485451r7881r1)
rdf:type:                                       http://xmlns.com/foaf/0.1/Person
ext:tag:                                        developer
foaf:name:                                      Alex

}
SIMPLE QUERY RESULT 
http://www.pleso.net/rdf/#p2
```

### <a name="Links:"></a>Links:[](#Links:)

*   [http://librdf.org/](http://librdf.org/)
*   [Redland RDF Language Bindings - Python API Reference](http://librdf.org/docs/pydoc/RDF.html)
