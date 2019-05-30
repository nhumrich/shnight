import React, { Component } from 'react';
import { Redirect } from "react-router-dom";
import '../App.css';
import Header from './components/header'
import axios from 'axios';

class Home extends Component {
    state = {
        name_field_value: '',
        game_in_progress: false
    }
    newGame(new_name) {
        if (new_name === '') return null;
        axios.post('http://localhost:8080/api/new ', {user_name: new_name}).then(
            response => {
                let new_state = {
                    'game_id': response.data.game_id,
                    'user_id': response.data.user_id,
                    'user_name': new_name
                }
                localStorage.setItem('app_state', JSON.stringify(new_state))
                this.setState({'game_in_progress': true})
            }
        );
    }
    render() {
        if (this.state.game_in_progress) return <Redirect to="/lobby"/>
        return <div className="App">
            <Header/>
            <h1>Start Game</h1>
            <input className="Name" type="text" placeholder="Your Name/Handle" name="name" value={this.state.name_field_value}
               onChange={evt => this.setState({ name_field_value: evt.target.value})} />
               &nbsp;<button onClick={evt => this.newGame(this.state.name_field_value)}>Start</button>
        </div>
    }
}

export default Home;
