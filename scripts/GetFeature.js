

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

/* --------------------------------------------------------------
----- Start of Script
-----------------------------------------------------------------  */

client.connect()

console.log("running")

var song_id

client.query('SELECT songid FROM songdata', (err, res) => {
	//don't think anything is needed here
}).then(
	function(ids){
		var resList = [];
		console.log(ids.rows.length)
		for( i = 0; i < ids.rows.length; i++){
			console.log(ids.rows[i].songid);
			Promise.all(getFeatures(ids.rows[i].songid)).then(function(values){
				resList.push(values);
		});
		}
		console.log(resList);
		return "hej";
	}
).then(
	function(result){
		console.log(result)
		client.query('SELECT * FROM songdata', (err, res) => {
	})
 }
).then(
	function(){
		client.end()
		console.log("Script finished running")
	}
)

function getFeatures(song_id){
	 var res;
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
	 				console.log(body.tempo)
	 				console.log(body.mode)
	 				console.log(body.loudness)
					res = [song_id, body.tempo, body.mode, body.loudness]
					console.log(res);
					return res;
	     })
	   }
	 })

}

function updateFeatureInDB(songid, tempo, mode, loudness){
		const text = "UPDATE songdata SET tempo = ($2), mode = ($3), loudness = ($4) WHERE songid = ($1)"
		client.query(text, [songid, tempo, mode, loudness], (err, res) => {
		})
}
