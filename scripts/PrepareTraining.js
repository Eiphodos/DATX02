

// HTTP request
var request = require('request') // "Request" library


// Spotify id and secret
var client_id = 'b3c7bb6a24de4750a15880440f94decf' // Your client id
var client_secret = 'c66c8a77642c44d89b78c6a9d15efa56' // Your secret

// Connecting to postgresSQL
const pg = require('pg')


const client = new pg.Client({
		user: 'postgres',
		host: 'localhost',
		database: 'postgres',
		password: 'databasen',
		port: 5432,
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

var ids = []
request.post(authOptions, function(error, response, body) {
  if (!error && response.statusCode === 200) {

    // use the access token to access the Spotify Web API
    var token = body.access_token;
    var options = {
      url: 'https://api.spotify.com/v1/users/sordi11/playlists/5Lyb7YeIvfTTEFYdludB2e/tracks',
      headers: {
        'Authorization': 'Bearer ' + token
      },
      json: true
    }
		const queryText ="INSERT INTO songdata VALUES ($1)"
		client.connect()
    request.get(options, function(error, response, body) {
			console.log("body")
			console.log(body.next)
			next = body.next
			console.log(next)
			for (i = 0; i < 5; i++){
					client.query(queryText,[body.items[i].track.id], (err, res) => {
					})
			}
			client.end()
		})
	}
})
