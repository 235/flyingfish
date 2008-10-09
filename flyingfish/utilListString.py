from constants import NAMESPACES, DICT_DELIMITER, ATTR_DELIMITER

class ListString(list):
    """ Modified List
        You could do with this=ListString():
            - refer this as usual List
            - call str(this), unicode(this) with better formating
            - this.as_string() same to str(this)
            - this.as_list() same to this  (!!! Dummy method)
            - this.as_is() will return None|Object|List depending on content    
            - this.is_empty() - True if we have no elements
            - this.is_string() - True if we have exactly 1 item
            - this.is_list() - True if we have more than 1 item
    """
    
    def __call__(self, *args):
        return self #list(self)
   
    def __str__(self):
        """ With some better output formating """
        #could be better, without copying ...
        data = list(self)
        result = ""
        splitter = ", "
        empty = "-"
        for item in data:
            if not item is None:
                result+= str(item) + splitter
            else:
                result+= empty + splitter
        return result[:-len(splitter)]
    
    def __unicode__(self):
        return unicode(self.__str__())
    
    def __repr__(self):
        return self.__str__()
    
    def as_is(self):
        """ will return None|Object|List depending on content """
        if len(self) == 0:
            return None
        elif len(self) == 1:
            return list(self)[0]
        else:
            return self
    
    def as_string(self):
        """ same to str(this) """
        return self.__unicode__()
    
    def as_list(self):
        """ same to self  (!!! Dummy method) """
        return list(self)
    
    def is_empty(self):
        """ True if we have no elements """
        if len(self) == 0:
            return True
        else:
            return False 
        
    def is_string(self):
        """ True if we have exactly 1 item """
        if len(self) == 1:
            return True
        else:
            return False    

    def is_list(self):
        """ True if we have more than 1 item """
        if len(self) > 1:
            return True
        else:
            return False
        
    def __nonzero__(self):
        """ bool(self) returns True only if we have at last 1 non-zero length element
            it helps to send non-empty list into Django-template ("",) and show filled inputs, 
            but still check it for existence {%if a %}
        """
        if len(self.__str__())==0:
            return False
        else:
            return True

    def __getitem__(self, uri):
        """ results["ext:Tag#1213213"] 
            To select exact result from list
        """
        from model import shortcut_to_uri
        for item in self:
            if item==uri or item==shortcut_to_uri(uri):
                return item
        return
            
    def __getattr__(self, predicate):
        ''' results.foaf_knows '''
        predicate_delimited = predicate.replace(ATTR_DELIMITER, DICT_DELIMITER, 1)
        return self.__getitem__(predicate_delimited)