from fastapi import FastAPI, HTTPException

app = FastAPI()

text_posts = {
    1: {"title": "New Post", "content": "cool test post"},
    2: {"title": "Morning Thoughts", "content": "Today is going to be a great day."},
    3: {"title": "Weekend Plans", "content": "Looking forward to a relaxing weekend."},
    4: {"title": "Learning FastAPI", "content": "FastAPI is pretty simple and fun to learn."},
    5: {"title": "Coffee Break", "content": "Nothing beats a good cup of coffee."},
    6: {"title": "Coding Time", "content": "Working on a small project today."},
    7: {"title": "Good Weather", "content": "The weather feels amazing today."},
    8: {"title": "New Idea", "content": "I just thought of an interesting project idea."},
    9: {"title": "Keep Going", "content": "Small progress every day adds up."},
    10: {"title": "Good Night", "content": "Time to relax and get some rest."}
}

@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts

@app.get("/posts/{id}")
def get_post(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404,detail="Post not found")
    return text_posts.get(id)