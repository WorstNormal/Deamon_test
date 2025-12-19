from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class TaskDifficulty(str, enum.Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

class ElementType(str, enum.Enum):
    Task = "Task"
    Theory = "Theory"

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"

    module_id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    open_date = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="modules")
    submodules = relationship("Submodule", back_populates="module", cascade="all, delete-orphan")

class Submodule(Base):
    __tablename__ = "submodules"

    submodule_id = Column(Integer, primary_key=True, index=True)
    submodule_name = Column(String, nullable=False)
    module_id = Column(Integer, ForeignKey("modules.module_id"))

    module = relationship("Module", back_populates="submodules")
    tasks = relationship("Task", back_populates="submodule", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    submodule_id = Column(Integer, ForeignKey("submodules.submodule_id"))
    type = Column(Enum(ElementType, name="element_type"), default=ElementType.Task)

    description = Column(Text)
    difficulty = Column(Enum(TaskDifficulty, name="task_difficulty"), nullable=True)
    time_limit = Column(String, nullable=True)
    memory_limit = Column(String, nullable=True)
    max_score = Column(Integer, default=100)

    submodule = relationship("Submodule", back_populates="tasks")