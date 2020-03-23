import React, { useState, useEffect } from 'react';
import Game from './components/Game'
import Setup from './components/Setup'
import sh_img from './sh.png'
import './App.css';
import axios from 'axios';
import { Container, Row, Col } from 'react-bootstrap';


function gameExists(gameId) {
  return axios.post('/api/game_exists', {'game_id': gameId})
}

function App() {
  const [gameLive, setGameLive] = useState(false);
  const [username, setUsername] = useState();
  const [userId, setUserId] = useState();
  const [gameId, setGameId] = useState();

  useEffect(() => {
    let game_state = JSON.parse(localStorage.getItem('app_state'));
    if (game_state !== null) {
      setGameId(game_state.game_id)
      setUserId(game_state.user_id)
      setUsername(game_state.username)
      gameExists(game_state.game_id).then(response => {
        if (response.data.status === null) {
          localStorage.removeItem('app_state')
        } else {
          setGameLive(true)
        }
      })
    }
  }, [])
  return (
    <Container fluid>
      <Row style={{marginTop: '20px'}}>
        <Col className="text-center"><img alt='logo' style={{width: '120px'}} src={sh_img}/></Col>
      </Row>
      <Row style={{marginTop: '20px'}}>
        <Col className="text-center">{gameLive ?
          <Game gameId={gameId} username={username} userId={userId} /> :
          <Setup setGameLive={setGameLive} setGameId={setGameId} userId={userId} gameId={gameId} setUserId={setUserId} username={username} setUsername={setUsername} />}</Col>
      </Row>
    </Container>
  );
}

export default App;
