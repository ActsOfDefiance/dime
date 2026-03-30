from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from dime.api.deps import DbSession
from dime.api.schemas.article import ArticleRead
from dime.api.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from dime.models.article import Article
from dime.models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(body: ProjectCreate, db: DbSession) -> Project:
    project = Project(
        id=uuid.uuid4(),
        name=body.name,
        slug=body.slug,
        style_guide=body.style_guide,
        content_guide=body.content_guide,
        workflow_config_id=body.workflow_config_id,
        default_adapter=body.default_adapter,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
async def list_projects(db: DbSession) -> list[Project]:
    result = await db.execute(select(Project))
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: uuid.UUID, db: DbSession) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: uuid.UUID, body: ProjectUpdate, db: DbSession
) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if body.name is not None:
        project.name = body.name
    if body.style_guide is not None:
        project.style_guide = body.style_guide
    if body.content_guide is not None:
        project.content_guide = body.content_guide
    if body.default_adapter is not None:
        project.default_adapter = body.default_adapter
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}/content-guide")
async def get_content_guide(project_id: uuid.UUID, db: DbSession) -> dict[str, Any]:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(project.content_guide)


@router.get("/{project_id}/articles", response_model=list[ArticleRead])
async def list_project_articles(project_id: uuid.UUID, db: DbSession) -> list[Article]:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await db.execute(select(Article).where(Article.project_id == project_id))
    return list(result.scalars().all())
