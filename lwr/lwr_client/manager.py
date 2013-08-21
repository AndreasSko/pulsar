from Queue import Queue
from threading import Thread
from os import getenv

from .client import Client, InputCachingClient
from .transport import get_transport
from .util import TransferEventManager

from logging import getLogger
log = getLogger(__name__)

DEFAULT_TRANSFER_THREADS = 2


class ClientManager(object):
    """
    Factory to create LWR clients, used to manage potential shared
    state between multiple client connections.
    """
    def __init__(self, **kwds):
        self.transport = get_transport(kwds.get('transport_type', None))
        self.event_manager = TransferEventManager()
        cache = kwds.get('cache', None)
        if cache is None:
            cache = _environ_default_int('LWR_CACHE_TRANSFERS')

        if cache:
            log.info("Setting LWR client class to caching variant.")
            self.client_class = InputCachingClient
            num_transfer_threads = int(kwds.get('transfer_threads', _environ_default_int('LWR_CACHE_TRANSFERS', DEFAULT_TRANSFER_THREADS)))
            self.__init_transfer_threads(num_transfer_threads)
        else:
            log.info("Setting LWR client class to standard, non-caching variant.")
            self.client_class = Client

    def _transfer_worker(self):
        while True:
            transfer_info = self.transfer_queue.get()
            try:
                self.__perform_transfer(transfer_info)
            except:
                pass
            self.transfer_queue.task_done()

    def __perform_transfer(self, transfer_info):
        (client, path) = transfer_info
        event_holder = self.event_manager.acquire_event(path, force_clear=True)
        client.cache_insert(path)
        event_holder.event.set()

    def __init_transfer_threads(self, num_transfer_threads):
        self.transfer_queue = Queue()
        for i in range(num_transfer_threads):
            t = Thread(target=self._transfer_worker)
            t.daemon = True
            t.start()

    def queue_transfer(self, client, path):
        self.transfer_queue.put((client, path))

    def get_client(self, destination_params, job_id):
        return self.client_class(destination_params, job_id, self)


def _environ_default_int(variable, default="0"):
    val = getenv(variable, default)
    int_val = int(default)
    if str(val).isdigit():
        int_val = int(val)
    return int_val