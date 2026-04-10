from aiogram.fsm.state import State, StatesGroup


class IssueState(StatesGroup):
    waiting_for_team_name = State()