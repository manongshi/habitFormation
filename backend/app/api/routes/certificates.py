from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Certificate, CertificateCategory, User
from app.schemas import CategoryRead, CertificatePage, CertificateRead

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CertificateCategory]:
    return list(
        db.scalars(
            select(CertificateCategory)
            .where(
                CertificateCategory.status == "active",
                CertificateCategory.is_deleted.is_(False),
            )
            .order_by(CertificateCategory.sort_order)
        ).all()
    )


@router.get("", response_model=CertificatePage)
def list_certificates(
    category: str | None = None,
    keyword: str | None = None,
    featured: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CertificatePage:
    filters = [Certificate.status == "active", Certificate.is_deleted.is_(False)]
    if category:
        filters.append(CertificateCategory.code == category)
    if keyword:
        term = f"%{keyword.strip()}%"
        filters.append(
            or_(
                Certificate.name.like(term),
                Certificate.short_name.like(term),
                Certificate.issuer.like(term),
            )
        )
    if featured is not None:
        filters.append(Certificate.is_featured == featured)

    base = select(Certificate).join(Certificate.category).where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = list(
        db.scalars(
            base.options(joinedload(Certificate.category))
            .order_by(Certificate.is_featured.desc(), Certificate.sort_order, Certificate.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return CertificatePage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{certificate_id}", response_model=CertificateRead)
def get_certificate(
    certificate_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Certificate:
    certificate = db.scalar(
        select(Certificate)
        .options(joinedload(Certificate.category))
        .where(
            Certificate.id == certificate_id,
            Certificate.status == "active",
            Certificate.is_deleted.is_(False),
        )
    )
    if certificate is None:
        raise HTTPException(status_code=404, detail="证书不存在或已下架")
    return certificate

