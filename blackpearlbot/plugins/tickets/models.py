from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from blackpearlbot.plugins.database import SESSION

from .database import Panel, Form, Field


class PanelModel:
    def __init__(
        self,
        guild_id: str,
        name: str,
        description: str,
        id: Optional[int] = None,
        forms=None,
        **kwargs,
    ):
        self.guild_id = guild_id
        self.name = name
        self.description = description
        self.id = id
        self.forms = (
            [
                FormModel(
                    **form.__dict__,
                )
                for form in forms
            ]
            if forms
            else []
        )

    @classmethod
    async def create(
        cls,
        guild_id: str,
        name: str,
        description: str = "",
        **kwargs,
    ) -> int:
        panel = Panel(
            guild_id=guild_id,
            name=name,
            description=description,
        )
        SESSION.add(panel)
        try:
            await SESSION.commit()
            return PanelModel(**panel.__dict__).id  # type: ignore
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def get(
        cls,
        guild_id: str,
        panel_id: int,
        fetch_related: bool = False,
    ) -> Optional["PanelModel"]:
        query = select(Panel).where(
            Panel.guild_id == guild_id,
            Panel.id == panel_id,
        )
        if fetch_related:
            query = query.options(
                selectinload(Panel.forms).selectinload(
                    Form.fields,
                )
            )
        panels = await SESSION.execute(query)
        panel = panels.scalars().first()
        if panel is None:
            return None
        panel = PanelModel(**panel.__dict__)
        return panel

    @classmethod
    async def get_all(
        cls,
        guild_id: str,
        fetch_related: bool = False,
    ) -> list["PanelModel"]:
        query = select(Panel).where(Panel.guild_id == guild_id)
        if fetch_related:
            query = query.options(
                selectinload(
                    Panel.forms,
                ).selectinload(Form.fields)
            )
        panels = await SESSION.execute(query)
        panels = panels.scalars().all()
        return (
            [
                PanelModel(
                    **panel.__dict__,
                )
                for panel in panels
            ]
            if panels
            else []
        )

    @classmethod
    async def update(
        cls,
        guild_id: str,
        panel_id: int,
        name: str,
        description: str,
    ) -> None:
        query = (
            update(Panel)
            .where(
                Panel.guild_id == guild_id,
                Panel.id == panel_id,
            )
            .values(name=name, description=description)
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete(cls, guild_id: str, panel_id: int) -> None:
        query = delete(Panel).where(
            Panel.guild_id == guild_id,
            Panel.id == panel_id,
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete_all(cls, guild_id: str) -> None:
        query = delete(Panel).where(Panel.guild_id == guild_id)
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise


class FormModel:
    def __init__(
        self,
        panel_id: int,
        name: str,
        id: Optional[int],
        description: str = "",
        fields=None,
        **kwargs,
    ):
        self.panel_id = panel_id
        self.name = name
        self.description = description
        self.id = id
        self.fields = []
        if fields:
            self.fields = [FieldModel(**field.__dict__) for field in fields]

    @classmethod
    async def create(
        cls,
        panel_id: int,
        name: str,
        description: str = "",
        **kwargs,
    ) -> str:
        form = Form(
            panel_id=panel_id,
            name=name,
            description=description,
        )
        SESSION.add(form)
        try:
            await SESSION.commit()
            return FormModel(**form.__dict__).id  # type: ignore
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def get(
        cls,
        panel_id: int,
        form_id: int,
        fetch_related: bool = False,
    ) -> Optional["FormModel"]:
        query = select(Form).where(
            Form.panel_id == panel_id,
            Form.id == form_id,
        )
        if fetch_related:
            query = query.options(
                selectinload(Form.fields),
            )
        forms = await SESSION.execute(query)
        form = forms.scalars().first()
        return FormModel(**form.__dict__) if form else None

    @classmethod
    async def get_all(
        cls,
        panel_id: int,
        fetch_related: bool = False,
    ) -> list["FormModel"]:
        query = select(Form).where(Form.panel_id == panel_id)
        if fetch_related:
            query = query.options(
                selectinload(Form.fields),
            )
        forms = await SESSION.execute(query)
        forms = forms.scalars().all()
        return (
            [
                FormModel(
                    **form.__dict__,
                )
                for form in forms
            ]
            if forms
            else []
        )

    @classmethod
    async def update(
        cls,
        panel_id: int,
        form_id: int,
        name: str,
        description: str = "",
    ) -> None:
        query = (
            update(Form)
            .where(
                Form.panel_id == panel_id,
                Form.id == form_id,
            )
            .values(name=name, description=description)
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete(cls, panel_id: int, form_id: int) -> None:
        query = delete(Form).where(
            Form.panel_id == panel_id,
            Form.id == form_id,
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete_all(cls, panel_id):
        query = delete(Form).where(Form.panel_id == panel_id)
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise


class FieldModel:
    def __init__(
        self,
        form_id: int,
        name: str,
        response: str = "",
        id=None,
        **kwargs,
    ):
        self.form_id = form_id
        self.id = id
        self.name = name
        self.response = response or ""

    @classmethod
    async def create(
        cls,
        form_id: int,
        name: str,
        response: str = "",
    ) -> str:
        field = Field(
            form_id=form_id,
            name=name,
            response=response,
        )
        SESSION.add(field)
        try:
            await SESSION.commit()
            return FieldModel(**field.__dict__).id  # type: ignore
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def get(cls, form_id: int, field_id: int) -> Optional["FieldModel"]:
        query = select(Field).where(
            Field.form_id == form_id,
            Field.id == field_id,
        )
        fields = await SESSION.execute(query)
        field = fields.scalars().first()
        return FieldModel(**field.__dict__) if field else None

    @classmethod
    async def get_all(cls, form_id: int) -> list["FieldModel"]:
        query = select(Field).where(Field.form_id == form_id)
        fields = await SESSION.execute(query)
        fields = fields.scalars().all()
        return (
            [
                FieldModel(
                    **field.__dict__,
                )
                for field in fields
            ]
            if fields
            else []
        )

    @classmethod
    async def update(
        cls,
        form_id: int,
        field_id: int,
        name: str,
        response: str = "",
    ) -> None:
        query = (
            update(Field)
            .where(
                Field.form_id == form_id,
                Field.id == field_id,
            )
            .values(name=name, response=response)
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete(cls, form_id: int, field_id: int) -> None:
        query = delete(Field).where(
            Field.form_id == form_id,
            Field.id == field_id,
        )
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise

    @classmethod
    async def delete_all(cls, form_id: int) -> None:
        query = delete(Field).where(Field.form_id == form_id)
        await SESSION.execute(query)
        try:
            await SESSION.commit()
        except Exception:
            await SESSION.rollback()
            raise
