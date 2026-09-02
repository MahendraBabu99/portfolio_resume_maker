from fastapi import UploadFile

def bucket_pdf(supabase,user_id, file:UploadFile):
    path = f"users/{user_id}/{file.filename}"
    content = file.file.read()
    supabase.storage.from_("pdf").upload(
        path,
        content,
        {"content-type": "application/pdf"}
    )
    url = supabase.storage.from_("pdf").get_public_url(path)

    supabase.table("users").update({
        "resume": url
    }).eq("id", user_id).execute()

    return {"url": url}

def insert_users(supabase, name, role):
    response = supabase.table('users').insert({
        'user_name' : name,
        'role' : role,
    }).execute()
    return response.data
    


def select(supabase):
    response = supabase.table('users').select('*').execute()
    return response.data