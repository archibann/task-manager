from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.enums import PriorityEnum


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Все задачи", callback_data="tasks_all")],
        [InlineKeyboardButton(text="✅ Выполненные", callback_data="tasks_completed")],
        [InlineKeyboardButton(text="⏳ В работе", callback_data="tasks_pending")],
        [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")],
    ])
    return keyboard


def get_task_list_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком задач"""
    buttons = []
    for task in tasks:
        status = "✅" if task.completed else "⏳"
        priority_emoji = {
            PriorityEnum.high: "🔴",
            PriorityEnum.medium: "🟡",
            PriorityEnum.low: "🟢",
        }.get(task.priority, "")
        
        title = task.title[:20] + "..." if len(task.title) > 20 else task.title
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {priority_emoji} {title}",
                callback_data=f"task_{task.id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="➕ Новая задача", callback_data="add_task"),
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(task_id: int, completed: bool) -> InlineKeyboardMarkup:
    """Клавиатура деталей задачи"""
    complete_text = "↩️ Вернуть в работу" if completed else "✅ Выполнено"
    buttons = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{task_id}")],
        [InlineKeyboardButton(text=complete_text, callback_data=f"complete_{task_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")],
        [InlineKeyboardButton(text="🔙 К списку задач", callback_data="tasks_all")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора приоритета"""
    buttons = [
        [InlineKeyboardButton(text="🔴 Высокий", callback_data="priority_high")],
        [InlineKeyboardButton(text="🟡 Средний", callback_data="priority_medium")],
        [InlineKeyboardButton(text="🟢 Низкий", callback_data="priority_low")],
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="priority_none")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_delete_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{task_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data=f"task_{task_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура редактирования задачи"""
    buttons = [
        [InlineKeyboardButton(text="📝 Название", callback_data=f"edit_title_{task_id}")],
        [InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_description_{task_id}")],
        [InlineKeyboardButton(text="📅 Дедлайн", callback_data=f"edit_deadline_{task_id}")],
        [InlineKeyboardButton(text="🎯 Приоритет", callback_data=f"edit_priority_{task_id}")],
        [InlineKeyboardButton(text="🔙 К задаче", callback_data=f"task_{task_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)