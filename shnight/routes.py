from starlette.responses import JSONResponse

from shnight.controller import new_game, start_game, leave_game, \
    events, join_game, game_id_exists, game_state, end_game


async def homepage(request):
    return JSONResponse({'hello': 'world'})


def registration(app):
    app.add_route('/', homepage, methods=['GET']),
    app.add_route('/api/new', new_game, methods=['POST']),
    app.add_route('/api/game_exists', game_id_exists, methods=['POST']),
    app.add_route('/api/game_state/{game_id}', game_state, methods=['GET']),
    app.add_route('/api/leave', leave_game, methods=['POST']),
    app.add_route('/api/join', join_game, methods=['POST']),
    app.add_route('/api/start/{game_id}', start_game, methods=['GET']),
    app.add_route('/api/end/{game_id}', end_game, methods=['GET']),
    app.add_route('/api/events', events, methods=['GET']),
    return app
