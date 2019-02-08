import asyncio
import random
from asyncio import Queue
from uuid import uuid4

from aiohttp import web
from aiohttp.web import Response, Request
from aiohttp_sse import sse_response
from datetime import datetime
from copy import copy


games = {10000: {'players': [], 'owner_id': str(uuid4()), 'status': 'closed'}}
players = {}


async def close_game(game_id):
    pass


async def push_game_update(game_id):
    pass


async def run_always():
    while True:
        await asyncio.sleep(3)
        for gid, game in games.items():
            if game.get('status') in ('closed', 'starting'):
                continue
            queues = []
            players_names = []
            for pid in game.get('players'):
                player = players[pid]
                queues.append(player['queue'])
                players_names.append(player['name'])

            event = 'Current Players: <br>'
            for name in players_names:
                event += name + '<br>'
            for q in queues:
                await q.put(event)


async def on_startup(app):
    asyncio.create_task(run_always())


async def events(request):
    user_id = request.query.get('user')
    event_queue = players[user_id]['queue']
    async with sse_response(request) as resp:
        while True:
            event = await event_queue.get()
            if event is None:
                del players[user_id]
                event = 'close'
            print(event)
            await resp.send(event)
            event_queue.task_done()


async def new_game(request):
    user_id = request.query.get('user')
    game_number = 10000
    while game_number in games:
        game_number = random.randint(10000, 99999)

    games[game_number] = {'players': [user_id], 'owner_id': user_id, 'status': 'open'}

    return web.HTTPFound(location=f'/game/{game_number}?user={user_id}')


async def start_game(request):
    game_id = int(request.match_info.get('game_id'))
    user_id = request.query.get('user')
    game = games.get(game_id)
    if game is None or game.get('owner_id') != user_id:
        return web.HTTPUnauthorized()

    cur_players = copy(game.get('players'))
    game['status'] = 'starting'

    num_of_players = len(cur_players)
    if num_of_players == 6:
        num_of_fasc = 1
    else:
        num_of_fasc = num_of_players // 3

    fasc = []

    for _ in range(num_of_fasc):
        p = random.choice(cur_players)
        fasc.append(p)
        cur_players.remove(p)

    hitty = random.choice(cur_players)
    cur_players.remove(hitty)

    order = copy(game.get('players'))
    random.shuffle(order)
    seats = '<br><br> Seating positions are:<br>'
    for i, pid in enumerate(order):
        player = players.get(pid)
        seats += str(i + 1) + ': ' + player.get('name') + '<br>'

    for pid in game['players']:
        player = players.get(pid)
        q = player['queue']
        if pid in fasc:
            role = 'Fascist'
        elif pid == hitty:
            role = 'Hitty'
        else:
            role = 'Liberal'

        event = f'You are <b>{role}</b>! <br><br>'
        if role == 'Fascist' or (role == 'Hitty' and num_of_players < 7):
            event += 'Your fellow fascists are: <br>'
            for f in fasc:
                p2 = players.get(f)
                if p2 != pid:
                    event += p2['name'] + '<br>'
            if role != 'Hitty':
                event += '<br> Hitty is: ' + players.get(hitty)['name'] + '<br>'

        event += seats
        await q.put(event)

    game['status'] = 'closed'

    return web.HTTPNoContent()


async def leave_game(request):
    user_id = request.query.get('user')
    game_id = int(request.match_info.get('game_id'))
    user = players.get(user_id)
    if user is None:
        return web.HTTPFound(location='/clear')
    game = games.get(game_id)
    if game is None:
        return web.HTTPFound(location=f'/lobby?user{user_id}')
    if user_id in game.get('players'):
        if user_id == game.get('owner_id'):
            game['status'] = 'closed'
            await close_game(game_id)
        else:
            cur_players = game.get('players')
            cur_players.remove(user_id)
            await push_game_update(game_id)

    return web.HTTPFound(location=f'/lobby?user={user_id}')


