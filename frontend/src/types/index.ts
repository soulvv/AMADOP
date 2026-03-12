export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_username?: string;
  created_at: string;
}

export interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  username?: string;
  content: string;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  message: string;
  read: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
