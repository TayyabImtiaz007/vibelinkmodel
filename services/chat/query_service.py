import os

from dotenv import load_dotenv
import openai
from services.chat.core.text_service import TextService
# import chroma
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()

# openai.api_key = os.getenv("OPENAI_KEY")
openai.api_key = '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'

# os.environ["OPENAI_API_KEY"] = API_KEY

HOME = os.path.dirname(os.path.abspath(__file__))
embeddings = OpenAIEmbeddings()


class ChatQueryService:
    def __init__(self, user_id, text, directory):
        self.text= text
        self.user_id = user_id
        self.directory = directory
        # self.query = query
    def query_text_service(self):
        # Take input from the user
        vectordb = Chroma(persist_directory=os.path.join(self.directory, "chroma_storage", self.user_id), embedding_function=embeddings)
        # Query the text_service system with the user ID and input text
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model_name='gpt-3.5-turbo')
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        if self.text:
            query = f"###Prompt {self.text}"
            llm_response = qa(query)
            return llm_response["result"]
        else:
            return []

    # print(chatsys('/Users/mac/Downloads/langchain-chat-vector-db-dev/vocabularies.txt', 'dhjfj-jfjj-jfjj_akin'))
    # user_id = 'dhjfj-jfjj-jfjj_poly'
    # chatsys('/Users/mac/Downloads/langchain-chat-vector-db-dev/vocabularies.txt', user_id)
    # while True:
    #     query = input("input the text here: ")
    #     output = query_text_service(user_id, input("input the text here: "))
    #     print(output)
# query = input("Input the text here: ")
# print(query_text_service(user_id, query))
# /Users/mac/Downloads/langchain-chat-vector-db-dev/chroma_storage/dhjfj-jfjj-jfjj_akin
# chatsys('/Users/mac/Downloads/langchain-chat-vector-db-dev/vocabularies.txt', 'dhjfj-jfjj-jfjj_akin')
