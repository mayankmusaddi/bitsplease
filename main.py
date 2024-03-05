import json
import yaml
import tornado
import logging

from tornado.ioloop import IOLoop
from utils.openai_utils import openai_call

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
        system_prompt = "You are a helpful assistant"
        messages = payload["messages"]
        with open('tools/tools.yaml', 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)  # Load YAML data
            tools = [{"type": "function", "function": function} for function in yaml_data]
        response, _ = await openai_call(system_prompt, messages, tools=tools)
        return response


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
