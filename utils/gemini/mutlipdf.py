import os
import fitz  # PyMuPDF
import requests
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv

# Load your environment key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# --------- PDF Text Extraction (Local or URL, Android-compatible) ---------
def get_pdf_text(pdf_docs):
    text = ""

    if isinstance(pdf_docs, str):
        pdf_docs = [pdf_docs]

    for pdf_doc in pdf_docs:
        try:
            print("Processing:", pdf_doc)

            if pdf_doc.startswith("http"):
                response = requests.get(pdf_doc)
                if response.status_code == 200:
                    pdf_data = BytesIO(response.content)
                    pdf_reader = fitz.open(stream=pdf_data, filetype="pdf")
                else:
                    print(f"Failed to fetch PDF from {pdf_doc}")
                    continue
            else:
                pdf_reader = fitz.open(pdf_doc)

            for i, page in enumerate(pdf_reader):
                page_text = page.get_text("text").strip()
                if page_text:
                    text += f"\n--- Page {i + 1} ---\n{page_text}\n"
                else:
                    print(f"Page {i + 1} contains only images or no extractable text.")

        except Exception as e:
            print(f"Error processing {pdf_doc}: {e}")

    return text.strip()

# --------- Split Text into Chunks ---------
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_text(text)

# --------- Generate Embeddings and Store in FAISS ---------
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# --------- Load Conversational QA Chain ---------
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context.
    If the answer is not in the context, say "answer is not available in the context please click the reload button to select next book that can provide the answer of your question ".

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.9)
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# --------- Gemini Fallback Model ---------
def gemini_pro(question):
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(question, stream=True)
    final_output = ""
    for chunk in response:
        final_output += chunk.text
    return final_output

# --------- Handle User Input and Ask Question ---------
def user_input(question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return response["output_text"]

# --------- Main Entry Function ---------
def get_response(question, pdf_docs):
    if not question:
        return "No question provided."

    raw_text = get_pdf_text(pdf_docs)
    chunks = get_text_chunks(raw_text)
    get_vector_store(chunks)

    response = user_input(question)

    if any(x in response.lower() for x in [
        "answer is not available in the context",
        "the provided context does not mention anything about",
        "this context does not mention anything about",
        "this question cannot be answered from the given"
    ]):
        return gemini_pro(question)

    return response

# --------- Example Usage (Replace with your own URL or file path) ---------
# if __name__ == "__main__":
#     question = "why this depression happened first analysis this context and gave me answer accourding to you "
#     pdf_url = "https://openlibrary-repo.ecampusontario.ca/jspui/bitstream/123456789/1145/4/The-Bell-Jar-1645639688._print.pdf"
#     answer = get_response(question, pdf_url)
#     print("\nFinal Answer:\n", answer)
