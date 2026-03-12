"""Setup database for AMADOP platform"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the amadop_db database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='amadop_db'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('amadop_db')
            ))
            print("✓ Database 'amadop_db' created successfully")
        else:
            print("✓ Database 'amadop_db' already exists")
        
        cursor.close()
        conn.close()
        
        # Now create tables
        print("\nCreating tables...")
        from backend.auth_service.database import Base, engine as auth_engine
        from backend.auth_service.models import User
        Base.metadata.create_all(bind=auth_engine)
        print("✓ Auth service tables created")
        
        from backend.post_service.database import Base as PostBase, engine as post_engine
        from backend.post_service.models import Post
        PostBase.metadata.create_all(bind=post_engine)
        print("✓ Post service tables created")
        
        from backend.comment_service.database import Base as CommentBase, engine as comment_engine
        from backend.comment_service.models import Comment
        CommentBase.metadata.create_all(bind=comment_engine)
        print("✓ Comment service tables created")
        
        from backend.notification_service.database import Base as NotifBase, engine as notif_engine
        from backend.notification_service.models import Notification
        NotifBase.metadata.create_all(bind=notif_engine)
        print("✓ Notification service tables created")
        
        print("\n✅ Database setup complete!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Setting up AMADOP database...\n")
    create_database()
