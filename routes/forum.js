// routes/forum.js
const express = require('express');
const router = express.Router();

let posts = []; // This will act as an in-memory store for forum posts

// Create a new post
router.post('/posts', (req, res) => {
  const { title, content } = req.body;

  // Validate input
  if (!title || !content) {
    return res.status(400).json({ message: 'Title and content are required' });
  }

  const newPost = { id: posts.length + 1, title, content, comments: [] };
  posts.push(newPost);

  return res.status(201).json(newPost);
});

// Get all posts
router.get('/posts', (req, res) => {
  return res.json(posts);
});

// Add a comment to a post
router.post('/posts/:id/comments', (req, res) => {
  const postId = parseInt(req.params.id);
  const { content } = req.body;

  // Validate input
  if (!content) {
    return res.status(400).json({ message: 'Comment content is required' });
  }

  const post = posts.find(p => p.id === postId);

  if (!post) {
    return res.status(404).json({ message: 'Post not found' });
  }

  const newComment = { id: post.comments.length + 1, content };
  post.comments.push(newComment);

  return res.status(201).json(newComment);
});

module.exports = router;
