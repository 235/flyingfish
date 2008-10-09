import RDF
from constants import NAMESPACES, DICT_DELIMITER, ATTR_DELIMITER
from utilListString import ListString

def uri_to_shortcut(uri):
    ''' convert URI to internal shortcuts-style like foaf:knows'''
    uri = str(uri)  # hey, but convert RDF.Node to string by yourself!
    for prefix, ns_uri in NAMESPACES.iteritems():
        if uri.startswith(ns_uri):
            return uri.replace(ns_uri, prefix + DICT_DELIMITER, 1)
    return uri  #no match

def shortcut_to_uri(shortcut):
    ''' convert internal shortcuts-style to full URI'''
    if shortcut is None: 
        return ''
    for prefix, ns_uri in NAMESPACES.iteritems():
        if shortcut.startswith(prefix + DICT_DELIMITER):
            return shortcut.replace(prefix + DICT_DELIMITER, ns_uri, 1)
    return shortcut     #no match


class RDFmodel:
    ''' Type-less RDF mapper class. '''
    # All properties should be declared beforehand - to avoid superimpose by RDF-predicates
    model = None
    root_URI = None
    cache = None
    cached = False
       
    def __init__(self, model, root_URI, cache = False):
        ''' takes Redland model and URI of RDF object to map. '''
        self.model = model
        if type(root_URI) is RDF.Node and root_URI.is_resource():   #a trick :\ literal type shouldn't be here
            self.root_URI = str(root_URI.uri)    
        else:
            self.root_URI = str(root_URI)
        if cache:
            self.cache_checkup()
      
    def cache_object(self):
        ''' it's preliminary cache - dumps RDF-object to python dictionary:
            all predicates&object to given root_URI subject
            useful only for objects up to hundreds relations, should be substituted in future'''
        if self.root_URI is None:   #can not query blank nodes 
            return
        try:
            qstr = "[%s] - -" % (self.root_URI) #prepare triple-type query
            #print "URI %s, query %s" % (self.root_URI, qstr) 
            qset = RDF.Query(qstr, query_language="triples")
            #construct cache - dictionary with a predicates as keys, values are lists for multiply statements 
            self.cache = {}
            for statement in qset.execute(self.model).as_stream():
                #need to convert from RDF.Node to string shortcuts - we cann't lookup dictionary by it
                predicate =  uri_to_shortcut(statement.predicate.uri)  #(statement.predicate)
                #if self.cache.has_key(predicate):
                #    if type(self.cache[predicate]) is list:
                #        self.cache[predicate].append(RDFmodel(self.model,statement.object))  #do not cache derivative models
                #    else:
                #        self.cache[predicate] = [self.cache[predicate], RDFmodel(self.model,statement.object)]
                #else:
                #    self.cache[predicate] = RDFmodel(self.model,statement.object)
                
                if self.cache.has_key(predicate):
                    self.cache[predicate].append(RDFmodel(self.model,statement.object))
                else:
                    self.cache[predicate] = ListString()
                    self.cache[predicate].append(RDFmodel(self.model,statement.object))
                    
            self.cached = True  #set up cache
        except: #bad query
            return
        
    def cache_checkup(self):
        '''silly cache-controller'''
        if not self.cached:
            self.cache_object()
    
    def cache_introspect(self, INDENT = 40):
        ''' to introspect what is inside in the cached RDF-object
            INDENT - the constant to format left-column(predicates) width'''
        self.cache_checkup()
        output = "%s {\n" % self.root_URI
        if not self.cached: return output + "}"
        for p, o in self.cache.iteritems():        
            indent = INDENT-len(str(p))
            output += "%s:%s\t" % (p, " "*indent) 
            if type(o) is list:
                output += "( "
                for item in o:
                    output += "%s, " % item
                output += ")\n"
            else:
                output += "%s\n" % o
        output += "\n}"
        return output    
    
    def predicates(self):
        ''' returns a list of all predicates''' 
        self.cache_checkup()
        return self.cache.keys()
    
    def __len__(self):
        self.cache_checkup()
        objects = 0
        for p, o in self.cache.iteritems():
            if type(o) is list: objects += len(o)
            else: objects += 1
        return objects
        
    def __getitem__(self, predicate):
        ''' rmodel["foaf:knows"] '''
        ####HACK FOR DJANGO! - it looks in dict before attr, need to convert:
        ####HACK#2 - predicate could be unicode - convert to sting
        predicate = str(predicate).replace(ATTR_DELIMITER, DICT_DELIMITER, 1)
        
        #print "GETTING %s" % predicate
        if self.cached:
            if not self.cache.has_key(predicate):
                #print "CACHE - no hit: %s" % predicate
                return None #stay quiet #raise AttributeError, predicate
            #print "CACHE %s => %s" % (predicate, self.cache[predicate])
            return self.cache[predicate]              
        else:
            #print "REQUEST"
            qstr = "[%s] [%s] -" % (self.root_URI, shortcut_to_uri(predicate)) 
            results = ListString()
            try:
                qset = RDF.Query(qstr, query_language="triples")
                for statement in qset.execute(self.model).as_stream():
                    results.append(RDFmodel(self.model, statement.object))
                    #print RDFmodel(self.model, statement.object)
            except:
                #print qstr
                return results #stay quiet #raise AttributeError, predicate
            return results
            
    def __getattr__(self, predicate):
        ''' rmodel.foaf_knows '''
        predicate_delimited = predicate.replace(ATTR_DELIMITER, DICT_DELIMITER, 1)
        return self.__getitem__(predicate_delimited)
    
    def has_attribute(self, predicate):
        ''' quite silly so far - only with cache '''
        self.cache_checkup()
        if self.cache.has_key(predicate):
            return True
        return False
    
    def __setitem__(self, predicate, object):
        ''' rmodel["foaf:knows"] = object '''
        #need better check between URI and Literal
        if shortcut_to_uri(object) == object:
            node_object = RDF.Node(object)
        else:
            node_object = RDF.Node(uri_string=shortcut_to_uri(object))
        statement = RDF.Statement(RDF.Node(uri_string=self.root_URI),
                                  RDF.Node(uri_string=shortcut_to_uri(predicate)),
                                  node_object)
        if not self.model.contains_statement(statement):
            self.model.append(statement)
            #print 'Appended: ', repr(statement)
            self.cached = False     #silly cache control        
    
    def __setattr__(self, predicate, object):
        ''' rmodel.foaf_knows = object '''
        #do not use self.__dict__ - it'll show only run-time created attrs
        if RDFmodel.__dict__.has_key(predicate):  
            self.__dict__[predicate] = object
        else:
            predicate_delimited = predicate.replace(ATTR_DELIMITER, DICT_DELIMITER, 1)
            self.__setitem__(predicate_delimited, object)
            
    def __delitem__(self, predicate):
        ''' del rmodel["foaf:knows"] '''
        predicate = shortcut_to_uri(predicate)
        qstr = "[%s] [%s] -" % (self.root_URI, shortcut_to_uri(predicate))
        qset = RDF.Query(qstr, query_language="triples")
        for statement in qset.execute(self.model).as_stream():
            del self.model[statement]
        self.cached = False     #silly cache control
        
    def __delattr__(self, predicate):
        ''' del rmodel.foaf_knows '''
        predicate_delimited = predicate.replace(ATTR_DELIMITER, DICT_DELIMITER, 1)
        self.__delitem__(predicate_delimited)

    def delete(self):
        ''' Delete all object statements. Redland doesn't delete literals/URIs, only connections '''
        for p in self.predicates():
            self.__delitem__(p)
                
    def __str__(self):
        return str(self.root_URI)
    
    def __unicode__(self):
        return unicode(self.root_URI)
    
    def __repr__(self):
        return self.cache_introspect()
    
    #Dirty hacks for Django template system. It needs this variable, it need this call! It's the way templates resolve variables
    alters_data=False #The template system wont execute a method if the method has alters_data=True set
    def __call__(self):
        #print "Executing %s" % self.root_URI
        return self
    
    def __eq__(self, value):
        if str(self.root_URI) == str(value):
            return True
        else:
            return False
        
    
    def keys(self): 
        self.cache_checkup()
        return self.cache.keys()
    def items(self): 
        self.cache_checkup()
        return self.cache.items()  
    def values(self): 
        self.cache_checkup()
        return self.cache.values()

    
    #TODO: is_list_value as_str as_list 