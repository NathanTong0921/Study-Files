from langchain_openai import ChatOpenAI

from langchain_core.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_debug

# set_debug(False)
set_debug(True)


#load API key
def load_api_key(key_file):
    """Load API key from a local file."""
    with open(key_file, "r", encoding="utf-8") as f:
        return f.read().strip()
api_key = load_api_key("api_key.txt")

chat_model = ChatOpenAI(
    model="gpt-4",
    api_key=api_key,
    base_url="https://aigc-api.hkust-gz.edu.cn/v1/",
    temperature=0.7,
)

review_system_template_str = """Your job is to use patient
reviews to answer questions about their experience at a
hospital. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

Patient reviews:

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=review_system_template_str
    )
)
review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [review_system_prompt, review_human_prompt]
review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)

context = "I had a great stay!"
question = "Did anyone have a positive experience?"


# review_chain = review_prompt_template | chat_model
# response = review_chain.invoke({"context": context, "question": question})
# print(response)

output_parser = StrOutputParser()
review_chain_ext = review_prompt_template | chat_model | output_parser
response = review_chain_ext.invoke({"context": context, "question": question})
print(response)


