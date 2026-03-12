import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Post } from '../types';
import { postAPI } from '../services/api';

const HomePage = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await postAPI.get('/posts');
      setPosts(response.data);
    } catch (err) {
      setError('Failed to load posts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center mt-8">Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Blog Posts</h1>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      <div className="space-y-4">
        {posts.map((post) => (
          <Link
            key={post.id}
            to={`/posts/${post.id}`}
            className="block bg-white p-6 rounded-lg shadow hover:shadow-lg transition"
          >
            <h2 className="text-xl font-semibold mb-2">{post.title}</h2>
            <p className="text-gray-600 mb-2">
              {post.content.substring(0, 200)}
              {post.content.length > 200 ? '...' : ''}
            </p>
            <div className="text-sm text-gray-500">
              By User {post.author_id} • {new Date(post.created_at).toLocaleDateString()}
            </div>
          </Link>
        ))}

        {posts.length === 0 && (
          <div className="text-center text-gray-500 py-8">No posts yet. Be the first to post!</div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
