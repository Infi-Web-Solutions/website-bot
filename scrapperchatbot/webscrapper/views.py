# In your app's views.py (e.g., webscrapper/views.py)

import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserSignupForm, UserLoginForm, BotForm, PDFUploadForm, URLInputForm # Import URLInputForm
from .models import Bot
from urlcrawler.main import run_scrapy_spider
# LangChain/LangGraph imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Union
from dotenv import load_dotenv
from pathlib import Path
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
import requests
from bs4 import BeautifulSoup

# For PDF loading and text splitting
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile

# For URL scraping
import trafilatura # New import for web scraping
from langchain_core.documents import Document # To create LangChain Document objects

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
connection_string_env = os.getenv("COLLECTION_STRING")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=OPENAI_API_KEY)

chat_memory = ConversationBufferWindowMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True,
    k=7
)

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a courteous and knowledgeable assistant representing Infi Web Solutions, committed to delivering exceptional client service.

        Your role is to respond thoughtfully to client inquiries using the provided context. Keep your tone professional, warm, and helpful at all times.

       1. Do not mention or reference the source of the information.

       2. Your primary objective is to assist the client by offering accurate and complete answers.

       3. If the context does not contain enough information to respond confidently, reply with: "I don't have enough information to answer that."

    Always present your response in HTML format, and do not include backticks or the word "html" in your output.

    Context: {context}

    Now, craft your reply accordingly."""),
    MessagesPlaceholder("chat_history"),
    ("user", "{question}")
])

class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]
    chat_history: List[Union[HumanMessage, AIMessage]]
    collection_name: str

def retrieve(state: GraphState):
    print("\n---RETRIEVE NODE EXECUTING---")
    question = state["question"]
    current_chat_history = state.get("chat_history", [])
    collection_name = state["collection_name"]
    
    print(f"DEBUG: retrieve() - Using collection_name: '{collection_name}' for search.")
    
    bot_vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string_env,
        use_jsonb=True,
    )
    
    retrieved_docs = bot_vector_store.similarity_search(question, k=6)
    documents = [doc.page_content for doc in retrieved_docs]
    
    print(f"Retrieved {len(documents)} documents:")
    for i, doc_content in enumerate(documents):
        print(f"  Doc {i+1}: {doc_content[:100]}...")
    
    if not documents:
        print("WARNING: No documents retrieved for the current question.")

    return {"documents": documents, "question": question, "chat_history": current_chat_history, "collection_name": collection_name}

def generate(state: GraphState):
    print("\n---GENERATE NODE EXECUTING---")
    question = state["question"]
    documents = state["documents"]
    chat_history = state["chat_history"]
    collection_name = state["collection_name"]
    
    context = "\n\n".join(documents)
    
    print(f"Question to LLM: '{question}'")
    print(f"Context provided to LLM:\n---\n{context}\n---")
    print(f"Chat History provided to LLM: {chat_history}")

    if not context.strip():
        print("WARNING: Empty context provided to LLM. LLM might respond with 'not enough information'.")

    response_messages = llm.invoke(rag_prompt.format_messages(
        context=context,
        chat_history=chat_history,
        question=question
    ))
    
    response = response_messages.content if hasattr(response_messages, 'content') else str(response_messages)

    print(f"LLM Generated Response: '{response}'")
    
    return {"generation": response, "question": question, "documents": documents, "chat_history": chat_history, "collection_name": collection_name}

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")

workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

@csrf_exempt
def chatbot_view(request):
    global chat_memory

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_question = data.get('question', '')

            if not user_question:
                return JsonResponse({'error': 'No question provided.'}, status=400)

            # OPTION 1: Use a fixed/shared collection
            collection_name = "my_docs"  # <-- Use your real collection name here

            # OPTION 2 (if using per-user bot): Load the user's first bot if exists
            # bot = Bot.objects.filter(owner=request.user).first()
            # if bot:
            #     collection_name = bot.collection_name
            # else:
            #     return JsonResponse({'error': 'No bot found for your account.'}, status=404)

            print(f"DEBUG: chatbot_view() - Processing question for collection: {collection_name}: '{user_question}'")

            current_chat_history = chat_memory.load_memory_variables({})["chat_history"]

            inputs = {
                "question": user_question,
                "chat_history": current_chat_history,
                "collection_name": collection_name
            }

            result = app.invoke(inputs)
            response_text = result.get("generation", "I'm sorry, I couldn't process your request.")

            chat_memory.save_context(
                {"input": user_question},
                {"output": response_text}
            )

            return JsonResponse({'response': response_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            print(f"Error processing request in chatbot_view: {e}")
            return JsonResponse({'error': f'An internal server error occurred: {e}'}, status=500)

    return render(request, 'webscrapper/chatbot.html')

# View for user signup
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('webscrapper:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserSignupForm()
    return render(request, 'webscrapper/signup.html', {'form': form})

# View for user login
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('webscrapper:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserLoginForm()
    return render(request, 'webscrapper/login.html', {'form': form})

# Custom logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('webscrapper:login')

@login_required
def home_view(request):
    user_bot = Bot.objects.filter(owner=request.user).first()
    context = {
        'user_bot': user_bot,
        'username': request.user.username
    }
    return render(request, 'webscrapper/home.html', context)

@login_required
def add_bot_view(request):
    if Bot.objects.filter(owner=request.user).exists():
        messages.error(request, "You can only create one bot per account.")
        return redirect('webscrapper:home')

    if request.method == 'POST':
        form = BotForm(request.POST)
        if form.is_valid():
            bot = form.save(commit=False)
            bot.owner = request.user
            bot.save()
            messages.success(request, f"Bot '{bot.name}' created successfully! Collection: {bot.collection_name}")
            return redirect('webscrapper:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = BotForm()
    return render(request, 'webscrapper/add_bot.html', {'form': form})

@login_required
def upload_pdf_view(request, bot_id):
    bot = get_object_or_404(Bot, id=bot_id, owner=request.user)
    
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf_file']
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                for chunk in pdf_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            try:
                loader = PyPDFLoader(tmp_file_path)
                documents = loader.load()
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=500)
                texts = text_splitter.split_documents(documents)
                
                print(f"DEBUG: upload_pdf_view() - Initializing PGVector for collection: '{bot.collection_name}'")
                bot_vector_store = PGVector(
                    embeddings=embeddings,
                    collection_name='my_docs',
                    connection=connection_string_env,
                    use_jsonb=True,
                )
                
                print(f"DEBUG: upload_pdf_view() - Adding {len(texts)} documents to collection: '{bot.collection_name}'")
                bot_vector_store.add_documents(texts)
                
                messages.success(request, f"PDF uploaded and processed for bot '{bot.name}' into collection '{bot.collection_name}'.")
                return redirect('webscrapper:home')
            except Exception as e:
                messages.error(request, f"Error processing PDF: {e}")
                print(f"ERROR in upload_pdf_view: {e}")
            finally:
                os.unlink(tmp_file_path)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PDFUploadForm()
    
    context = {
        'form': form,
        'bot': bot
    }
    return render(request, 'webscrapper/upload_pdf.html', context)


@login_required
def add_url_view(request, bot_id):
    bot = get_object_or_404(Bot, id=bot_id, owner=request.user)

    if request.method == 'POST':
        form = URLInputForm(request.POST)
        if form.is_valid():
            url_to_scrape = form.cleaned_data['url_to_scrape']
            print(f"DEBUG: add_url_view() - Processing URL: {url_to_scrape} for bot '{bot.name}' (Collection: {bot.collection_name})")
            link_of_website=run_scrapy_spider(url_to_scrape)  # Call the scraping function with the provided URL

            print(link_of_website)



            def scrape_website(url):
                """
                Scrapes the given URL and extracts information.
                """
                # Fetch the website content
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad status codes

                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract specific elements and information (modify this section)
                # Example: extracting all paragraph text
                text_extracted=''
                for p in soup.find_all('p'):
                    text_extracted+=p.get_text()

                # Further processing and data extraction as needed
                # ...

                return text_extracted  # Modify return value based on extracted data

            import concurrent.futures
            full_combined_text = ''

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit scraping tasks concurrently
                future_to_url = {executor.submit(scrape_website, url): url for url in link_of_website}
                
                # Gather results as they become available
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        extracted_data = future.result()
                    except Exception as exc:
                        print(f"Scraping {url} generated an exception: {exc}")
                    else:
                        full_combined_text += extracted_data

            print("full combinead text",full_combined_text)

            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(model="text-embedding-3-large",api_key=OPENAI_API_KEY)

            # # See docker command above to launch a postgres instance with pgvector enabled.
            connection = connection_string_env  # Uses psycopg3!
            collection_name = "my_docs"

            vector_store = PGVector(
                embeddings=embeddings,
                collection_name=collection_name,
                connection=connection,
                use_jsonb=True,
            )
            from langchain_core.documents import Document
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=6000,
                chunk_overlap=500,
            )

            # Split the document into chunks
            chunks = splitter.split_text(full_combined_text)

            # Format chunks into Document objects with metadata
            docs = []
            for i, chunk in enumerate(chunks, start=1):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "id": i,
                        "location": "unknown",  # Placeholder – you can update based on content
                        "topic": "unknown"      # Placeholder – you can update based on content
                    }
                )
                docs.append(doc)

            vector_store.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])
            print("added documents to vector store")
    # If the request is GET or form is invalid, render the home page with messages
    return redirect('webscrapper:home') # Redirect to home to show messages and the form


@login_required
def bot_chat_view(request, bot_id):
    bot = get_object_or_404(Bot, id=bot_id, owner=request.user)
    context = {
        'bot': bot,
    }
    return render(request, 'webscrapper/bot_chat.html', context)
