from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    todos = relationship('ToDo', back_populates='user')
    assessments = relationship("Assessment", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    co_curricular = relationship("CoCurricular", back_populates="user")
    personal_commitments = relationship("PersonalCommitment", back_populates="user")

    def check_password(self, password):
        return check_password_hash(self.password, password)

class ToDo(Base):
    __tablename__ = 'todo'
    id = Column(Integer, primary_key=True)
    task = Column(String, nullable=False)
    category = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='todos')

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    subject = Column(String(50), nullable=False)
    due_date = Column(DateTime, nullable=False)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="assessments")

class StudySession(Base):
    __tablename__ = 'study_sessions'
    id = Column(Integer, primary_key=True)
    subject = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer)  # Duration in minutes
    topics = Column(String(200))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="study_sessions")

class CoCurricular(Base):
    __tablename__ = 'co_curricular'
    id = Column(Integer, primary_key=True)
    activity = Column(String(100), nullable=False)
    schedule = Column(String(200))
    location = Column(String(100))
    role = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="co_curricular")

class PersonalCommitment(Base):
    __tablename__ = 'personal_commitments'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    priority = Column(String(20))
    notes = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="personal_commitments")

# Database setup
engine = create_engine('sqlite:///todo.db')
Base.metadata.create_all(engine)