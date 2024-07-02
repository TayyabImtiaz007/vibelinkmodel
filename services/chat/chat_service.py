import os

from dotenv import load_dotenv
from services.chat.core.text_service import TextService
# import chroma
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import shutil

load_dotenv()

# API_KEY = os.getenv("OPENAI_KEY")
#
# os.environ["OPENAI_API_KEY"] = API_KEY

HOME = os.path.dirname(os.path.abspath(__file__))
embeddings = OpenAIEmbeddings()


class ChatService:
    def __init__(self, file, user_id, directory):
        self.file = file
        self.user_id = user_id
        self.directory = directory
        # self.query = query
    def chatsys(self):
        # if os.path.exists(os.path.join(self.directory, "chroma_storage")):
        #     shutil.rmtree(os.path.join(self.directory, "chroma_storage"))

        os.makedirs(os.path.join(self.directory, "chroma_storage"), exist_ok=True)

        # uuid_memory = str(uuid.uuid4())
        temp_save_directory = os.path.join(self.directory, 'dataset')

        # filename = '/Users/mac/Downloads/langchain-chat-vector-db-dev/vocab.txt' # add the file name here
        data_path = os.path.join(temp_save_directory, self.file)

        cht_mdl = TextService(data_path, persist_directory=os.path.join(self.directory, "chroma_storage", self.user_id))
        cht_mdl.fetch_document()
        cht_mdl.create_vector_index()
        # while True:
        #     query = input("input the text here: ")
        #     output = cht_mdl.query_document(prompt=query)
        #     print(output)

        # return cht_mdl