

// HTTP request
var request = require('request') // "Request" library


// Spotify id and secret
var client_id = 'b3c7bb6a24de4750a15880440f94decf' // Your client id
var client_secret = 'c66c8a77642c44d89b78c6a9d15efa56' // Your secret

// Connecting to postgresSQL
const pg = require('pg')


const client = new pg.Client({
		user: 'nodejs',
		host: 'localhost',
		database: 'postgres',
		password: 'NodeSQLServer',
		port: 5432,
})
client.connect()

var song_id

client.query('SELECT songid FROM userdata_userdata', (err, res) => {
  song_id = res.rows[0].songid
  console.log(res.rows[0].songid);
  client.end()
})

// your application requests authorization
var authOptions = {
  url: 'https://accounts.spotify.com/api/token',
  headers: {
    'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
  },
  form: {
    grant_type: 'client_credentials'
  },
  json: true
}

var tempo

request.post(authOptions, function(error, response, body) {
  if (!error && response.statusCode === 200) {

    // use the access token to access the Spotify Web API
    var token = body.access_token;
    var options = {
      url: 'https://api.spotify.com/v1/audio-features/' + song_id,
      headers: {
        'Authorization': 'Bearer ' + token
      },
      json: true
    }
    request.get(options, function(error, response, body) {
		tempo = body.tempo
		console.log(body.tempo)
		console.log(body.energy)
		console.log(body.valence)
		console.log(body.loudness)
    })
  }
})
/*
const text = "UPDATE tensordata SET tempo = ($1) WHERE songid = ($2)"

const client2 = new pg.Client({
		user: 'nodejs',
		host: 'localhost',
		database: 'postgres',
		password: 'NodeSQLServer',
		port: 5432,
})


client2.connect()

client2.query(text, [tempo, song_id], (err, res) => {
	if (err) {
		console.log(err.stack)
	} else {
		console.log(res)
	}
  client2.end()
})
*/