class Module:

    def run(self):
        raise NotImplementedError

    def stop(self, timeout=None):
        raise NotImplementedError
