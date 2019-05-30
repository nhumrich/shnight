import React, { Component } from 'react';
import { Router, Route } from "react-router-dom";
import { createBrowserHistory } from "history";
import './App.css';
import axios from 'axios';
import Home from './pages/home'
import Join from './pages/joingame'
import New from './pages/newgame'
import Lobby from './pages/lobby'

const customHistory = createBrowserHistory();

class App extends Component {
    gameExists(gameId) {
        return axios.post('http://localhost:8080/api/game_exists', {'game_id': gameId})
    }

    checkSessionStarted() {
        var game_state = JSON.parse(localStorage.getItem('app_state'));
        if (game_state !== null) {
            var game_id = game_state.game_id
            this.gameExists(game_id).then(response => {
                if (response.data.status === null) {
                    localStorage.removeItem('app_state')
                } else {
                    customHistory.push('/lobby')
                }
            })
        }
    }

    componentWillMount() {
        this.checkSessionStarted()
    }

    render() {
        return <Router history={customHistory}>
            <Route path="/" exact component={Home}/>
            <Route path="/lobby" exact component={() => <Lobby history={customHistory}/> }/>
            <Route path="/join" exact component={Join}/>
            <Route path="/new" exact component={New}/>
        </Router>
    }
}

export default App;




