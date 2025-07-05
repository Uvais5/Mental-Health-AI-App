
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import json
from langchain_community.document_loaders import PyPDFDirectoryLoader
import requests  
from io import BytesIO
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
import fitz  
import requests
import fitz  # PyMuPDF
from io import BytesIO
from kivy.utils import platform
def get_pdf_text2(pdf_docs):
    """
    Extracts text from PDF(s), ignoring pages that only contain images (e.g., scanned PDFs).
    
    :param pdf_docs: str or list of PDF file paths/URLs
    :return: Extracted text as a string
    """
    text = ""

    if isinstance(pdf_docs, str):
        pdf_docs = [pdf_docs]

    for pdf_doc in pdf_docs:
        try:
            print("Processing:", pdf_doc)

            # Load PDF from URL
            if pdf_doc.startswith("http"):
                response = requests.get(pdf_doc)
                if response.status_code == 200:
                    pdf_data = BytesIO(response.content)
                    pdf_reader = fitz.open(stream=pdf_data, filetype="pdf")
                else:
                    print(f"Failed to fetch PDF from {pdf_doc}")
                    continue
            else:
                # Load local PDF
                pdf_reader = fitz.open(pdf_doc)

            # Go through each page and extract text if it exists
            for i, page in enumerate(pdf_reader):
                page_text = page.get_text("text").strip()
                if page_text:
                    text += f"\n--- Page {i + 1} ---\n"
                    text += page_text + "\n"
                else:
                    print(f"Page {i + 1} contains only images or no extractable text. Skipped.")

        except Exception as e:
            print(f"Error processing {pdf_doc}: {e}")

    return text.strip()

def get_pdf_text(pdf_docs):
    """
    Extracts text from a PDF file (local or URL). Works on Android with Kivy.
    
    :param pdf_docs: str (PDF file path or URL) or list of PDFs
    :return: Extracted text as a string
    """
    text = ""

    # Convert a single string input to a list
    if isinstance(pdf_docs, str):
        pdf_docs = [pdf_docs]

    for pdf_doc in pdf_docs:
        try:
            print("Processing:", pdf_doc)

            # Handle PDF from URL
            if pdf_doc.startswith("http"):
                response = requests.get(pdf_doc)
                if response.status_code == 200:
                    pdf_data = BytesIO(response.content)
                    pdf_reader = fitz.open(stream=pdf_data, filetype="pdf")
                else:
                    print(f"Failed to fetch PDF from {pdf_doc}")
                    continue
            else:
                # Handle local PDF file (use correct Android path)
                pdf_reader = fitz.open(pdf_doc)

            # Extract text from each page
            for page in pdf_reader:
                text += page.get_text("text") + "\n"

        except Exception as e:
            print(f"Error processing {pdf_doc}: {e}")

    return text.strip()




def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    print("This is Embedding ",embeddings)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain



def gemini_pro(question):
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(question,stream=True)
    print("This is gemini-1.5-flash answer")
    for chunk in response:
        # print(response)
        pass
    return response.text


def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)
    response = response["output_text"]
    # print("___________________Output______________")
    # print(response)
    return response
    
    
    

def get_response(ques,pdf_docs):
    if ques is None:
        return "question is none"
    else:

        # pdf_docs = "https://sims.sairam.edu.in/wp-content/uploads/sites/7/2024/03/THE-INTELLIGENT-INVESTOR.pdf"
        raw_text = get_pdf_text2(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)
        res = user_input(ques)
        if "answer is not available in the context" in res.lower():
            print("This is gemini")
            res = gemini_pro(ques)
        elif "the provided context does not mention anything about" in res.lower():
            res = gemini_pro(ques)
        elif  "this context does not mention anything about" in res.lower()  :
            res = gemini_pro(ques)
        elif "this question cannot be answered from the given" in res.lower():
            res = gemini_pro(ques)
        return res


from utils.classes.database import get_database_path
base_dir = get_database_path()
def get_cbt_response(thought,mode):
    if mode=="thought_cbt":
        file_name = "thought_cbt_conversation_log.json"
         
    elif mode == "imgery_cbt":
        file_name = "imagery_conversation_log.json"
    try:        
        full_file_path = os.path.join(base_dir[2],file_name)
        if platform == 'android' and app_storage_path:
            print("this os ")
            from android.storage import app_storage_path
            file_dir = app_storage_path()
        else:
            file_dir = os.getcwd()
        file_path = os.path.join(file_dir, full_file_path)
        print(file_path)
        try:
            with open(file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                except:
                    data = []
                
        except:
            print("json is not created")
            data=[]
    
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat(history=data)
        response = chat.send_message(f"""{thought}""",stream=True) 
        res = []
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                res.append(chunk.text)

        text = ''.join(res)

        add_to_conversation(file_path, thought, text)
    except Exception as e:
        print(e)
        text = "somthing went wrong ask again"
    return text


def get_convert_image_prompt(prompt):

    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(f"convert this thought {prompt} to a image generator context",stream=True)
    res =[]
    for chunk in response:
        res.append(chunk.text)
    return res

def load_conversation(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            try:
                return json.load(json_file)
            except:
                return []
    else:
        # If the file doesn't exist, return an empty list (new file will be created later)
        return []

# Function to save updated data to JSON
def save_conversation(file_path, conversation_data):
    with open(file_path, 'w') as json_file:
        json.dump(conversation_data, json_file, indent=4)

# Function to add a new question and response in the required format
def add_to_conversation(file_path, user_message, assistant_message):
    # Step 1: Load existing conversation (or start a new one if the file doesn't exist)
    conversation_data = load_conversation(file_path)

    # Step 2: Add the new question (user message) and response (assistant message)
    conversation_data.append({
        "role": "user",
        "parts": user_message
    })
    conversation_data.append({
        "role": "model",
        "parts": assistant_message
    })

    # Step 3: Save the updated conversation back to the JSON file (create the file if it doesn't exist)
    save_conversation(file_path, conversation_data)



def get_visualization_instruction(data,mode):
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            if mode=="instruction":    
                response = model.generate_content(f"gave me instruction to Visualization with Affirmations with this data'{data}' while instructing to visualizaton i want you to say my affirmations and make visualization part in more detailed as possible ")
            else:
                response = model.generate_content(f"gave me affirmations accrouding to this data '{data}'")
            return response.text.replace("*","")
        
        except:
            text = "somthing went wrong please restart the app and generate again"
            return text
# if __name__ == "__main__":
#     main()




def ask_gemini_about_pdf(question, pdf):
    context_text = get_pdf_text2(pdf)
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt_template = f"""
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context_text}?\n
    Question: \n{question}\n

    Answer:
    """
    response = model.generate_content(prompt_template)
    return response.text