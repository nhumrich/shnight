import React, { Component } from 'react';
import { Link } from "react-router-dom";
import logo from '../../sh.png';
import '../../App.css';

class Header extends Component {
    render() {
        return <header className="App-main">
            <Link to="/">
                <img src={logo} className="App-logo sm" alt="logo" />
            </Link>
        </header>
    }
}

export default Header;
