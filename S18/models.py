from peewee import *
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

db = SqliteDatabase('room_equipment.db')


class EquipmentType(str, Enum):
    TECH = "tech"
    FURNITURE = "furniture"
    TOOL = "tool"
    
    @classmethod
    def get_values(cls) -> List[str]:
        return [item.value for item in cls]
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.get_values()


class BaseModel(Model):
    class Meta:
        database = db


class Equipment(BaseModel):
    name = CharField(max_length=100, unique=True)
    description = CharField(max_length=500, null=True)
    equipment_type = CharField(
        max_length=20,
        choices=[(e.value, e.name) for e in EquipmentType],
        default=EquipmentType.TECH.value
    )
    is_portable = BooleanField(default=False)
    power_required = BooleanField(default=False)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(null=True)  # При создании = NULL

    class Meta:
        table_name = 'equipment'

    def save(self, *args, **kwargs):
        is_new = self.id is None
        
        if is_new:
            if len(self.name) > 100:
                raise ValueError("Название оборудования должно содержать максимум 100 символов")
        else:
            if len(self.name) < 2 or len(self.name) > 100:
                raise ValueError("Название оборудования должно содержать от 2 до 100 символов")
        
        if self.description is not None and len(self.description) > 500:
            raise ValueError("Описание должно содержать максимум 500 символов")
        
        if not EquipmentType.is_valid(self.equipment_type):
            raise ValueError(f"Тип оборудования должен быть одним из: {', '.join(EquipmentType.get_values())}")
        
        if not is_new:
            dirty_fields = [f for f in self.dirty_fields if f != 'updated_at']
            if dirty_fields:
                self.updated_at = datetime.now()
        
        return super().save(*args, **kwargs)

    @classmethod
    def soft_delete_by_id(cls, equipment_id: int) -> bool:
        try:
            equipment = cls.get_by_id(equipment_id)
            if not equipment.is_active:
                return False
            equipment.is_active = False
            equipment.updated_at = datetime.now()
            equipment.save()
            return True
        except DoesNotExist:
            return False

    def soft_delete(self) -> bool:
        if not self.is_active:
            return False
        self.is_active = False
        self.updated_at = datetime.now()
        self.save()
        return True

    def restore(self) -> bool:
        if self.is_active:
            return False
        self.is_active = True
        self.updated_at = datetime.now()
        self.save()
        return True

    @classmethod
    def get_by_id_or_none(cls, equipment_id: int) -> Optional['Equipment']:
        try:
            return cls.get_by_id(equipment_id)
        except DoesNotExist:
            return None

    @classmethod
    def get_active_by_id(cls, equipment_id: int) -> Optional['Equipment']:
        try:
            return cls.get((cls.id == equipment_id) & (cls.is_active == True))
        except DoesNotExist:
            return None

    @classmethod
    def filter_equipment(cls,
                         equipment_type: Optional[str] = None,
                         is_portable: Optional[bool] = None,
                         power_required: Optional[bool] = None,
                         is_active: bool = True,
                         search: Optional[str] = None,
                         limit: int = 20,
                         offset: int = 0) -> List['Equipment']:

        if limit < 1 or limit > 100:
            raise ValueError("limit должен быть от 1 до 100")
        if offset < 0:
            raise ValueError("offset должен быть >= 0")
        
        query = cls.select()
        

        if equipment_type:
            if not EquipmentType.is_valid(equipment_type):
                raise ValueError(f"Неверный тип оборудования: {equipment_type}")
            query = query.where(cls.equipment_type == equipment_type)
        if is_portable is not None:
            query = query.where(cls.is_portable == is_portable)
        if power_required is not None:
            query = query.where(cls.power_required == power_required)
        if is_active is not None:
            query = query.where(cls.is_active == is_active)
        if search:
            query = query.where(cls.name.contains(search))
        
        # Пагинация
        query = query.limit(limit).offset(offset)
        
        return list(query)

    @classmethod
    def count_filtered(cls,
                       equipment_type: Optional[str] = None,
                       is_portable: Optional[bool] = None,
                       power_required: Optional[bool] = None,
                       is_active: bool = True,
                       search: Optional[str] = None) -> int:

        query = cls.select()
        
        if equipment_type:
            if not EquipmentType.is_valid(equipment_type):
                raise ValueError(f"Неверный тип оборудования: {equipment_type}")
            query = query.where(cls.equipment_type == equipment_type)
        if is_portable is not None:
            query = query.where(cls.is_portable == is_portable)
        if power_required is not None:
            query = query.where(cls.power_required == power_required)
        if is_active is not None:
            query = query.where(cls.is_active == is_active)
        if search:
            query = query.where(cls.name.contains(search))
        
        return query.count()

    def to_dict(self, for_list: bool = False) -> Dict[str, Any]:
  
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "equipment_type": self.equipment_type,
            "is_portable": self.is_portable,
            "power_required": self.power_required,
            "is_active": self.is_active,
        }
        
        if not for_list:
            data["created_at"] = self.created_at.isoformat() if self.created_at else None
            data["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        
        return data
        
def init_db():
    db.connect()
    db.create_tables([Equipment])


if __name__ == '__main__':
    init_db()
