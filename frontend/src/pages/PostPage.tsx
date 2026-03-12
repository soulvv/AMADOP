import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Post, Comment } from '../types';
import { postAPI, commentAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PostPage = () => {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentContent, setCommentContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (id) {
      fetchPost();
      fetchComments();
    }
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await postAPI.get(`/posts/${id}`);
      setPost(response.data);
    } catch (err) {
      setError('Failed to load post');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await commentAPI.get(`/comments/${id}`);
      setComments(response.data);
    } catch (err) {
      console.error('Failed to load comments', err);
    }
  };

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentContent.trim()) return;

    try {
      await commentAPI.post('/comments', {
        post_id: Number(id),
        content: commentContent,
      });

      setCommentContent('');
      fetchComments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to post comment');
    }
  };

  if (loading) {
    return <div className="text-center mt-8">Loading...</div>;
  }

  if (!post) {
    return <div className="text-center mt-8">Post not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      <article className="bg-white p-6 rounded-lg shadow mb-6">
        <h1 className="text-3xl font-bold mb-4">{post.title}</h1>
        <div className="text-sm text-gray-500 mb-4">
          By User {post.author_id} • {new Date(post.created_at).toLocaleDateString()}
        </div>
        <div className="prose max-w-none">{post.content}</div>
      </article>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Comments ({comments.length})</h2>

        {isAuthenticated && (
          <form onSubmit={handleCommentSubmit} className="mb-6">
            <textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Write a comment..."
              rows={3}
              maxLength={1000}
              required
            />
            <button
              type="submit"
              className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Post Comment
            </button>
          </form>
        )}

        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="text-sm text-gray-500 mb-1">
                User {comment.user_id} • {new Date(comment.created_at).toLocaleDateString()}
              </div>
              <p className="text-gray-800">{comment.content}</p>
            </div>
          ))}

          {comments.length === 0 && (
            <p className="text-gray-500 text-center py-4">No comments yet. Be the first!</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PostPage;
