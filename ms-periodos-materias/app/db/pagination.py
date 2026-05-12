from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.pagination import get_offset


async def paginate_query(
    db: AsyncSession,
    stmt: Select,
    page: int,
    limit: int,
):
    count_stmt = select(func.count()).select_from(
        stmt.order_by(None).subquery()
    )

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    result = await db.execute(
        stmt.offset(get_offset(page, limit)).limit(limit)
    )

    items = result.scalars().all()

    return items, total