import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models_server import Course, Module, Submodule, Task
from schemas import CourseImport

app = FastAPI(title="LMS Course Importer")


async def get_or_create_course(session: AsyncSession, data: CourseImport) -> Course:
    stmt = select(Course).where(Course.course_name == data.course_name)
    result = await session.execute(stmt)
    course = result.scalar_one_or_none()

    if course:
        course.description = data.description
    else:
        course = Course(course_name=data.course_name, description=data.description)
        session.add(course)

    await session.flush()
    return course


async def get_or_create_module(session: AsyncSession, course_id: int, name: str) -> Module:
    stmt = select(Module).where(Module.course_id == course_id, Module.module_name == name)
    result = await session.execute(stmt)
    module = result.scalar_one_or_none()

    if not module:
        module = Module(course_id=course_id, module_name=name)
        session.add(module)
        await session.flush()
    return module


async def get_or_create_submodule(session: AsyncSession, module_id: int, name: str) -> Submodule:
    stmt = select(Submodule).where(Submodule.module_id == module_id, Submodule.submodule_name == name)
    result = await session.execute(stmt)
    submodule = result.scalar_one_or_none()

    if not submodule:
        submodule = Submodule(module_id=module_id, submodule_name=name)
        session.add(submodule)
        await session.flush()
    return submodule


async def upsert_task(session: AsyncSession, submodule_id: int, task_data) -> Task:
    stmt = select(Task).where(Task.submodule_id == submodule_id, Task.task_name == task_data.task_name)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    update_data = {
        "description": task_data.description,
        "type": task_data.type,  # Сохраняем тип (Task/Theory)
        "difficulty": task_data.difficulty,
        "time_limit": task_data.time_limit,
        "memory_limit": task_data.memory_limit,
        "max_score": task_data.max_score
    }

    if task:
        for key, value in update_data.items():
            setattr(task, key, value)
    else:
        task = Task(submodule_id=submodule_id, task_name=task_data.task_name, **update_data)
        session.add(task)

    return task


@app.post("/api/v1/courses/import", status_code=status.HTTP_200_OK)
async def import_course(course_data: CourseImport, db: AsyncSession = Depends(get_db)):
    try:
        course = await get_or_create_course(db, course_data)

        for mod_data in course_data.modules:
            module = await get_or_create_module(db, course.course_id, mod_data.module_name)
            for sub_data in mod_data.submodules:
                submodule = await get_or_create_submodule(db, module.module_id, sub_data.submodule_name)
                for task_data in sub_data.tasks:
                    await upsert_task(db, submodule.submodule_id, task_data)

        await db.commit()
        return {"status": "success", "course_id": course.course_id, "message": f"Course '{course.course_name}' synced."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)