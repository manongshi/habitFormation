from sqlalchemy import select

from app.core.config import settings
from app.data.certificates import CATEGORY_DATA, CERTIFICATE_DATA
from app.db.session import Base, SessionLocal, engine
from app.models import Certificate, CertificateCategory


def image_url(category_code: str) -> str:
    base = settings.cos_public_base_url.rstrip("/")
    return f"{base}/certificate-square/v1/{category_code}.svg"


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        categories = {}
        for code, name, description, sort_order in CATEGORY_DATA:
            category = db.scalar(select(CertificateCategory).where(CertificateCategory.code == code))
            values = {
                "name": name,
                "description": description,
                "image_url": image_url(code),
                "sort_order": sort_order,
                "status": "active",
                "is_deleted": False,
            }
            if category is None:
                category = CertificateCategory(code=code, **values)
                db.add(category)
                db.flush()
            else:
                for field, value in values.items():
                    setattr(category, field, value)
            categories[code] = category

        for sort_order, item in enumerate(CERTIFICATE_DATA, start=1):
            values = dict(item)
            category_code = values.pop("category_code")
            values.update(
                category_id=categories[category_code].id,
                image_url=image_url(category_code),
                sort_order=sort_order,
                status="active",
                is_deleted=False,
            )
            certificate = db.scalar(select(Certificate).where(Certificate.code == values["code"]))
            if certificate is None:
                db.add(Certificate(**values))
            else:
                for field, value in values.items():
                    setattr(certificate, field, value)

        db.commit()
        print(f"seeded {len(CATEGORY_DATA)} categories and {len(CERTIFICATE_DATA)} certificates")


if __name__ == "__main__":
    main()
