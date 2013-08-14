import threading
from Queue import Queue

class NotifWorker(threading.Thread):
    '''
    NotifWorker is a simple worker thread for handling notifications.

    It can be subclassed or call out to external function tasks as appropriate.
    '''
    def __init__(self, is_daemon = True):
        threading.Thread.__init__(self)
        self.name = "NotifWorker"
        self.daemon = is_daemon
        self.tasks = Queue()
        self.start()
        
    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))
            
    def run(self):
        # wait for a task and process it
        while True:
            func, args, kargs = self.tasks.get()
            # TODO: need a sentinel task to indicate shutdown
            try:
                func(*args, **kargs)
            except Exception, e:
                # TODO: log this somewhere
                print "NotifWorker task raised Exception:"
                print e
            self.tasks.task_done()

