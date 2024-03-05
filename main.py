import tornado
PORT = 10000


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self):
        super().set_header('Content-Type', 'application/json')

    async def post(self):
        payload = tornado.escape.json_decode(self.request.body)
        response = await self.process(payload)
        return response

    async def process(self, payload):
        return {"success": True}


def main(port=PORT):
    base_handler = BaseHandler()

    app = tornado.web.Application(handlers=[("/predict", base_handler)])
    app.listen(port)


if __name__ == "__main__":
    main()
