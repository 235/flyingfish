import RDF
import string

def modeldump(model):
    output = ""
    for s in model.as_stream():
        output += "Statement: %s\n" % s
    return output

def sparql(model, sparql):
    output = ""
    q = RDF.Query(sparql, query_language="sparql")
    for result in q.execute(model):
        output += "{\n"
        for k in result:
            output += "\t%s = %s\n" %  (k,result[k])
        output += "}\n"
    return output

def str_scalar_or_list(var):
    if type(var) is list:  
        return string.join( map(str, var), ', ' ),
    else:
        return str(var)

    