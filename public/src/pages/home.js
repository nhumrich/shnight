import React, { Component } from 'react';
import { Link } from "react-router-dom";
import logo from '../sh.png';
import '../App.css';

class Home extends Component {
    render() {
        return <div className="App">
            <header className="App-header">
                <img src={logo} className="App-logo" alt="logo" />
                <p>
                    <Link to="/new">New Game</Link> | <Link to="/join">Join Game</Link>
                </p>
            </header>
        </div>
    }
}

export default Home;
