const request = require('request');

const express = require('express');
var session = require('cookie-session');
var bodyParser = require('body-parser');

const engines = require('consolidate');
var hbs = require('handlebars');

const dotgit = require('dotgitignore')();
const cors = require('cors')

require('dotenv').config();

var mysql = require('mysql');

const url = require('url');
const fs = require('fs'); 
const app = express();

app.engine('hbs', engines.handlebars);
app.set('views', './views');
app.set('view engine', 'hbs');


const connection  = mysql.createPool({
	host     : 'eu-cdbr-west-01.cleardb.com',
	user     :  process.env.DB_USER,
	password :  process.env.DB_PWD,
	database : 'heroku_1b392502415228b'
});


app.use(cors({origin: true}));
app.use(session({
    secret: 'secret',
    resave: true,
    saveUninitialized: true
}));

app.use(bodyParser.urlencoded({extended : true}));
app.use(bodyParser.json());


app.get('/', function (request, response) {
    response.render('login');
});


app.post('/auth', function (request, response){

    var username = request.body.username;
    var password = request.body.password;


	if (username && password) {
		connection.query('SELECT * FROM user WHERE username = ? AND password = ?', [username, password], function(error, results, fields) {
			if (results.length > 0) {

            request.session.loggedin = true;
            request.session.username = username;

            response.render('query');
        } else {
            response.render('error', { error: 'Incorrect Username and/or Password!' });
        }
    });

    } else {
        response.render('error', { error: 'Please enter Username and Password!' });
    };
});

app.get('/query', function (request, response) {  
    if (request.session.loggedin) {
        response.render('query');
    } else {
        response.render('error', { error: 'Please login to view this page!' });
    }
});


