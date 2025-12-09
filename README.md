# Flappy Bird

Лабораторная работа №3 - 2D аркадная игра на Python с использованием Pygame.

## Установка и запуск

```bash
pip install -r requirements.txt
python src/main.py
```

## Управление

- **ПРОБЕЛ** или **ЛКМ** - прыжок
- **ESC** - выход в меню

## Структура проекта

```
flappy_bird/
├── src/
│   ├── main.py              # Главный модуль
│   ├── config/
│   │   └── game_config.json # Конфигурация игры
│   ├── engine/
│   │   ├── game_engine.py   # Игровой движок
│   │   └── physics.py       # Физика и коллизии
│   ├── objects/
│   │   ├── game_object.py   # Базовые классы
│   │   ├── bird.py          # Класс птицы
│   │   ├── pipe.py          # Класс труб
│   │   └── ground.py        # Класс земли
│   └── ui/
│       ├── renderer.py      # Рендерер
│       └── menu.py          # Меню и UI
├── requirements.txt
└── README.md
```

## Архитектура

Проект использует ООП подход с иерархией классов:

- `GameObject` → `MovingObject` → `AnimatedObject` → `Bird`
- `GameObject` → `MovingObject` → `Pipe`, `Ground`

## Уровни сложности

- **Легко**: большой промежуток, медленные трубы
- **Средне**: стандартные настройки
- **Сложно**: маленький промежуток, быстрые трубы
