from peewee import *
from datetime import datetime

db = SqliteDatabase('room_equipment.db')


class BaseModel(Model):
    class Meta:
        database = db


class Room(BaseModel):
    room_number = CharField(max_length=20, unique=True)
    floor = IntegerField()
    building = CharField(max_length=50)

    class Meta:
        table_name = 'rooms'


class Equipment(BaseModel):
    name = CharField(max_length=100, unique=True)
    description = CharField(max_length=500, null=True)
    equipment_type = CharField(max_length=20, choices=['tech', 'furniture', 'tool'], default='tech')
    is_portable = BooleanField(default=False)
    power_required = BooleanField(default=False)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)
    
    class Meta:
        table_name = 'equipment'
        indexes = (
            (('name',), False),  # обычный индекс
    )
         def save(self, *args, **kwargs):
        if len(self.name) < 2:
            raise ValueError("Название оборудования должно содержать минимум 2 символа")
        if len(self.name) > 100:
            raise ValueError("Название оборудования должно содержать максимум 100 символов")
        if self.description and len(self.description) > 500:
            raise ValueError("Описание должно содержать максимум 500 символов")
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

          def soft_delete(self):
        self.is_active = False
        self.save()

        def restore(self):
        self.is_active = True
        self.save()

class RoomEquipment(BaseModel):
    room = ForeignKeyField(Room, backref='equipment_links')
    equipment = ForeignKeyField(Equipment, backref='room_links')
    quantity = IntegerField(default=1)
    last_check_date = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.last_check_date = datetime.now()
        return super().save(*args, **kwargs)

    class Meta:
        table_name = 'room_equipment'


def init_db():
    db.connect()
    db.create_tables([Room, Equipment, RoomEquipment])


if __name__ == '__main__':
    init_db()
