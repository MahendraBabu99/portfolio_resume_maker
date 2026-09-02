import os
from google import genai

client = genai.Client(
    api_key = os.getenv("OPENAI_KEY")
)

def resume(supabase,id):

    response = supabase.table('users')\
        .select('resume')\
        .eq('id', id)\
        .single()\
        .execute()

    return response.data["resume"]

def content(supabase,id, requests, PdfReader, BytesIO):
    pdf_url = resume(supabase,id)

    response = requests.get(pdf_url)

    reader = PdfReader(BytesIO(response.content))

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text
    
    

def generate_code(text):
    
    prompt = f"""
    Create a modern portfolio website for this resume with some interactive user interface
    it should be very professional with some animations. The information used in the code must be taken from the resume only.

    Resume:
    {text}

    Generate:
    - Hero section
    - About section
    - Skills section
    - Projects section
    - Contact section

    Return a single self-contained HTML file with embedded CSS.
    Do not exceed 1500 lines
    Do not include explainations and comments in the code.
    """
    
    response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents=prompt
)

    return response.text

def throw_into_bucket(supabase,code, id):
    path = f"users/{id}/portfolio.html"
    supabase.storage.from_('code').upload(
        path,
        code.encode('utf-8'),
        {'content-type' : 'text/html'}
    )
    
    #after updating into bucket get the link and update users table too
    
    url = supabase.storage.from_('code').get_public_url(path) 
    
    updation  =supabase.table('users').update({
        'portfolio' : url
    }).eq('id',id).execute()
    return {'portfolio-url' : url}
    


def complete(supabase,id,requests, PdfReader, BytesIO):
    res = content(supabase,id,requests,PdfReader,BytesIO)
    code = generate_code(res)
    return  throw_into_bucket(supabase,code,id)
