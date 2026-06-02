from peewee import *
from datetime import datetime

db = SqliteDatabase('room_equipment.db')


class BaseModel(Model):
    class Meta:
        database = db


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

    def save(self, *args, **kwargs):
        # Валидация при СОЗДАНИИ (нет проверки на минимальную длину)
        if not self.id:  # новая запись
            if len(self.name) > 100:
                raise ValueError("Название оборудования должно содержать максимум 100 символов")
        else:  # обновление существующей
            if len(self.name) < 2 or len(self.name) > 100:
                raise ValueError("Название оборудования должно содержать от 2 до 100 символов")

            if self.equipment_type not in ['tech', 'furniture', 'tool']:
                raise ValueError("equipment_type должен быть одним из: tech, furniture, tool")

        if self.description and len(self.description) > 500:
            raise ValueError("Описание должно содержать максимум 500 символов")
        
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    def soft_delete(self):
        if not self.is_active:
            return False
        self.is_active = False
        self.save()
        return True

    def restore(self):
        if self.is_active:
            return False
        self.is_active = True
        self.save()
        return True


def init_db():
    db.connect()
    db.create_tables([Equipment])


if __name__ == '__main__':
    init_db()
