from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client

from app.core.config import settings


def main() -> None:
    if not all([settings.cos_bucket, settings.cos_secret_id, settings.cos_secret_key]):
        raise RuntimeError("COS 配置不完整")

    client = CosS3Client(
        CosConfig(
            Region=settings.cos_region,
            SecretId=settings.cos_secret_id,
            SecretKey=settings.cos_secret_key,
            Scheme="https",
        )
    )
    asset_dir = Path(__file__).resolve().parents[1] / "assets" / "certificates"
    for path in sorted(asset_dir.glob("*.svg")):
        key = f"certificate-square/v1/{path.name}"
        with path.open("rb") as file:
            client.put_object(
                Bucket=settings.cos_bucket,
                Body=file,
                Key=key,
                ContentType="image/svg+xml",
                CacheControl="public, max-age=31536000, immutable",
            )
        print(f"uploaded {key}")


if __name__ == "__main__":
    main()

