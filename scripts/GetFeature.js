

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

const client2 = new pg.Client({
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

/* --------------------------------------------------------------
----- Start of Script
-----------------------------------------------------------------  */

client.connect()
client2.connect()

console.log("running")

var song_id

client.query('SELECT songid FROM songdata', (err, res) => {
  song_id = res.rows
	console.log(song_id.length)
	for( i = 0; i < song_id.length; i++){
		getFeatures(song_id[i]);
	}
	client.end()
	client2.end()
})

function getFeatures(song_id){
	 console.log(song_id)
	 request.post(authOptions, function(error, response, body) {
	   if (!error && response.statusCode === 200) {

	     // use the access token to access the Spotify Web API
	     var token = body.access_token;
	     var options = {
	       url: 'https://api.spotify.com/v1/audio-features/' + song_id.songid,
	       headers: {
	         'Authorization': 'Bearer ' + token
	       },
	       json: true
	     }
	     request.get(options, function(error, response, body) {
	 				console.log(body.tempo)
	 				console.log(body.mode)
	 				console.log(body.loudness)
					updateFeatureInDB(song_id.songid, body.tempo, body.mode, body.loudness)
	     })
	   }
	 })
}

function updateFeatureInDB(songid, tempo, mode, loudness){
		const text = "UPDATE songdata SET tempo = ($2), mode = ($3), loudness = ($4) WHERE songid = ($1)"
		client2.query(text, [songid, tempo, mode, loudness], (err, res) =>
		})

}
