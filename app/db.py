from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from app.user import User



async def create_user(session, user_in):
    try:
        user= User(
            name=user_in.name,
            email= user_in.email,
            age= user_in.age

        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "age": user.age
            }
        }
    except ValueError as e:
        return str(e)
    except Exception as e:
        return str(e)
    

async def get_all_users(session):
    try:
        stmt= select(User)
        result = await session.execute(stmt)
        return result.scalars().all()

    except Exception as e:
        return str(e)
    
async def get_user_from_id(session, id):
    try:
        return await session.get(User, id)
    except Exception as e:
        return str(e)
    


