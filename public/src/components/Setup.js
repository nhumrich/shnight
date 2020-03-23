import React, { useState } from 'react';
import { Button, Form, Container, Row, Col } from 'react-bootstrap';
import axios from 'axios';

function Setup(props) {
  const [buttonsEnabled, setButtonsEnabled] = useState(false);
  const [willJoin, setWillJoin] = useState(false);
  const [joinGameId, setJoinGameId] = useState();
  const [joinError, setJoinError] = useState('')

  const handleUsernameChange = event => {
    if (!buttonsEnabled) {
      setButtonsEnabled(true)
    }
    if (event.currentTarget.value === '') {
      setButtonsEnabled(false)
    }
    props.setUsername(event.currentTarget.value)
  }

  const handleChangeGameId = event => {
    props.setGameId(event.currentTarget.value)
  }

  const joinGame = () => {
    let game_id = parseInt(props.gameId)
    if (Number.isInteger(parseInt(game_id)) && game_id > 100000 && game_id <= 999999) {
      axios.post('/api/join ', {game_id: game_id, user_name: props.username})
      .then(response => {
        if (response.data.exists === true) {
          let new_state = {
            'game_id': response.data.game_id,
            'user_id': response.data.user_id,
            'username': props.username,
          }
          props.setGameId(response.data.game_id)
          props.setUserId(response.data.user_id)
          props.setGameLive(true)
          localStorage.setItem('app_state', JSON.stringify(new_state))
        } else {
          setJoinError('Unable to join game. Check your PIN and try again.')
        }
      })
    }
  }

  const newGame = () => {
    if (props.username !== '') {
      axios.post('/api/new ', {user_name: props.username}).then(
        response => {
          let new_state = {
            'game_id': response.data.game_id,
            'user_id': response.data.user_id,
            'username': props.username,
          }
          props.setGameId(response.data.game_id)
          props.setUserId(response.data.user_id)
          props.setGameLive(true)
          localStorage.setItem('app_state', JSON.stringify(new_state))
        }
      );
    } else {

    }
  }
  return (
    <Container style={{width: '300px'}}>
      <Form>
        <Form.Group>
          <Row>
            <Col>
              <Form.Control type="input" placeholder="name" onChange={handleUsernameChange} />
            </Col>
          </Row>
          <Row style={{marginTop: '20px'}}>
            <Col>
              <Button variant='primary' onClick={() => newGame()} disabled={buttonsEnabled ? '' : 'disabled'}>New Game</Button>
            </Col>
            <Col>
              <Button disabled={buttonsEnabled ? '' : 'disabled'} onClick={() => setWillJoin(true)}>Join Game</Button>
            </Col>
          </Row>
          {willJoin ? (
            <>
              <Row style={{marginTop: '20px'}}>
                <Col>
                  <Form.Control type="input" placeholder="Game Code" onChange={handleChangeGameId} />
                </Col>
              </Row>
              <Row style={{marginTop: '20px'}}>
                <Col>
                  <Button onClick={joinGame}>Go!</Button>
                </Col>
              </Row>
            </>
          ) : ''}
        </Form.Group>
      </Form>
    </Container>
  )
}

export default Setup;
