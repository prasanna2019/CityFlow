from sqlalchemy.orm import Mapped, relationship, DeclarativeBase, mapped_column, validates
from pydantic import BaseModel, Field, EmailStr


class Base(DeclarativeBase):
    pass

class User(Base):
     __tablename__= 'users'
     id: Mapped[int]= mapped_column(nullable= False, primary_key= True)
     name: Mapped[str]= mapped_column(nullable= False)
     email: Mapped[str]= mapped_column(nullable= False, unique= True)
     age: Mapped[int | None]= mapped_column()
     password: Mapped[str]= mapped_column(nullable= False)

     @validates('age') 
     def age_validate(self, key, age):
          if age < 18:
               raise ValueError("Age should be more than 18")
          return age
     
     @validates('password')
     def password_validate(self, key, password):
          if len(password) < 8:
               raise ValueError("Password should be more than 10 characters")
          return password

     

class UserResponse(BaseModel):
     name: str= Field(min_length= 3, max_length= 15)
     email: str= EmailStr

     
     