async def join_game(request):
    user_id = request.query.get('user')
    params = await request.post()
    game_id = int(params.get('game_id'))
    game = games.get(game_id)
    if game is not None and game.get('status') == 'open':
        game.get('players').append(user_id)
        await push_game_update(game_id)
        return web.HTTPFound(location=f'/game/{game_id}?user={user_id}')
    else:
        return web.HTTPFound(location=f'/lobby?user={user_id}')


async def hello(request):
    loop = request.app.loop
    async with sse_response(request) as resp:
        while True:
            data = 'Server Time : {}'.format(datetime.now())
            print(data)
            await resp.send(data)
            await asyncio.sleep(1, loop=loop)
    return resp


async def index(request):
    d = """
        <html>
        <body>
            <script>
                pid = localStorage.getItem("player_id")
                if (pid != null) {
                    window.location.href = `/lobby?user=${pid}`;
                }
            </script>
        
            <form action="/new_player" method="post">
              Name:<br><br>
              <input type="text" name="name"><br><br><br>
              <input type="submit" value="Submit">
              
            </form>
        </body>
        </html>
    """
    return Response(text=d, content_type='text/html')


async def handle_clear(request: Request):
    d = """
    <html>
        <body>
            <script>
                localStorage.removeItem("player_id")
                window.location.href = `/`
            </script>
        </body>
        </html>
    """
    return Response(text=d, content_type='text/html')


async def new_player(request: Request):
    params = await request.post()
    name = params.get('name')
    if name is None:
        return web.HTTPBadRequest()

    player_id = str(uuid4())
    event_queue = Queue()
    players[player_id] = {'name': name, 'queue': event_queue, 'done': False}
    d = f"""
        <html>
        <body>
            <script>
                localStorage.setItem("player_id", "{player_id}")
                window.location.href = "/lobby?user={player_id}"
            </script>
        </body>
        </html>    
    """
    return Response(text=d, content_type='text/html')


async def handle_lobby(request):
    user_id = request.query.get('user')
    user = players.get(user_id)
    if user is None:
        return web.HTTPFound('/clear')

    d = f"""
        <html>
        <body>
            <h1>Welcome {user['name']}</h1><br>
            <form action="/new?user={user_id}" method="post">
              <input type="submit" value="New game">
              
            </form>
            <form action="/join?user={user_id}" method="post">
              Game Number:<br><br>
              <input type="text" name="game_id"><br><br><br>
              <input type="submit" value="Join Game">
              
            </form>
        </body>
    </html>
    """
    return Response(text=d, content_type='text/html')


async def handle_game(request: Request):
    game_id = int(request.match_info.get('game_id'))
    user_id = request.query.get('user')
    if games.get(game_id) is None:
        return web.HTTPFound(f'/lobby?user={user_id}')
    user = players.get(user_id)
    if user is None:
        return web.HTTPFound('/clear')
    d = f"""
            <html>
            <body>

                <script>
                    var sse = new EventSource("/events?user={user_id}");
                    sse.onmessage = function(e) {{
                        if (e.data === 'close') {{
                            sse.close()
                        }} else {{
                            document.getElementById('response').innerHTML = e.data
                        }}
                    }}
                </script>
                <h1>Welcome {user['name']}</h1><br>
                <h2>You are in game number {game_id}</h2><br><br>
                <div id="response"></div><br><br>
                <form  action="/leave/{game_id}?user={user_id}" method="post"><input type="submit" value="Leave Game"></form>
        """

    if games[game_id]['owner_id'] == user_id:
        d += f"""
                <button type="button" onclick="fetch('/start/{game_id}?user={user_id}')">Start</button>
            </body>
        </html>
        """

    return web.Response(text=d, content_type='text/html')


def main():
    app = web.Application()
    app.add_routes([web.post('/new', new_game),
                    web.get('/start/{game_id}', start_game),
                    web.post('/leave/{game_id}', leave_game),
                    web.get('/events', events),
                    web.post('/join', join_game),
                    web.get('/lobby', handle_lobby),
                    web.get('/game/{game_id}', handle_game),
                    web.get('/', index),
                    web.get('/clear', handle_clear),
                    web.post('/new_player', new_player)
                    ])
    app.on_startup.append(on_startup)
    web.run_app(app)
