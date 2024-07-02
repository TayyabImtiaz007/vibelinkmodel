from langchain_community.document_loaders import TextLoader

from services.chat.core.base_service import ChatService


class TextService(ChatService):

    def fetch_document(self):
        self.saved_file_path.endswith("txt")
        self.loaders = TextLoader(self.saved_file_path)
