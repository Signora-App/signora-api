const express = require('express');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// Import forum routes
const forumRoutes = require('./routes/forum');

app.use(bodyParser.json());
app.use(morgan('dev'));
app.use(cors());

// Main route
app.get('/', (req, res) => {
  res.send('Welcome to Signora API');
});

// Forum routes
app.use('/api/forum', forumRoutes);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
