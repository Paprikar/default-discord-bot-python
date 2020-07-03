class Module:

    def run(self):
        raise NotImplementedError

    async def start(self, *args, **kwargs):
        raise NotImplementedError

    def stop(self, timeout=None):
        raise NotImplementedError

    async def close(self, *args, **kwargs):
        raise NotImplementedError
