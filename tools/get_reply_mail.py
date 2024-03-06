from utils.mail_server import get_mail
from utils.openai_utils import openai_call

PORT = 10006


async def get_reply_mail():
    """
    Retrieves stored mail and creates a positive reply mail for it
    """
    mail_msg = get_mail("user_0")
    system_prompt = f"You are an executive at a big company, who got an email: {mail_msg}"
    messages = [{"role": "user", "content": f"Write a positively worded reply mail."}]
    _response, _ = await openai_call(system_prompt, messages)
    return _response["results"]
