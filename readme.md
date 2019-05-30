# SHNight
Secret Hitler Night Phase


## Installation

### Prerequisites. 
Must have [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

You also need `git`

### Install & Run

```
$ git clone https://github.com/nhumrich/shnight.git
$ cd shnight
$ docker-compose up --build
# you might need to add `sudo` before `docker-compose`
```


## Notes
This was designed with minimalism in mind. All state data is stored in memory, so restarting the server, docker,
whatever, will cause problems for people currently in the middle of a game, or in the lobby. 


## Todo's and wants
- [ ] Clean up UI
- [ ] Add voting
- [ ] Add the rest of game logic
- [ ] Create persistant state via database, or other means
