from shnight.game import Game
from shnight.user import User
from shnight.controller import _game_state, players
import random


def create_user(name):
    user = User(name)
    players[user.id] = user
    return user


def check_visibility(game):
    player_count = len(game.players)
    for player in game.players:
        state = _game_state(game, player)
        for record in state['players']:
            if player == game.hitler:
                if player == record['id']:
                    assert record['role'] == 2
                elif record['id'] in game.fascists:
                    if player_count < 7:
                        assert record['role'] == 1
                    else:
                        assert record['role'] == 0
                else:
                    assert record['role'] == 0

            elif player in game.fascists:
                if player == record['id']:
                    assert record['role'] == 1
                elif record['id'] in game.fascists:
                    assert record['role'] == 1
                elif record['id'] == game.hitler:
                    assert record['role'] == 2
                else:
                    assert record['role'] == 0

            else:
                assert record['role'] == 0


def create_game(name='Master', player_count=5):
    owner = create_user(name)
    game = Game(owner.id)
    for n in range(player_count - 1):
        user = create_user(f'bob{n}')
        game.add_player(user.id)
    return game, owner


def test_game():
    game, user = create_game('Skyler')
    # assert new game, and owner
    assert game.owner_id == user.id
    assert user.id in game.players

    # assert other game doesn't affect first game
    game2, user2 = create_game('Jacen')
    assert game2.owner_id == user2.id
    assert user2.id in game2.players and user2.id not in game.players

    # make sure we have enough players
    assert len(game.players) == 5

    # ensure our game hasn't been started yet
    assert game.fascists == []
    assert game.hitler is None

    # start game/generate roles
    game.generate_roles()
    game.generate_seating()

    # make sure that there are proper roles assigned
    assert game.get_role(game.fascists[0]) == 1
    assert game.get_role(game.hitler) == 2
    assert len(game.fascists) == 1
    assert len(game.players) == 5
    check_visibility(game)

    # make sure we have the right roles for 6 players
    game, _ = create_game(player_count=6)
    game.generate_roles()
    game.generate_seating()
    assert len(game.fascists) == 1
    assert len(game.players) == 6
    check_visibility(game)

    # make sure we have the right roles for 7 players
    game, _ = create_game(player_count=7)
    game.generate_roles()
    game.generate_seating()
    assert len(game.fascists) == 2
    assert len(game.players) == 7
    check_visibility(game)

    # make sure we have the right roles for 8 players
    game, _ = create_game(player_count=8)
    game.generate_roles()
    game.generate_seating()
    assert len(game.fascists) == 2
    assert len(game.players) == 8
    check_visibility(game)

    # make sure we have the right roles for 9 players
    game, _ = create_game(player_count=9)
    game.generate_roles()
    game.generate_seating()
    assert len(game.fascists) == 3
    assert len(game.players) == 9
    check_visibility(game)

    # make sure we have the right roles for 10 players
    game, _ = create_game(player_count=10)
    game.generate_roles()
    game.generate_seating()
    assert len(game.fascists) == 3
    assert len(game.players) == 10
    check_visibility(game)

    # test seating chart
    assert len(game.seating) == 10


def test_vote():
    game, _ = create_game()
    player = None
    for player in game.players:
        game.add_vote(player, random.choice([True, False]))
        state = _game_state(game, player)

test_game()
test_vote()
