import json
import tornado
import logging

from tornado.ioloop import IOLoop

PORT = 10000


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        super().set_header("Content-Type", "application/json; charset=UTF-8")

    async def post(self):
        payload = tornado.escape.json_decode(self.request.body)
        response = await self.process(payload)
        logging.info(f"request.processed, response={response}")
        self.write(json.dumps(response))
        return response

    async def process(self, payload):
        output = {
            "payload": payload,
            "success": True
        }
        return output


def main(port=PORT):
    try:
        app = tornado.web.Application(handlers=[("/predict", BaseHandler)])
        app.listen(port)
        logging.info(f"Starting tornado server at port: {str(port)}")
        IOLoop.current().start()
    except Exception as e:
        import sys
        logging.error(f"Error in application {e}", exc_info=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
