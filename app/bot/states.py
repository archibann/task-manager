from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    """Состояния для создания новой задачи"""
    title = State()
    description = State()
    deadline = State()
    priority = State()


class EditTaskStates(StatesGroup):
    """Состояния для редактирования задачи"""
    title = State()
    description = State()
    deadline = State()
    priority = State()