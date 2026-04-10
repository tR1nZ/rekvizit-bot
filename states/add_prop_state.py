from aiogram.fsm.state import State, StatesGroup


class AddPropState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_box_number = State()
    waiting_for_quantity = State()
    waiting_for_gender_group = State()
    waiting_for_item_type = State()
    waiting_for_photo = State()