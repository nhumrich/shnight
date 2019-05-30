# SHNight
Secret Hitler Night Phase


## Installation

### Prerequisites. 
- [Docker](https://docs.docker.com/install/) installed and running. 
- [docker-compose](https://docs.docker.com/compose/install/) installed.
- `git`

### Install & Run

```
$ git clone https://github.com/nhumrich/shnight.git
$ cd shnight
$ docker-compose up --build
# you might need to add `sudo` before `docker-compose`
```

Then just navigate to [localhost](http://localhost). The server is running on port 80, so if you have something else running on 80, you will need to stop it, or update the `docker-compose.yml`.

## Notes
This was designed with minimalism in mind. All state data is stored in memory, so restarting the server, docker,
whatever, will cause problems for people currently in the middle of a game, or in the lobby. 


## Todo's and wants
- [ ] Clean up UI
- [ ] Add voting
- [ ] Add the rest of game logic
- [ ] Create persistant state via database, or other means
