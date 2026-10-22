from dataclasses import dataclass
from bank_system.repositories import InMemoryRepository

@dataclass
class DummyItem:
    id: int
    name: str

def test_repository_operations():
    repo = InMemoryRepository[DummyItem]()
    item = DummyItem(id=1, name="Test")
    
    # Додавання та отримання
    repo.add(item)
    assert repo.get(1) == item
    assert repo.get(999) is None
    
    # Список всіх
    all_items = repo.all()
    assert len(all_items) == 1
    assert all_items[0] == item
    
    # Видалення
    success = repo.remove(1)
    assert success is True
    assert repo.get(1) is None
    
    # Видалення неіснуючого
    assert repo.remove(999) is False