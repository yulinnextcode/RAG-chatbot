var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var personas = require('./personas')
const cors = require('cors')

var app = express();

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const defaultDelay = 500;

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(cors());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

let personaId = "100";

app.use('/sendMessage', async (req, res)=>{
  let json = {...personas['100'],...personas[personaId]}

  console.log("request: ", req.body);
  const response = json['sendMessage']; 
  console.log("response: ", response);

  await delay(response.responseTime || defaultDelay)
  
  res.status(response.statusCode)
  res.send(JSON.stringify(response.body));
}); 




app.use('/feedback', async (req, res)=>{
  await delay(defaultDelay)
  let json = {...personas['100'],...personas[personaId]}

  console.log("request: ", req.body);
  const response = json['feedback']; 
  console.log("response: ", response);
  
  res.status(response.statusCode)
  res.send(JSON.stringify(response.body));
}); 

app.use('/timeout', async (req, res)=>{
  await delay(defaultDelay)
  let json = {...personas['100'],...personas[personaId]}

  console.log("request: ", req.body);
  const response = json['timeout']; 
  console.log("response: ", response);
  
  res.status(response.statusCode)
  res.send(JSON.stringify(response.body));
}); 

app.use('/extendSession', async (req, res)=>{
  await delay(defaultDelay)
  let json = {...personas['100'],...personas[personaId]}

  console.log("request: ", req.body);
  const response = json['extendSession']; 
  console.log("response: ", response);
  
  res.status(response.statusCode)
  res.send(JSON.stringify(response.body));
}); 


app.use('/', (req, res)=>{
  if(req.query.id) {
    res.cookie('persona', req.query.id, { maxAge: 900000, httpOnly: true });
    personaId = req.query.id;
    console.log(`Persona ${req.query.id} is selected.`);
    console.log(JSON.stringify(personas[req.query.id]))
  }
  
  const list = Object.keys(personas).map(key=> `<li><a href="/?id=${key}">${personas[key].description}</a></li>`)

  res.send(`<a target="_blank" href="/Georgia Department of Human Services.html">Test Webpage: the inactivity timeout is 3 mins on the testing server. You will get notice 1.5 mins before the timeout.</a><ol>${list.join('')}</ol>`);

}); 

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
