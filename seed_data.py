import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database URL (pointing to local Postgres which we'll then migrate or just use K8s)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/amadop_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    session = SessionLocal()
    
    try:
        # Check if users already exist
        user_count = session.execute(text("SELECT count(*) FROM users")).scalar()
        if user_count > 1: # amadop_tester exists
            print(f"Database already has {user_count} users. Skipping seeding.")
            return

        print("Seeding database with realistic sample data...")

        # 1. Create Users
        users = [
            ("tech_enthusiast", "tech@example.com", "$2b$12$bra/mqOmNeIjIsSoFZpMPuik.4MyctGvHWjibqsbwdoWDs8bQHLyi"), # password123
            ("devops_guru", "guru@amadop.io", "$2b$12$bra/mqOmNeIjIsSoFZpMPuik.4MyctGvHWjibqsbwdoWDs8bQHLyi"),
            ("ai_researcher", "ai@lab.edu", "$2b$12$bra/mqOmNeIjIsSoFZpMPuik.4MyctGvHWjibqsbwdoWDs8bQHLyi"),
            ("cloud_architect", "cloud@azure.com", "$2b$12$bra/mqOmNeIjIsSoFZpMPuik.4MyctGvHWjibqsbwdoWDs8bQHLyi"),
            ("frontend_ninja", "ninja@react.dev", "$2b$12$bra/mqOmNeIjIsSoFZpMPuik.4MyctGvHWjibqsbwdoWDs8bQHLyi")
        ]
        
        for username, email, pwd in users:
            last_login = datetime.now() - timedelta(hours=random.randint(0, 24))
            session.execute(text(
                "INSERT INTO users (username, email, password_hash, created_at, last_login) VALUES (:u, :e, :p, :c, :l)"
            ), {"u": username, "e": email, "p": pwd, "c": datetime.now() - timedelta(days=random.randint(1, 30)), "l": last_login})

        session.commit()
        
        # Get user IDs
        user_ids = [r[0] for r in session.execute(text("SELECT id FROM users")).fetchall()]

        # 2. Create Posts
        posts = [
            ("The Future of Autonomous DevOps", "Autonomous DevOps is not just a dream. With tools like AMADOP, we are moving towards a world where infrastructure heals itself.", "Self-healing infrastructure is the cornerstone of modern DevOps."),
            ("Microservices Architecture in 2026", "Scaling microservices requires more than just Kubernetes. You need proper observability and AI-driven insights.", "Observability is key to scaling microservices."),
            ("Why I switched from Docker Compose to Kubernetes", "Docker Compose is great for local development, but Kubernetes offers the orchestration needed for production-grade stability.", "Transitioning to K8s for better orchestration."),
            ("AI Agents: The New Developers?", "AI agents are now performing complex coding tasks, but human intuition remains irreplaceable in architecture design.", "The role of AI agents in modern software development."),
            ("Mastering Tailwind CSS", "Utility-first CSS is changing how we build frontends. It's fast, consistent, and beautiful.", "Building beautiful UIs with Tailwind CSS.")
        ]

        for title, content, summary in posts:
            author_id = random.choice(user_ids)
            session.execute(text(
                "INSERT INTO posts (title, content, author_id, summary, created_at) VALUES (:t, :c, :a, :s, :ca)"
            ), {"t": title, "c": content, "a": author_id, "s": summary, "ca": datetime.now() - timedelta(days=random.randint(0, 5))})

        session.commit()

        # 3. Create Comments
        post_ids = [r[0] for r in session.execute(text("SELECT id FROM posts")).fetchall()]
        comments = [
            "Great article! Really helped me understand the transition to K8s.",
            "I disagree with the point on AI agents, they still have a long way to go.",
            "Tailwind is life! Never going back to vanilla CSS.",
            "Can you provide a part 2 on observability tools?",
            "AMADOP looks very promising. Keep up the good work!"
        ]

        for _ in range(15):
            post_id = random.choice(post_ids)
            author_id = random.choice(user_ids)
            content = random.choice(comments)
            session.execute(text(
                "INSERT INTO comments (post_id, author_id, content, created_at) VALUES (:p, :a, :c, :ca)"
            ), {"p": post_id, "a": author_id, "c": content, "ca": datetime.now() - timedelta(hours=random.randint(0, 48))})

        session.commit()
        print("✓ Successfully seeded users, posts, and comments.")

    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
