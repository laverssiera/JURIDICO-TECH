from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LegalClause, LegalContract
from app.events.repository import OutboxRepository


class ContractRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, contract: LegalContract) -> LegalContract:
        self.session.add(contract)
        await self.session.commit()
        await self.session.refresh(contract)
        return contract

    async def add_with_outbox(self, contract: LegalContract, subject: str, payload: dict) -> LegalContract:
        outbox_repo = OutboxRepository(self.session)
        async with self.session.begin():
            self.session.add(contract)
            await outbox_repo.enqueue(subject=subject, payload=payload)
        await self.session.refresh(contract)
        return contract

    async def get(self, contract_id: str) -> LegalContract | None:
        stmt = select(LegalContract).where(LegalContract.id == contract_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[LegalContract]:
        stmt = select(LegalContract).order_by(LegalContract.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_clause(self, clause: LegalClause) -> LegalClause:
        self.session.add(clause)
        await self.session.commit()
        await self.session.refresh(clause)
        return clause

    async def list_clauses(self, contract_id: str) -> list[LegalClause]:
        stmt = select(LegalClause).where(LegalClause.contract_id == contract_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_clause(self, contract_id: str, clause_id: str) -> LegalClause | None:
        stmt = select(LegalClause).where(
            LegalClause.contract_id == contract_id,
            LegalClause.id == clause_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_clause(self, clause: LegalClause) -> None:
        await self.session.delete(clause)
        await self.session.commit()

    async def update_clause(self, clause: LegalClause) -> LegalClause:
        await self.session.commit()
        await self.session.refresh(clause)
        return clause

    async def transition(
        self,
        contract: LegalContract,
        new_status: str,
        subject: str,
        payload: dict,
    ) -> LegalContract:
        outbox_repo = OutboxRepository(self.session)
        contract.status = new_status
        self.session.add(contract)
        await outbox_repo.enqueue(subject=subject, payload=payload)
        await self.session.commit()
        await self.session.refresh(contract)
        return contract
