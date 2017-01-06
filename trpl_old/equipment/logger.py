import inspect, time, sys

filename = 'log.out'

def get_caller():
    """ return filename, line number, and func name of caller """
    stack = get_stack()
    return stack[3][1], stack[3][2], stack[3][3]

def get_parent():
    """ return filename, line number, and func name of caller's parent function """
    stack = get_stack()
    return stack[4][1], stack[4][2], stack[4][3]

def get_stack():
    return inspect.stack()

def write(message, type='error'):
    caller_fn, caller_line, caller = get_caller()
    parent_fn, parent_line, parent = get_parent()
    caller_fn = ''.join(caller_fn.split('/')[-1].split('.py')[:-1])
    parent_fn = ''.join(parent_fn.split('/')[-1].split('.py')[:-1])
    
    stime = time.strftime('%m/%d/%y-%H:%M:%S')
    
    log_message = '%s : %s.%d:%s : %s.%d:%s : %s\n' % (stime, parent_fn, parent_line, parent, caller_fn, caller_line, caller, message)
    
    f = open(filename, 'a')
    f.write(log_message)
    f.close()
    if type=='error':
        sys.stderr.write(log_message)
    else:
        print log_message
