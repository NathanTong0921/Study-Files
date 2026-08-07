from langchain.agents import create_agent
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from tools import get_current_wait_time

def load_api_key(key_file):
    """Load API key from a local file."""
    with open(key_file, "r", encoding="utf-8") as f:
        return f.read().strip()
api_key = load_api_key("api_key.txt")

REVIEWS_CHROMA_PATH = "chroma_data/"

review_template_str = """Your job is to use patient
reviews to answer questions about their experience at
a hospital. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.
{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=review_template_str
    )
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [review_system_prompt, review_human_prompt]

review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

chat_model = ChatOpenAI(
    model="gpt-4",
    api_key=api_key,
    base_url="https://aigc-api.hkust-gz.edu.cn/v1/",
    temperature=0.7,
)

output_parser = StrOutputParser()

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "device": "cpu",
    },
    encode_kwargs={
        "normalize_embeddings": True,
    },
)

reviews_vector_db = Chroma(persist_directory=REVIEWS_CHROMA_PATH, embedding_function=embedding_model)

reviews_retriever = reviews_vector_db.as_retriever(k=10)

review_chain = (
    {"context": reviews_retriever, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | StrOutputParser()
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions
        about patient reviews or experiences at the hospital.
        Not useful for answering questions about specific visit
        details such as payer, billing, treatment, diagnosis,
        chief complaint, hospital, or physician information.
        Pass the entire question as input to the tool. For instance,
        if the question is "What do patients think about the triage system?",
        the input should be "What do patients think about the triage system?"
        """,
    ),
    Tool(
        name="Waits",
        func=get_current_wait_time,
        description="""Use when asked about current wait times
        at a specific hospital. This tool can only get the current
        wait time at a hospital and does not have any information about
        aggregate or historical wait times. This tool returns wait times in
        minutes. Do not pass the word "hospital" as input,
        only the hospital name itself. For instance, if the question is
        "What is the wait time at hospital A?", the input should be "A".
        """,
    ),
]


agent_chat_model = ChatOpenAI(
    model="gpt-4",
    api_key=api_key,
    base_url="https://aigc-api.hkust-gz.edu.cn/v1/",
    temperature=0.2,
)

hospital_agent = create_agent(
    model=agent_chat_model,
    tools=tools,
    system_prompt="You are a helpful assistant. Use tools when appropriate.",
)


# question = """Has anyone complained about communication with the hospital staff?"""
question = "What is the wait time at hospital A?"
result = hospital_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    }
)
print(result["messages"][-1].content)

# test_model = agent_chat_model.bind_tools(tools)
# response = test_model.invoke(
#     "You must use the Waits tool to find the current wait time at hospital A."
# )
# print(response)
# print("Tool calls:", response.tool_calls)