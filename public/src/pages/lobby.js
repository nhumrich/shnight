import React, { Component } from 'react';
import '../App.css';
import axios from 'axios';
import logo from '../sh.png';
import liberal_img from '../liberal.png'
import fascist_img from '../fascist.png'
import hitler_img from '../hitler.png'

let sse = null

class Lobby extends Component {
    _isMounted = false;

    state = {
        'game_id': '3',
        'status': null,
        'users_in_lobby': [],
        'user_role': 0,
        'sse': null
    }
    registerEE(userId) {
        this.setState({'sse': null})
        sse = new EventSource('http://localhost:8080/api/events?user='+userId)
        this.setState({'sse': sse})
        sse.onmessage = e => {
            if (this._isMounted === true) {
                let d = JSON.parse(e.data)
                let i;
                let role = 0;
                for (i = 0; i < d.players.length; i++) {
                    if (d.players[i].id === userId) {
                        role = d.players[i].role
                    }
                }
                this.setState({
                    'user_role': role,
                    'status': d.status,
                    'users_in_lobby': d.players,
                    'owner_id': d.owner_id})
            }

        }
    }
    startGame() {
        if (this.state.users_in_lobby.length < 5) {
            alert('Not enough players to begin.')
            return
        }
        axios.get('http://localhost:8080/api/start/'+this.state.game_id+'?user='+this.state.user_id).then(
            response => {
            }
        )
    }
    endGame() {
        axios.get('http://localhost:8080/api/end/'+this.state.game_id+'?user='+this.state.user_id).then(
            response => {
                console.log(response)
            }
        )
    }
    leaveGame() {
        axios.post('http://localhost:8080/api/leave', {user_id: this.state.user_id, game_id: this.state.game_id}).then(
            response => {
                localStorage.removeItem('app_state')
                this.props.history.push('/')
            }
        )
    }
    loadState() {
        let game_state = JSON.parse(localStorage.getItem('app_state'));
        if (game_state === null ){
            return this.props.history.push('/')
        }
        this.setState({
            'user_name': game_state.user_name,
            'user_id': game_state.user_id,
            'game_id': game_state.game_id
        })
        axios.get('http://localhost:8080/api/game_state/'+game_state.game_id+'?user_id='+game_state.user_id).then(
                    response => {
                        let d = response.data
                        let i;
                        let role = 0;
                        for (i = 0; i < d.players.length; i++) {
                            if (d.players[i].id === game_state.user_id) {
                                role = d.players[i].role
                            }
                        }
                        this.setState({
                        'user_role': role,
                        'users_in_lobby': response.data.players,
                        'status': response.data.status,
                        'owner_id': response.data.owner_id})
                    }
                )
        return game_state.user_id
    }

    componentDidMount() {
        this._isMounted = true;
        let uid = this.loadState()
        this.registerEE(uid)
    }
    componentWillUnmount() {
        this._isMounted = false
        sse = null
    }

    userList() {
        return <div> <h3>Users In Lobby:</h3> {
            this.state.users_in_lobby.map((user, idx) => (
                <div key={idx}>{user.name}{user.id === this.state.owner_id ? ' (owner)' : ''}</div>
            ))
        }</div>
    }

    showRole() {
        let roleImage = liberal_img;
        if (this.state.user_role === 1) {
            roleImage = fascist_img
        }
        else if (this.state.user_role === 2) {
            roleImage = hitler_img
        }
        return <div>
            <img src={roleImage}/>
        </div>
    }
    canViewRole() {
        return this.state.user_role === 1  || (this.state.user_role === 2 && this.state.users_in_lobby.length === 5)
    }
    render() {
        return <div className="App">
            <header className="App-main cursor" onClick={evt => this.leaveGame()}>
                <img src={logo} className="App-logo sm" alt="logo" />
            </header>
            <h3>Game Id: {this.state.game_id}</h3>
            {this.state.status === 'closed' ? this.showRole() : this.userList()}
            {this.canViewRole() === true ?
                this.state.users_in_lobby.map((user, idx) => {
                    if (user.role === 0 || user.id === this.state.user_id) return null
                    if (user.role === 1) {
                        return <div>Fellow Fascist: {user.name}</div>
                    }
                    return <div>
                        Hitler: {user.name}
                    </div>

                }) : '' }
            { this.state.user_id === this.state.owner_id ? this.state.users_in_lobby.length >= 5 ? this.state.status !== 'closed' ? (
               <div className="leave_button">
                   <button onClick={evt => this.startGame()}>Start Secret Hitler</button>
               </div>
            ) : (
                <div className="leave_button">
                    <button onClick={evt => this.endGame()}>End Game</button>
                </div>
            ): (<div className="leave_button">
                    <button disabled>Need More Players to start</button>
                </div>
                ) : ''}

            { this.state.status === 'closed' ? '' : (
            <div className="leave_button">
               <button onClick={evt => this.leaveGame()}>Leave</button>
            </div>
                )}
        </div>
    }
}

export default Lobby;