app.post('/results', function (request, response) {
    if (request.session.loggedin) {

        var keyword = request.body.keyword;
        var nResults = request.body.nResults;

        const { spawn } = require('child_process');
        obj = { keyword : keyword, nResults : nResults }
        const childPython = spawn('python', ['main.py', JSON.stringify(obj)]);

        childPython.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`)
        });

        childPython.stdout.on('data', (data) => {
            var data = JSON.parse(data.toString().replace(/'/g, '"'));
            console.log('stdout', data)


        /*var data = {"keyword": "wifi", "nResults": "1", "overall": {"scraper": {"techradar": [{"title": ["google wifi review"], "link": "https://www.techradar.com/reviews/google-wifi", "img": "https://cdn.mos.cms.futurecdn.net/pbiyvrJ6M84eTMQuLNCvWi.jpg", "time": "12-30-2021", "weighting": 0, "polarity": 0.15804246717469853, "subjectivity": 0.4813681084755463, "content": {"wifi": 44, "google": 34, "mesh": 14, "meters": 9, "router": 8, "points": 8, "network": 8, "price": 7}, "source": "techradar"}], "sorted_articles": [{"title": ["google wifi review"], "link": "https://www.techradar.com/reviews/google-wifi", "img": "https://cdn.mos.cms.futurecdn.net/pbiyvrJ6M84eTMQuLNCvWi.jpg", "time": "12-30-2021", "weighting": 0, "polarity": 0.15804246717469853, "subjectivity": 0.4813681084755463, "content": {"wifi": 44, "google": 34, "mesh": 14, "meters": 9, "router": 8, "points": 8, "network": 8, "price": 7}, "source": "techradar", "delta_published_at": 12, "user_vote_prediction": 0}]}, "social_media": {"reddit": [{"source": "Reddit", "title": "Free wifi ", "url": "https://v.redd.it/urmi4sa1gcz71", "text": " if you think this post is funny upvote this comment   if you think this post is unfunny downvote this comment         downloadvideo link  savevideo link  kevin would also like to remind you that if youre really desperate youtubedl can be used to download videos from reddit    whilst youre here tyqy why not join our public discord server reject wman paket phoenix is eternal  and 100 mbps quick  shes 12 zamn paket phoenix good deal buy you just got free wified sauce pls already failed nnn sauce the song is unironically a bop what is it called hmmm yes 1gbps of internet connection for upscaled 4k bbc im sad and horny now  i wait for the sauce i thought the indihome memes were dead pak agus selamanya hahaha guys funny bait meme  you though you would see her ass but it transitioned to funny thing  taiwan sauce   fat oily redditor fuck you free wifi and your face is also a cute girls buttocks how could you say no i missed this meme that indonesian music is lit que carajo hace un video de escuela argentina aca get wifi anywhere you go this song is so good im not even joking truly a classic she kinda looks like my sister wtf sauce please sauce where sauce deleted sauce i dont wanna have to see the wmen i love that ad yo hmu when theres discounts twitter link only 935000  lmao spanish shitpost ohshitwifi internet speed is so fast thanks bro i was trying to remember the name of the song and i was stuck xd anywhere you go i agree i love this too much get wifi anywhere you go plays techno music from 2010 what is free wifi in hindi lol yoo wifi nyoooo awww they grow old so fast comrades go on without me huh sauce  can i buy the 100mbs package h stupid reddit thumbnail gave it away that my friends is a child prank em john nice cock  idk whats going on with the rest of the joke but those girls are speaking the argentine dialect i forgor the music makes up for it dammit got mas agusrolled again nice butsauce hold up where can i find the video no one going to point out he is doing the shocker with his hand lol can this video be any more creepy ma boooyyy with the free wifi", "created": 1636800962.0, "polarity": 0.19893830128205128, "subjectivity": 0.6829059829059828, "entities": [["UPVOTE", "ORG"], ["Kevin", "PERSON"], ["Reddit", "GPE"], ["Tyqy", "GPE"], ["100", "CARDINAL"], ["SHES", "ORG"], ["12", "CARDINAL"], ["NNN", "ORG"], ["1Gbps", "CARDINAL"], ["4k", "CARDINAL"], ["BBC", "ORG"], ["Pak Agus", "PERSON"], ["HAHAHA", "NORP"], ["taiwan", "GPE"], ["Indonesian", "NORP"], ["un", "ORG"], ["Argentina", "GPE"], ["WIFI", "PERSON"], ["Only $935,000", "MONEY"], ["spanish", "NORP"], ["Wifi", "PERSON"], ["2010", "DATE"], ["HINDI", "GPE"], ["Nyoooo", "ORG"], ["Awww", "ORG"], ["100mbs", "DATE"], ["Idk", "PERSON"], ["Mas Agusrolled", "PERSON"], ["Lol", "PERSON"], ["WiFi", "PERSON"]], "Dominant_Topic": 1.0, "Topic_Perc_Contrib": 0.3694, "Keywords": "free, music, song, fast, comment, akan, nice, post, transitioned, guys", "Topic_Weights": {"0": 0.29078014184397166, "1": 0.369385342789598, "2": 0.33983451536643017}, "Intent": "Opinion"}], "twitter": [{"source": "Twitter", "text": "hoonzkart wifi o bluetooth k b beh hahshahhaha ", "retweet_count": 0, "favorite_count": 0, "url": [], "location": 0, "profile_image_url": "http://pbs.twimg.com/profile_images/1473663596957937669/mKij1mC5_normal.jpg", "username": "jaykekikartz", "created": "Tue Jan 11 14:19:41 +0000 2022", "name": "mira", "polarity": 0.0, "subjectivity": 0.0, "entities": [["HAHSHAHHAHA", "ORG"]], "Dominant_Topic": 1.0, "Topic_Perc_Contrib": 0.3694, "Keywords": "free, music, song, fast, comment, akan, nice, post, transitioned, guys", "Topic_Weights": {"0": 0.29078014184397166, "1": 0.369385342789598, "2": 0.33983451536643017}, "Intent": "Opinion"}], "instagram": [{"source": "Instagram", "alt": "Photo by Zulaikha Ika Nst on January 11, 2022. May be an image of jewelry and text that says PENDANT KESEHATAN MCI Tampak Depan Tampak belakang.", "image_url": "https://instagram.fpnh18-3.fna.fbcdn.net/v/t51.2885-15/e35/271548750_1120756448761895_5229768998560375328_n.jpg?_nc_ht=instagram.fpnh18-3.fna.fbcdn.net&_nc_cat=111&_nc_ohc=bA3HgaSNnwgAX8WHSwm&edm=ABZsPhsBAAAA&ccb=7-4&oh=00_AT_9YOyJGbb9LXi0MNRZU8hl6y1VcFZTr3ASjcSn6dJyvg&oe=61E3A1C4&_nc_sid=4efc9f", "text": " kalung pendant utk kesehatan keluarga anda  katanya kalo kena radiasi bisa bikin cepat tua bersyukur aq punya bioglass n kalung pendant mci yg berperan sbg anti radiasi   kalung emas bertaburan berlian seharga puluhan juta sekalipun tidak bisa membantu apaapa ketika anda sakit betul tidak   sementara kalung pendant cantik ini bisa membuat badan lebih fit dan berenergi tubuh lebih sehat segar dan bersemangat   dibalik kilaunya kalung ini ternyata bisa melancarkan peredaran darah membantu menangkal polusiradiasi dari lingkungan   bentuknya yang mungil dan elegan tidak akan merusak fashion style anda malah akan membuat penampilan semakin berkilau dan mewah   niat baik jangan ditundatunda ya kesehatan adalah investasi yang paling berharga untuk anda sendiri untuk keluarga untuk orang tua tercinta  harga ecer  life secret woman 1650000  life secret man 1650000  biopendant 1400000  pendant aura heart 1400000  pendant marvel 1800000  pendant spider 1800000  harga paketan bs lebih murah free voucher 400000 free membership selamanya  kalungkesehatan antiradiasi wifi kalungberenergi aksesoriskalung kalungcouple pendantaura lifesecret lifesecretwoman lifesecretman biopendant  order chat me wa  081260888105", "created": "2022-01-11T14:19:40.000Z", "location": [44.933143, 7.540121], "polarity": 0.08, "subjectivity": 0.68, "entities": [["ANDA", "PERSON"], ["Katanya", "GPE"], ["tua", "PERSON"], ["MCI", "ORG"], ["Kalung", "GPE"], ["berlian seharga puluhan juta sekalipun", "PERSON"], ["apa-apa", "NORP"], ["Anda", "PERSON"], ["Sementara kalung", "PERSON"], ["Pendant", "ORG"], ["lebih", "GPE"], ["dan ber-energi", "PERSON"], ["lebih", "GPE"], ["dan bersemangat", "PERSON"], ["Dibalik kilaunya", "PERSON"], ["kalung ini ternyata bisa", "ORG"], ["melancarkan", "FAC"], ["Bentuknya yang", "PERSON"], ["dan elegan tidak", "PERSON"], ["akan", "ORG"], ["Anda", "PERSON"], ["malah", "ORG"], ["akan", "ORG"], ["dan mewah", "PERSON"], ["Niat", "PERSON"], ["kesehatan adalah investasi yang", "PERSON"], ["Untuk Anda", "PERSON"], ["untuk keluarga", "PERSON"], ["untuk orang tua", "PERSON"], ["1.650.000", "CARDINAL"], ["Life Secret Man 1.650.000", "WORK_OF_ART"], ["1.400.000", "CARDINAL"], ["1.400.000", "CARDINAL"], ["1.800.000", "CARDINAL"], ["lebih", "GPE"], ["400.000", "CARDINAL"], ["#kalungkesehatan #", "MONEY"], ["#kalungberenergi #", "MONEY"], ["#kalungcouple #", "MONEY"], ["#lifesecretwoman #", "MONEY"], ["#", "CARDINAL"]], "Dominant_Topic": 1.0, "Topic_Perc_Contrib": 0.3694, "Keywords": "free, music, song, fast, comment, akan, nice, post, transitioned, guys", "Topic_Weights": {"0": 0.29078014184397166, "1": 0.369385342789598, "2": 0.33983451536643017}, "Intent": "Opinion", "image_details": [{"Label": "Event", "Score": 0.6859139800071716, "Topicality": 0.6859139800071716}]}]}}}*/
        if (data["overall"].length === 0) { 
            
            response.send("Array is empty!") 
        
        } else {            
            response.render('output', { overall: data["overall"] });

        }
        });

    } else {
        response.render('error', { error: 'Please enter Username and Password!' });
    }
});

app.post('/dbupdate', function (request, response){

    if (request.body['upvote']){
        var articles = request.body['upvote']
        
        if (articles.constructor !== Array) {
            var articles = [articles]
        }

        var arrayLength = articles.length;
        for (var i = 0; i < arrayLength; i++) {
                
            var link = articles[i]

            //connection.query("UPDATE articles SET user_vote=1 WHERE articles.link=?", [link], function(error, results, fields) {
                        
            var sql = "UPDATE articles SET user_vote = '1' WHERE articles.link=?";
            connection.query(sql, [link], function (err, result) {
                if (err) throw err;
                console.log(result.affectedRows + " record(s) updated");
            });

        };
    }

    response.send("Should be done")
            
});

const port = process.env.PORT || 5000
app.listen(port)

console.log(`Server is listening on port ${port}`);
