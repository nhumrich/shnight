import asyncio
import json
import random
from aiohttp_sse import sse_response
from aiohttp import web
from shnight.game import Game
from shnight.user import User

games = {}
players = {}


async def new_game(request):
    data = await request.json()
    user_name = data['user_name']
    user = User(user_name)
    players[user.id] = user

    game_number = random.randint(100000, 999999)
    while game_number in games:
        game_number = random.randint(100000, 999999)

    games[game_number] = Game(user.id)
    return web.json_response({
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
        if game.status == 'open' and len(game.players) <= 10:
            game.add_player(user.id)
            return web.json_response({
                'exists': True,
                'user_id': user.id,
                'game_id': game_number,
                'owner_id': game.owner_id,
                'players': game.get_players()
            })
    return web.json_response({'exists': False})


async def game_state(request):
    game_id = int(request.match_info.get('game_id'))
    user_id = request.query.get('user_id')
    if game_id in games:
        _players = await _get_players_names(games[game_id], user_id)
        event = {
            'players': _players,
            'owner_id': games[game_id].owner_id,
            'status': games[game_id].status
        }
        return web.json_response(event)
    return web.json_response({'players': [], 'owner_id': ''})


async def game_id_exists(request):
    data = await request.json()
    game_number = int(data['game_id'])
    if game_number in games:
        game = games[game_number]
        return web.json_response({
            'status': game.status
        })
    return web.json_response({'status': None})


async def leave_game(request):
    data = await request.json()
    user_id = data['user_id']
    game_number = int(data['game_id'])
    game = games[game_number]
    game.remove_player(user_id)
    if len(game.players) == 0:
        del game
    return web.json_response({'success': True})


async def start_game(request):
    game_id = int(request.match_info.get('game_id'))
    user_id = request.query.get('user')
    game = games.get(game_id)
    if game.status != 'open':
        return web.HTTPConflict()
    if game is None or game.owner_id != user_id:
        return web.HTTPUnauthorized()
    game.generate_roles()
    game.generate_seating()
    return web.HTTPNoContent()


async def end_game(request):
    game_id = int(request.match_info.get('game_id'))
    user_id = request.query.get('user')
    game = games.get(game_id)
    if game.status != 'closed' or user_id != game.owner_id:
        return web.HTTPConflict()
    game.end()
    return web.HTTPNoContent()


async def _get_players_names(game, user_id):
    _players = []
    requester_role = game.get_role(user_id)
    can_see_roles = False
    if requester_role == 1 or (requester_role == 2 and len(game.players) < 7):
        can_see_roles = True
    for player_id in game.players:
        _players.append({
            'id': player_id,
            'name': players[player_id].name,
            'role': game.get_role(player_id) if can_see_roles else 0,
            'seat': game.get_seat(player_id)
        })
    return _players


async def run_always():
    while True:
        await asyncio.sleep(3)
        for gid, game in games.items():
            queues = []
            for pid in game.players:
                player = players[pid]
                queues.append(player.queue)
                _players = await _get_players_names(games[gid], pid)

                event = {
                    'players': _players,
                    'owner_id': games[gid].owner_id,
                    'status': games[gid].status
                }
                await player.queue.put(event)


async def events(request):
    user_id = request.query.get('user')
    if user_id in players:
        event_queue = players[user_id].queue
        async with sse_response(request) as resp:
            while True:
                event = await event_queue.get()
                if event is None:
                    del players[user_id]
                    event = 'close'
                await resp.send(json.dumps(event))
                event_queue.task_done()



