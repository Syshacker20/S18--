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
    
    class Meta:
        table_name = 'equipment'


class RoomEquipment(BaseModel):
    room = ForeignKeyField(Room, backref='equipment_links')
    equipment = ForeignKeyField(Equipment, backref='room_links')
    quantity = IntegerField(default=1)
    last_check_date = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'room_equipment'

def init_db():
    db.connect()
    db.create_tables([Room, Equipment, RoomEquipment])

if __name__ == '__main__':
    init_db()  
