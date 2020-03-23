import asyncio
import json
import random
from starlette.responses import StreamingResponse
from starlette.responses import JSONResponse
from shnight.game import Game
from shnight.user import User

games = {}
players = {}


def _get_players_names(game, user_id):
    _players = []
    requester_role = game.get_role(user_id)
    for player_id in game.players:
        _role = 0
        if requester_role == 2:
            if player_id == user_id:
                _role = 2
            elif player_id in game.fascists:
                if len(game.players) < 7:
                    _role = 1
        elif requester_role == 1:
            if player_id == user_id or player_id in game.fascists:
                _role = 1
            elif player_id == game.hitler:
                _role = 2

        _players.append({
            'id': player_id,
            'name': players[player_id].name,
            'role': _role,
            'seat': game.get_seat(player_id)
        })
    return _players


def _game_state(game, user_id):
    _players = _get_players_names(game, user_id)
    event = {
        'players': _players,
        'owner_id': game.owner_id,
        'status': game.status,
        'elections_open': game.elections,
        'votes': {
            'ja': game.votes['ja'],
            'nein': game.votes['nein'],
            'total': f'{len(game.votes["ja"]) + len(game.votes["nein"])} / {len(game.players)}'
        }
    }
    return event


async def new_game(request):
    data = await request.json()
    user_name = data['user_name']
    user = User(user_name)
    players[user.id] = user

    game_number = random.randint(100000, 999999)
    while game_number in games:
        game_number = random.randint(100000, 999999)

    games[game_number] = Game(user.id)
    user.game_id = game_number
    return JSONResponse({
            'user_id': user.id,
            'game_id': game_number,
            'owner_id': games[game_number].owner_id,
            'players': games[game_number].get_players()
        })


async def join_game(request):
    data = await request.json()
    user_name = data['user_name']
    user = User(user_name)
    players[user.id] = user
    game_number = int(data['game_id'])

    if game_number in games:
        game = games[game_number]
        user.game_id = game_number
        if game.status == 'open' and len(game.players) <= 10:
            game.add_player(user.id)
            return JSONResponse({
                'exists': True,
                'user_id': user.id,
                'game_id': game_number,
                'owner_id': game.owner_id,
                'players': game.get_players()
            })
    return JSONResponse({'exists': False})


async def toggle_elections(request):
    game_id = int(request.path_params.get('game_id'))
    if game_id in games:
        games[game_id].toggle_elections()
    return JSONResponse({'success': True})


async def cast_vote(request):
    game_id = int(request.path_params.get('game_id'))
    data = await request.json()
    vote = data['vote_for'] == 'ja'
    user_id = data['user_id']
    if game_id in games:
        games[game_id].add_vote(user_id, vote)


async def game_state(request):
    game_id = int(request.path_params.get('game_id'))
    user_id = request.query_params.get('user_id')
    if game_id in games:
        event = _game_state(games[game_id], user_id)
        return JSONResponse(event)
    return JSONResponse({'players': [], 'owner_id': ''})


async def game_id_exists(request):
    data = await request.json()
    game_number = int(data['game_id'])
    if game_number in games:
        game = games[game_number]
        return JSONResponse({
            'status': game.status
        })
    return JSONResponse({'status': None})


async def leave_game(request):
    data = await request.json()
    user_id = data['user_id']
    game_number = int(data['game_id'])
    game = games[game_number]
    game.remove_player(user_id)
    if len(game.players) == 0:
        del game
    return JSONResponse({'success': True})


async def start_game(request):
    game_id = int(request.path_params.get('game_id'))
    user_id = request.query_params.get('user')
    game = games.get(game_id)
    if game.status != 'open':
        return JSONResponse({'error': 'Conflict'}, status_code=409)
    if game is None or game.owner_id != user_id:
        return JSONResponse({'error': 'Not Authorized'}, status_code=401)
    game.generate_roles()
    game.generate_seating()
    return JSONResponse({}, status_code=204)


async def end_game(request):
    game_id = int(request.path_params.get('game_id'))
    user_id = request.query_params.get('user')
    game = games.get(game_id)
    if game.status != 'closed' or user_id != game.owner_id:
        return JSONResponse({'error': 'Conflict'}, status_code=409)
    game.end()
    return JSONResponse({}, status_code=204)


async def run_always():
    while True:
        await asyncio.sleep(3)
        for game_id, game in games.items():
            queues = []
            for user_id in game.players:
                player = players[user_id]
                queues.append(player.queue)
                event = _game_state(games[game_id], user_id)
                await player.queue.put(event)


def _encode(data):
    message = f"data: {data}"
    message += "\r\n\r\n"
    return message.encode("utf-8")


async def events(request):
    user_id = request.query_params.get('user')
    if user_id in players:
        async def event_stream():
            while True:
                event = _game_state(games[players[user_id].game_id], user_id)
                yield _encode(json.dumps(event))
                await asyncio.sleep(1)

        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(event_stream(), headers=headers)
