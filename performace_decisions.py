### performance tests

### how to initialize array with defaults

pos = range(300)

def test1():
    """Stupid test function"""
    l = []
    for i in pos:
        l.append((1, 1, 1))

def test2():
    len(pos) * [(1, 1, 1)]

def test3():
    map(lambda x: (1, 1, 1), pos)
    
## default values

def dv1(a=dict()):
    return a.get(0) or 5

def dv2(a=2):
    return a
    
    

if __name__ == '__main__':
    import timeit
    #print "Initialze array"
    #print "append: ", (timeit.timeit("test1()", setup="from __main__ import *"))
    #print "len*: ", (timeit.timeit("test2()", setup="from __main__ import *"))
    #print "map lambda: ", (timeit.timeit("test3()", setup="from __main__ import *"))

    print 'default values'
    print "or: ", (timeit.timeit("dv1()", setup="from __main__ import *"))
    print "or mit parameter: ", (timeit.timeit("dv1({'a':5})", setup="from __main__ import *"))
    print "=: ", (timeit.timeit("dv2()", setup="from __main__ import *"))
    print "= mit parameter: ", (timeit.timeit("dv2(**{'a': 3})", setup="from __main__ import *"))
    
    
    
