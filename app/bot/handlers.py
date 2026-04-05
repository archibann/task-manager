import asyncio
from datetime import datetime, date
from typing import Optional
from contextlib import contextmanager

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.database import SessionLocal
from app import crud
from app.enums import PriorityEnum
from app.bot.keyboards import (
    get_main_keyboard,
    get_task_list_keyboard,
    get_task_detail_keyboard,
    get_priority_keyboard,
    get_confirm_delete_keyboard,
    get_edit_keyboard,
)
from app.bot.states import AddTaskStates, EditTaskStates
from app.bot.utils import run_sync

router = Router()


@contextmanager
def get_db():
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== КОМАНДЫ ====================

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    text = (
        "👋 Привет! Я бот для управления задачами.\n\n"
        "📌 <b>Доступные команды:</b>\n"
        "/tasks - список всех задач\n"
        "/add - добавить новую задачу\n"
        "/help - помощь\n\n"
        "Или используйте кнопки ниже 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    text = (
        "📖 <b>Справка по командам:</b>\n\n"
        "/start - Главное меню\n"
        "/tasks - Список всех задач\n"
        "/add - Добавить новую задачу\n\n"
        "🎯 <b>Приоритеты задач:</b>\n"
        "🔴 Высокий\n"
        "🟡 Средний\n"
        "🟢 Низкий\n\n"
        "💡 Используйте inline-кнопки для навигации!"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Показать список всех задач"""
    try:
        def get_tasks_sync():
            with get_db() as db:
                return crud.get_tasks(db, skip=0, limit=50)
        
        tasks = await run_sync(get_tasks_sync)
        
        if not tasks:
            await message.answer(
                "📋 Список задач пуст.\nНажмите ➕ чтобы добавить первую задачу!",
                reply_markup=get_main_keyboard()
            )
            return
        
        text = f"📋 <b>Все задачи ({len(tasks)}):</b>\n\n"
        for i, task in enumerate(tasks, 1):
            status = "✅" if task.completed else "⏳"
            priority_emoji = {
                PriorityEnum.high: "🔴",
                PriorityEnum.medium: "🟡",
                PriorityEnum.low: "🟢",
            }.get(task.priority, "")
            text += f"{i}. {status} {priority_emoji} {task.title}\n"
        
        await message.answer(text, reply_markup=get_task_list_keyboard(tasks), parse_mode="HTML")
    except asyncio.TimeoutError:
        await message.answer("⏱ Превышено время ожидания. Попробуйте ещё раз.")


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """Начало создания новой задачи"""
    await state.set_state(AddTaskStates.title)
    await message.answer(
        "📝 <b>Создание новой задачи</b>\n\n"
        "Введите название задачи:",
        parse_mode="HTML"
    )


# ==================== CALLBACK ОБРАБОТЧИКИ ====================

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "👋 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tasks_"))
async def callback_tasks_list(callback: CallbackQuery):
    """Показать список задач с фильтром"""
    try:
        filter_type = callback.data.split("_")[1]
        
        def get_filtered_tasks():
            with get_db() as db:
                if filter_type == "completed":
                    return crud.get_tasks(db, completed=True, limit=50), "✅ <b>Выполненные задачи:</b>"
                elif filter_type == "pending":
                    return crud.get_tasks(db, completed=False, limit=50), "⏳ <b>Задачи в работе:</b>"
                else:
                    return crud.get_tasks(db, limit=50), "📋 <b>Все задачи:</b>"
        
        tasks, title = await run_sync(get_filtered_tasks)
        
        if not tasks:
            await callback.message.edit_text(
                "📭 Задачи не найдены.",
                reply_markup=get_main_keyboard()
            )
            await callback.answer()
            return
        
        text = f"{title}\n\n"
        for i, task in enumerate(tasks, 1):
            status = "✅" if task.completed else "⏳"
            priority_emoji = {
                PriorityEnum.high: "🔴",
                PriorityEnum.medium: "🟡",
                PriorityEnum.low: "🟢",
            }.get(task.priority, "")
            text += f"{i}. {status} {priority_emoji} {task.title}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_task_list_keyboard(tasks),
            parse_mode="HTML"
        )
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


@router.callback_query(F.data.startswith("task_"))
async def callback_task_detail(callback: CallbackQuery):
    """Показать детали задачи"""
    try:
        task_id = int(callback.data.split("_")[1])
        
        def get_task_details():
            with get_db() as db:
                return crud.get_task(db, task_id)
        
        task = await run_sync(get_task_details)
        
        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return
        
        status = "✅ Выполнена" if task.completed else "⏳ В работе"
        priority_text = {
            PriorityEnum.high: "🔴 Высокий",
            PriorityEnum.medium: "🟡 Средний",
            PriorityEnum.low: "🟢 Низкий",
        }.get(task.priority, "Не указан")
        
        deadline_text = task.deadline.strftime("%d.%m.%Y") if task.deadline else "Не указан"
        
        text = (
            f"📌 <b>Задача #{task.id}</b>\n\n"
            f"<b>Название:</b> {task.title}\n"
            f"<b>Описание:</b> {task.description or 'Нет описания'}\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Приоритет:</b> {priority_text}\n"
            f"<b>Дедлайн:</b> {deadline_text}\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_task_detail_keyboard(task.id, task.completed),
            parse_mode="HTML"
        )
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


@router.callback_query(F.data == "add_task")
async def callback_add_task(callback: CallbackQuery, state: FSMContext):
    """Начало создания задачи через кнопку"""
    await state.set_state(AddTaskStates.title)
    await callback.message.edit_text(
        "📝 <b>Создание новой задачи</b>\n\n"
        "Введите название задачи:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("complete_"))
async def callback_complete_task(callback: CallbackQuery):
    """Отметить задачу как выполненную/невыполненную"""
    try:
        task_id = int(callback.data.split("_")[1])
        
        def toggle_complete():
            with get_db() as db:
                task = crud.get_task(db, task_id)
                if not task:
                    return None
                
                if task.completed:
                    task.completed = False
                    action = "возвращена в работу"
                else:
                    task.completed = True
                    action = "отмечена как выполненная"
                
                db.commit()
                db.refresh(task)
                return task, action
        
        result = await run_sync(toggle_complete)
        
        if result is None:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return
        
        task, action = result
        await callback.answer(f"✅ Задача {action}!")
        
        status = "✅ Выполнена" if task.completed else "⏳ В работе"
        priority_text = {
            PriorityEnum.high: "🔴 Высокий",
            PriorityEnum.medium: "🟡 Средний",
            PriorityEnum.low: "🟢 Низкий",
        }.get(task.priority, "Не указан")
        
        deadline_text = task.deadline.strftime("%d.%m.%Y") if task.deadline else "Не указан"
        
        text = (
            f"📌 <b>Задача #{task.id}</b>\n\n"
            f"<b>Название:</b> {task.title}\n"
            f"<b>Описание:</b> {task.description or 'Нет описания'}\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Приоритет:</b> {priority_text}\n"
            f"<b>Дедлайн:</b> {deadline_text}\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_task_detail_keyboard(task.id, task.completed),
            parse_mode="HTML"
        )
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


@router.callback_query(F.data.startswith("delete_"))
async def callback_delete_task(callback: CallbackQuery):
    """Запрос на удаление задачи"""
    try:
        task_id = int(callback.data.split("_")[1])
        
        def get_task_for_delete():
            with get_db() as db:
                return crud.get_task(db, task_id)
        
        task = await run_sync(get_task_for_delete)
        
        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"🗑 <b>Удаление задачи</b>\n\n"
            f"Вы уверены, что хотите удалить задачу:\n"
            f"<b>«{task.title}»</b>?",
            reply_markup=get_confirm_delete_keyboard(task_id),
            parse_mode="HTML"
        )
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


@router.callback_query(F.data.startswith("confirm_delete_"))
async def callback_confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления задачи"""
    try:
        task_id = int(callback.data.split("_")[2])
        
        def delete_task_sync():
            with get_db() as db:
                return crud.delete_task(db, task_id)
        
        task = await run_sync(delete_task_sync)
        
        if task:
            await callback.message.edit_text(
                f"✅ Задача <b>«{task.title}»</b> удалена!",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "❌ Задача не найдена",
                reply_markup=get_main_keyboard()
            )
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


@router.callback_query(F.data.startswith("edit_"))
async def callback_edit_task(callback: CallbackQuery, state: FSMContext):
    """Редактирование задачи"""
    try:
        data = callback.data.split("_")
        
        if len(data) == 2:
            task_id = int(data[1])
            
            def get_task_for_edit():
                with get_db() as db:
                    return crud.get_task(db, task_id)
            
            task = await run_sync(get_task_for_edit)
            
            if not task:
                await callback.answer("❌ Задача не найдена", show_alert=True)
                return
            
            await callback.message.edit_text(
                f"✏️ <b>Редактирование задачи</b>\n\n"
                f"Задача: <b>{task.title}</b>\n\n"
                f"Выберите, что хотите изменить:",
                reply_markup=get_edit_keyboard(task_id),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        if len(data) == 3:
            field = data[1]
            task_id = int(data[2])
            
            await state.update_data(edit_task_id=task_id)
            
            if field == "title":
                await state.set_state(EditTaskStates.title)
                await callback.message.edit_text(
                    "📝 Введите новое название задачи:",
                    parse_mode="HTML"
                )
            elif field == "description":
                await state.set_state(EditTaskStates.description)
                await callback.message.edit_text(
                    "📄 Введите новое описание задачи:",
                    parse_mode="HTML"
                )
            elif field == "deadline":
                await state.set_state(EditTaskStates.deadline)
                await callback.message.edit_text(
                    "📅 Введите новую дату дедлайна (ДД.ММ.ГГГГ):",
                    parse_mode="HTML"
                )
            elif field == "priority":
                await state.set_state(EditTaskStates.priority)
                await callback.message.edit_text(
                    "🎯 Выберите новый приоритет:",
                    reply_markup=get_priority_keyboard(),
                    parse_mode="HTML"
                )
            
            await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


# ==================== FSM - СОЗДАНИЕ ЗАДАЧИ ====================

@router.message(AddTaskStates.title)
async def process_add_title(message: Message, state: FSMContext):
    """Обработка названия новой задачи"""
    await state.update_data(title=message.text)
    await state.set_state(AddTaskStates.description)
    await message.answer(
        "📄 Введите описание задачи (или нажмите /skip чтобы пропустить):",
        parse_mode="HTML"
    )


@router.message(AddTaskStates.description)
async def process_add_description(message: Message, state: FSMContext):
    """Обработка описания новой задачи"""
    if message.text != "/skip":
        await state.update_data(description=message.text)
    await state.set_state(AddTaskStates.deadline)
    await message.answer(
        "📅 Введите дату дедлайна (ДД.ММ.ГГГГ) или /skip:",
        parse_mode="HTML"
    )


@router.message(AddTaskStates.deadline)
async def process_add_deadline(message: Message, state: FSMContext):
    """Обработка дедлайна новой задачи"""
    if message.text != "/skip":
        try:
            deadline = datetime.strptime(message.text, "%d.%m.%Y").date()
            await state.update_data(deadline=deadline)
        except ValueError:
            await message.answer("❌ Неверный формат даты. Введите ДД.ММ.ГГГГ:")
            return
    
    await state.set_state(AddTaskStates.priority)
    await message.answer(
        "🎯 Выберите приоритет:",
        reply_markup=get_priority_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(AddTaskStates.priority, F.data.startswith("priority_"))
async def process_add_priority(callback: CallbackQuery, state: FSMContext):
    """Обработка приоритета и создание задачи"""
    try:
        priority_value = callback.data.split("_")[1]
        priority = None if priority_value == "none" else PriorityEnum(priority_value)
        
        data = await state.get_data()
        title = data.get("title")
        description = data.get("description")
        deadline = data.get("deadline")
        
        def create_task_sync():
            with get_db() as db:
                return crud.create_task(
                    db,
                    title=title,
                    description=description,
                    deadline=deadline,
                    priority=priority
                )
        
        task = await run_sync(create_task_sync)
        
        await callback.message.edit_text(
            f"✅ <b>Задача создана!</b>\n\n"
            f"📌 #{task.id} - {task.title}\n"
            f"📄 {task.description or 'Без описания'}\n"
            f"📅 Дедлайн: {task.deadline.strftime('%d.%m.%Y') if task.deadline else 'Не указан'}\n"
            f"🎯 Приоритет: {priority_value if priority else 'Не указан'}",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        
        await state.clear()
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


# ==================== FSM - РЕДАКТИРОВАНИЕ ЗАДАЧИ ====================

@router.message(EditTaskStates.title)
async def process_edit_title(message: Message, state: FSMContext):
    """Обработка нового названия"""
    try:
        data = await state.get_data()
        task_id = data.get("edit_task_id")
        
        def update_title():
            with get_db() as db:
                crud.update_task(db, task_id, title=message.text)
                return crud.get_task(db, task_id)
        
        task = await run_sync(update_title)
        
        await message.answer(
            f"✅ Название обновлено!\n\n📌 <b>{task.title}</b>",
            reply_markup=get_edit_keyboard(task_id),
            parse_mode="HTML"
        )
        await state.clear()
    except asyncio.TimeoutError:
        await message.answer("⏱ Превышено время ожидания. Попробуйте ещё раз.")


@router.message(EditTaskStates.description)
async def process_edit_description(message: Message, state: FSMContext):
    """Обработка нового описания"""
    try:
        data = await state.get_data()
        task_id = data.get("edit_task_id")
        
        def update_description():
            with get_db() as db:
                crud.update_task(db, task_id, description=message.text)
                return crud.get_task(db, task_id)
        
        task = await run_sync(update_description)
        
        await message.answer(
            f"✅ Описание обновлено!\n\n📄 {task.description or 'Нет описания'}",
            reply_markup=get_edit_keyboard(task_id),
            parse_mode="HTML"
        )
        await state.clear()
    except asyncio.TimeoutError:
        await message.answer("⏱ Превышено время ожидания. Попробуйте ещё раз.")


@router.message(EditTaskStates.deadline)
async def process_edit_deadline(message: Message, state: FSMContext):
    """Обработка нового дедлайна"""
    try:
        data = await state.get_data()
        task_id = data.get("edit_task_id")
        
        try:
            deadline = datetime.strptime(message.text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("❌ Неверный формат даты. Введите ДД.ММ.ГГГГ:")
            return
        
        def update_deadline():
            with get_db() as db:
                crud.update_task(db, task_id, deadline=deadline)
                return crud.get_task(db, task_id)
        
        task = await run_sync(update_deadline)
        
        await message.answer(
            f"✅ Дедлайн обновлен!\n\n📅 {task.deadline.strftime('%d.%m.%Y')}",
            reply_markup=get_edit_keyboard(task_id),
            parse_mode="HTML"
        )
        await state.clear()
    except asyncio.TimeoutError:
        await message.answer("⏱ Превышено время ожидания. Попробуйте ещё раз.")


@router.callback_query(EditTaskStates.priority, F.data.startswith("priority_"))
async def process_edit_priority(callback: CallbackQuery, state: FSMContext):
    """Обработка нового приоритета"""
    try:
        priority_value = callback.data.split("_")[1]
        priority = None if priority_value == "none" else PriorityEnum(priority_value)
        
        data = await state.get_data()
        task_id = data.get("edit_task_id")
        
        def update_priority():
            with get_db() as db:
                crud.update_task(db, task_id, priority=priority)
                return crud.get_task(db, task_id)
        
        task = await run_sync(update_priority)
        
        priority_text = {
            PriorityEnum.high: "🔴 Высокий",
            PriorityEnum.medium: "🟡 Средний",
            PriorityEnum.low: "🟢 Низкий",
        }.get(task.priority, "Не указан")
        
        await callback.message.edit_text(
            f"✅ Приоритет обновлен!\n\n🎯 {priority_text}",
            reply_markup=get_edit_keyboard(task_id),
            parse_mode="HTML"
        )
        
        await state.clear()
        await callback.answer()
    except asyncio.TimeoutError:
        await callback.answer("⏱ Превышено время ожидания", show_alert=True)


# ==================== FALLBACK ====================

@router.message()
async def fallback_handler(message: Message, state: FSMContext):
    """Обработчик для неизвестных сообщений"""
    current_state = await state.get_state()
    if current_state:
        await message.answer(
            "⚠️ Пожалуйста, следуйте инструкциям или нажмите /cancel для отмены."
        )
    else:
        await message.answer(
            "🤔 Не понимаю команду.\nИспользуйте /help для справки.",
            reply_markup=get_main_keyboard()
        )