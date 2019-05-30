from shnight import __version__
from shnight.game import Game
from shnight.user import User


def test_game():
    user = User('Skyler')
    g = Game(user.id)
    # assert new game, and owner
    assert g.owner_id == user.id
    assert g.players == [user.id]

    # assert other game doesn't affect first game
    u2 = User('Jacen')
    g2 = Game(u2.id)
    assert g2.owner_id == u2.id
    assert g.players == [user.id]

    # add all players
    for n in range(4):
        u = User(f'bob{n}')
        g.add_player(u.id)

    # make sure we have enough players
    assert len(g.players) == 5

    # ensure our game hasn't been started yet
    assert g.fascists == []
    assert g.hitler is None

    # start game/generate roles
    g.generate_roles()

    # make sure that there are proper roles assigned
    assert g.get_role(g.fascists[0]) == 1
    assert g.get_role(g.hitler) == 2
    assert len(g.fascists) == 1
    assert len(g.players) == 5

    # make sure we have the right roles for 6 players
    u = User('bob5')
    g.add_player(u.id)
    g.generate_roles()
    assert len(g.fascists) == 1
    assert len(g.players) == 6

    # make sure we have the right roles for 7 players
    u = User('bob6')
    g.add_player(u.id)
    g.generate_roles()
    assert len(g.fascists) == 2
    assert len(g.players) == 7

    # make sure we have the right roles for 8 players
    u = User('bob7')
    g.add_player(u.id)
    g.generate_roles()
    assert len(g.fascists) == 2
    assert len(g.players) == 8

    # make sure we have the right roles for 9 players
    u = User('bob7')
    g.add_player(u.id)
    g.generate_roles()
    assert len(g.fascists) == 3
    assert len(g.players) == 9

    # make sure we have the right roles for 10 players
    u = User('bob8')
    g.add_player(u.id)
    g.generate_roles()
    assert len(g.fascists) == 3
    assert len(g.players) == 10

    # test seating chart
    g.generate_seating()
    assert len(g.seating) == 10


def test_version():
    assert __version__ == '0.1.0'


test_game()
