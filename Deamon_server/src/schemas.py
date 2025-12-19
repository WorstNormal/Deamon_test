from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TaskDifficulty(str, Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

class ElementType(str, Enum):
    Task = "Task"
    Theory = "Theory"

class TaskImport(BaseModel):
    task_name: str
    type: ElementType = ElementType.Task
    difficulty: Optional[TaskDifficulty] = None
    max_score: int = 0
    description: str
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None

class SubmoduleImport(BaseModel):
    submodule_name: str
    tasks: List[TaskImport]

class ModuleImport(BaseModel):
    module_name: str
    submodules: List[SubmoduleImport]

class CourseImport(BaseModel):
    course_name: str
    description: Optional[str] = None
    modules: List[ModuleImport]