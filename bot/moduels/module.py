class Module:

    def run(self):
        raise NotImplementedError


    async def start(self):
        raise NotImplementedError


    async def close(self):
        raise NotImplementedError
