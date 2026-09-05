from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostResponse, PostCreate, UserCreate, UserRead, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from app.users import auth_backend, current_active_user, fastapi_users

import shutil
import os
import uuid
import tempfile



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(fastapi_users.get_auth_router(auth_backend),prefix='/auth/jwt',tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead,UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    temp_file_path = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename or "")[1]
        ) as temp_file:

            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Upload to ImageKit
        with open(temp_file_path, "rb") as image_file:
            upload_result = imagekit.files.upload(
                file=image_file,
                file_name=file.filename or "upload",
                use_unique_file_name=True,
                tags=["backend-upload"],
            )

        # Create database record
        post = Post(
            caption=caption,
            url=upload_result.url,
            file_type=(
                "video"
                if file.content_type and file.content_type.startswith("video/")
                else "image"
            ),
            file_name=upload_result.name,
        )

        session.add(post)

        await session.commit()
        await session.refresh(post)

        return post

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Delete temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        # Close uploaded file
        if file.file:
            file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )

    posts = result.scalars().all()

    posts_data = []

    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
            }
        )

    return {
        "posts": posts_data
    }


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(
            select(Post).where(Post.id == post_uuid)
        )

        post = result.scalars().first()

        if not post:
            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )

        await session.delete(post)
        await session.commit()

        return {
            "success": True,
            "message": "Post deleted successfully"
        }

    except HTTPException:
        raise

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid post ID"
        )

    except Exception as e:
        await session.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

