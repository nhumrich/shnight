import React, { Component } from 'react';
import '../App.css';
import axios from 'axios';
import { Redirect } from "react-router-dom";
import Header from './components/header'

class Join extends Component {
    state = {
        'game_field_value': '',
        'name_field_value': '',
        'game_in_progress': false

    }

    joinGame(user, game_id) {
        if (user === '' || game_id === '') return null;
        game_id = parseInt(game_id)
        this.setState({'join_error_message': ''})
        if (Number.isInteger(parseInt(game_id)) && game_id > 100000 && game_id <= 999999) {
            axios.post('http://localhost:8080/api/join ', {game_id: game_id, user_name: user}).then(
                response => {
                    if (response.data.exists === true) {
                        let new_state = {
                            'game_id': response.data.game_id,
                            'user_id': response.data.user_id,
                            'user_name': user
                        }
                        localStorage.setItem('app_state', JSON.stringify(new_state))
                        this.setState({'game_in_progress': true})
                    } else {
                        this.setState({'join_error_message': 'Unable to join game. Check your PIN and try again.'})
                    }
                }
            )
            return
        }
        this.setState({'join_error_message': 'Unable to join game. Check your PIN and try again.'})
    }
    render() {
        if (this.state.game_in_progress) return <Redirect to="/lobby"/>
        return <div className="App">
            <Header/>
           <h1>Join Game</h1>
           <input className="GameId" type="text" placeholder="Game ID/Pin" name="game_id" value={this.state.game_field_value}
                                   onChange={evt => this.setState({ game_field_value: evt.target.value})} /><br/>
           <input className="Name" type="text" placeholder="Name/Handle" name="name" value={this.state.name_field_value}
               onChange={evt => this.setState({ name_field_value: evt.target.value})} />
               <button onClick={evt => this.joinGame(this.state.name_field_value, this.state.game_field_value)}>Start</button>
               {this.state.join_error_message === '' ? '' : (<div>{this.state.join_error_message}</div>)}
        </div>
    }
}

export default Join;
