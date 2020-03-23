import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Form, Container, Row, Col, Card, Table } from 'react-bootstrap';
import liberal_img from '../liberal.png'
import fascist_img from '../fascist.png'
import hitler_img from '../hitler.png'
import ja_img from '../ja.png'
import nein_img from '../nein.png'


function GameInfo(props) {
  return (
    <Card>
      <div style={{background: '#ccc'}}>GameId: {props.gameId}</div>
      <div style={{background: '#ccc', marginBottom: '10px'}}>Username: {props.username}</div>
      {props.gameStarted ? (
        <div>
        <strong>Play/Seat Order</strong>
        <UserBoard userId={props.userId} players={props.players} role={props.userRole}/>
        </div>
      ) : (
        <div>
          { props.players.length !== 0 ?
            props.players.map((player, idx) => {
              return <div key={idx} >{player.name}</div>
            })
          : ''}
        </div>
      )}
    </Card>
  )
}

function Actions(props) {
  return (
    <Card>
      <div style={{background: '#ccc'}}>Actions</div>
      {props.ownerId === props.userId && !props.gameStarted ? (
        <div style={{marginBottom: '10px', marginTop: '10px'}}>
          <Button variant='info' size="sm" onClick={props.startGame}>Start Game</Button>
        </div>
      ) : ''}
      {props.ownerId === props.userId && props.gameStarted ? (
        <div style={{marginBottom: '10px', marginTop: '10px'}}>
          <Button variant='info' size="sm" onClick={props.endGame}>End Game</Button>
        </div>
      ) : ''}
      {props.ownerId === props.userId && props.gameStarted ? (
        <div style={{marginBottom: '10px'}}>
          <div>Polls are <strong>{props.electionsOpen ? 'Open' : 'Closed'}</strong></div>
          <Button variant='info' size="sm" onClick={props.toggleElections}>{props.electionsOpen ? 'Close' : 'Open'} Polls</Button>
        </div>
      ) : ''}
    </Card>
  )
}

function showRole(role, show=true, width=119) {
  if (!show) {
    return <div style={{background: '#555', width: 119, height: 174, color: '#fff', paddingTop: '60px'}}><strong>Role</strong></div>
  }
  let roleImage = liberal_img;
  if (role === 1) {
      roleImage = fascist_img
  }
  else if (role === 2) {
      roleImage = hitler_img
  }
  return <div>
      <img style={{width: width}} src={roleImage}/>
  </div>
}

function UserBoard(props) {

  return <div>
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>Name</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
      {props.players.sort((a, b) => (a.seat > b.seat) ? 1 : -1).map((player, idx) => {
        return <tr key={idx}><td>{player.id === props.userId ? <strong>You:</strong> : '' } {player.name}</td><td>{showRole(player.role, true, 45)}</td></tr>
      })}
      </tbody>
    </Table>
  </div>
}

function VotingResults(props) {
  let roleImage = props.voteType === 'ja' ? ja_img : nein_img
  let plist = {}
  for (let i = 0; i < props.players.length; i++) {
    plist[props.players[i].id] = props.players[i].name
  }

  if (props.hasVoted) {
    return (
    <Table striped bordered hover>
      <tbody>
        {props.playersVotes.map((player, idx) => {
          return (
            <tr key={idx}>
              <td>
                {plist[player]}
              </td>
              <td>
                <img style={{width: '45px'}} src={roleImage}/>
              </td>
            </tr>
          )
        })}
      </tbody>
    </Table>    )
  }
}


function Game(props) {
  const [sse, setSse] = useState()
  const [gameStatus, setGameStatus] = useState('closed')
  const [userRole, setUserRole] = useState()
  const [players, setPlayers] = useState([])
  const [ownerId, setOwnerId] = useState()
  const [electionsOpen, setElectionsOpen] = useState()
  const [hasVoted, setHasVoted] = useState(false)
  const [voteState, setVoteState] = useState()
  const [allVotes, setAllVotes] = useState()

  useEffect(() => {
    setSse(new EventSource('/api/events?user='+props.userId)
    .onmessage = e => {
      if (e) {
        let d = JSON.parse(e.data)
        let i;
        let role = 0;
        for (i = 0; i < d.players.length; i++) {
          if (d.players[i].id === props.userId) {
            role = d.players[i].role
          }
        }

        for (i = 0; i < d.votes.ja.length; i++) {
          if (d.votes.ja[i] == props.userId) {
            setHasVoted(true)
            setVoteState('ja')
          }
        }

        for (i = 0; i< d.votes.nein.length; i++) {
          if (d.votes.nein[i] == props.userId) {
            setHasVoted(true)
            setVoteState('nein')
          }
        }

        setAllVotes(d.votes)
        if (!d.elections_open) {
          setHasVoted(false)
        }
        setGameStatus(d.status)
        setUserRole(role)
        setPlayers(d.players)
        setOwnerId(d.owner_id)
        setElectionsOpen(d.elections_open)
      }
    })
  }, [])

  const startGame = () => {
    if (players.length < 5) {
      alert('Not enough players to begin.')
      return
    }
    axios.get('/api/start/'+props.gameId+'?user='+props.userId).then(
      console.log('game started')
    )
  }
  const endGame = () => {
    axios.get('/api/end/'+props.gameId+'?user='+props.userId).then(
      console.log('game ended')
    )
  }
  const toggleElections = () => {
    axios.post('/api/toggle_elections/'+props.gameId, {}).then(
      response => {
        console.log(response)
      }
    )
  }

  const handleVote = cast => {
    setHasVoted(true)
    setVoteState(cast)

    axios.post('/api/cast_vote/'+props.gameId, {'user_id': props.userId, 'vote_for': cast}).then(
      response => {
        console.log(response)
      }
    )
  }

  return (
    <Container style={{marginTop: '20px'}}>
      <Row>
        <Col md={2}><Actions gameStarted={gameStatus!=='open'} endGame={endGame} electionsOpen={electionsOpen} startGame={startGame} toggleElections={toggleElections} ownerId={ownerId} gameId={props.gameId} userId={props.userId}/></Col>
        <Col md={7}>{gameStatus!=='open' ? (
        <div>
          {electionsOpen ? (
            <>
            {hasVoted ? (
              <div>
                <div>You have cast your vote: <strong>{voteState}</strong></div>
                <VotingResults voteType='ja' hasVoted={hasVoted} playersVotes={allVotes.ja} players={players}/>
                <VotingResults voteType='nein' hasVoted={hasVoted} playersVotes={allVotes.nein} players={players}/>
              </div>
            ) : (
              <>
              <img onClick={() => handleVote('ja')} style={{cursor: 'pointer'}} src={ja_img}/> <img onClick={() => handleVote('nein')} style={{cursor: 'pointer'}} src={nein_img}/>
              </>
            ) }
            </>
          ) : 'Game Started'}
        </div>
      ) : (
        <div>
          Game has not started. <br/><br/>Share this code with your friends:<br/>
          <strong>{props.gameId}</strong>
        </div>
      )}</Col>
        <Col><GameInfo userId={props.userId} gameStarted={gameStatus!=='open'} players={players} gameId={props.gameId} username={props.username}/></Col>
      </Row>
    </Container>
  )
}

export default Game;
