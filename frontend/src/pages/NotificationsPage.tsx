import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Notification } from '../types';
import { notificationAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (user) {
      fetchNotifications();
    }
  }, [isAuthenticated, user]);

  const fetchNotifications = async () => {
    try {
      const response = await notificationAPI.get(`/notifications/${user?.id}`);
      setNotifications(response.data);
    } catch (err) {
      setError('Failed to load notifications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await notificationAPI.patch(`/notifications/${notificationId}/read`);
      setNotifications((prev) =>
        prev.map((notif) => (notif.id === notificationId ? { ...notif, read: true } : notif))
      );
    } catch (err) {
      console.error('Failed to mark notification as read', err);
    }
  };

  if (loading) {
    return <div className="text-center mt-8">Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Notifications</h1>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      <div className="space-y-3">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`p-4 rounded-lg shadow ${
              notification.read ? 'bg-white' : 'bg-blue-50 border-l-4 border-blue-500'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="text-gray-800">{notification.message}</p>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(notification.created_at).toLocaleString()}
                </p>
              </div>
              {!notification.read && (
                <button
                  onClick={() => markAsRead(notification.id)}
                  className="ml-4 text-blue-500 hover:text-blue-700 text-sm"
                >
                  Mark as read
                </button>
              )}
            </div>
          </div>
        ))}

        {notifications.length === 0 && (
          <div className="text-center text-gray-500 py-8">No notifications yet</div>
        )}
      </div>
    </div>
  );
};

export default NotificationsPage;
