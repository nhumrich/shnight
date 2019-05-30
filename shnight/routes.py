from aiohttp import web
from shnight.controller import new_game, start_game, leave_game, \
    events, join_game, game_id_exists, game_state, end_game
routes = [
    web.post('/api/new', new_game),
    web.post('/api/game_exists', game_id_exists),
    web.get('/api/game_state/{game_id}', game_state),
    web.post('/api/leave', leave_game),
    web.post('/api/join', join_game),
    web.get('/api/start/{game_id}', start_game),
    web.get('/api/end/{game_id}', end_game),
    web.get('/api/events', events),
]
