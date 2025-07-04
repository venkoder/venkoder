#!/usr/bin/env python3
"""
Advanced GitHub Statistics Generator
File: scripts/generate_stats.py
"""

import os
import json
import sys
from github import Github
from datetime import datetime
from collections import Counter

def generate_advanced_stats():
    """Generate comprehensive GitHub statistics"""
    username = os.getenv('USERNAME')
    token = os.getenv('GITHUB_TOKEN')

    if not username or not token:
        print("❌ Missing USERNAME or GITHUB_TOKEN environment variables")
        return False

    print(f"📊 Generating statistics for {username}...")

    try:
        g = Github(token)
        user = g.get_user(username)

        # Initialize counters
        languages = Counter()
        topics = Counter()

        # Statistics containers
        total_stars = 0
        total_forks = 0
        total_size = 0
        recent_activity = 0
        public_repos = 0
        repo_sizes = []
        creation_dates = []
        update_dates = []

        print("🔍 Analyzing repositories...")

        # Analyze all public repositories
        for repo in user.get_repos():
            if not repo.fork and not repo.private:
                public_repos += 1

                # Language statistics
                if repo.language:
                    languages[repo.language] += repo.size

                # Aggregate statistics
                total_stars += repo.stargazers_count
                total_forks += repo.forks_count
                total_size += repo.size

                # Repository metadata
                repo_sizes.append(repo.size)
                creation_dates.append(repo.created_at)
                update_dates.append(repo.updated_at)

                # Topics analysis
                try:
                    for topic in repo.get_topics():
                        topics[topic] += 1
                except:
                    pass  # Skip if topics not available

                # Recent activity (last 30 days)
                if (datetime.now() - repo.updated_at.replace(tzinfo=None)).days <= 30:
                    recent_activity += 1

                print(f"  ✅ Analyzed {repo.name}")

        # Calculate advanced metrics
        avg_repo_size = sum(repo_sizes) / len(repo_sizes) if repo_sizes else 0

        # Recent updates analysis
        recent_updates = len([d for d in update_dates
                             if (datetime.now() - d.replace(tzinfo=None)).days <= 90])

        # Account age analysis
        if creation_dates:
            oldest_repo = min(creation_dates)
            account_age_days = (datetime.now() - oldest_repo.replace(tzinfo=None)).days
        else:
            account_age_days = 0

        # Create comprehensive stats object
        stats = {
            'profile': {
                'username': username,
                'total_repos': public_repos,
                'total_stars': total_stars,
                'total_forks': total_forks,
                'followers': user.followers,
                'following': user.following,
                'account_age_days': account_age_days
            },
            'repositories': {
                'total_size_mb': round(total_size / 1024, 2),
                'average_size_kb': round(avg_repo_size, 2),
                'recent_activity_30d': recent_activity,
                'recent_updates_90d': recent_updates,
                'largest_repo_size': max(repo_sizes) if repo_sizes else 0
            },
            'languages': {
                'top_languages': dict(languages.most_common(10)),
                'language_count': len(languages),
                'primary_language': languages.most_common(1)[0][0] if languages else 'None'
            },
            'topics': {
                'top_topics': dict(topics.most_common(10)),
                'topic_count': len(topics)
            },
            'activity': {
                'stars_per_repo': round(total_stars / public_repos, 2) if public_repos > 0 else 0,
                'forks_per_repo': round(total_forks / public_repos, 2) if public_repos > 0 else 0,
                'activity_score': calculate_activity_score(total_stars, total_forks, recent_activity, public_repos)
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '2.0.0'
            }
        }

        # Create assets directory if it doesn't exist
        os.makedirs('assets', exist_ok=True)

        # Save comprehensive stats
        with open('assets/stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

        # Generate summary report
        generate_stats_summary(stats)

        print("✅ Statistics generated successfully!")
        print_stats_summary(stats)

        return True

    except Exception as e:
        print(f"❌ Error generating statistics: {e}")
        return False

def calculate_activity_score(stars, forks, recent_activity, repo_count):
    """Calculate overall activity score (0-100)"""
    if repo_count == 0:
        return 0

    # Base score from engagement
    engagement_score = min((stars + forks * 2) / repo_count * 2, 40)

    # Recent activity bonus
    activity_score = min(recent_activity * 10, 30)

    # Repository diversity bonus
    diversity_score = min(repo_count * 2, 30)

    total_score = engagement_score + activity_score + diversity_score
    return min(round(total_score), 100)

def generate_stats_summary(stats):
    """Generate a human-readable stats summary"""
    summary = f"""# 📊 GitHub Statistics Summary

**Profile Overview:**
- 👤 Username: {stats['profile']['username']}
- 📂 Public Repositories: {stats['profile']['total_repos']}
- ⭐ Total Stars: {stats['profile']['total_stars']}
- 🍴 Total Forks: {stats['profile']['total_forks']}
- 👥 Followers: {stats['profile']['followers']}

**Repository Insights:**
- 💾 Total Size: {stats['repositories']['total_size_mb']} MB
- 📈 Recent Activity (30d): {stats['repositories']['recent_activity_30d']} repos
- 🔥 Activity Score: {stats['activity']['activity_score']}/100

**Top Languages:**
"""

    # Add top languages
    for lang, size in list(stats['languages']['top_languages'].items())[:5]:
        summary += f"- {lang}: {round(size/1024, 1)} MB\n"

    summary += f"""
**Generated:** {stats['metadata']['generated_at']}
"""

    # Save summary
    with open('assets/stats_summary.md', 'w') as f:
        f.write(summary)

def print_stats_summary(stats):
    """Print stats summary to console"""
    print("\n📊 Statistics Summary:")
    print(f"  📂 Repositories: {stats['profile']['total_repos']}")
    print(f"  ⭐ Total Stars: {stats['profile']['total_stars']}")
    print(f"  🍴 Total Forks: {stats['profile']['total_forks']}")
    print(f"  💻 Languages: {stats['languages']['language_count']}")
    print(f"  🏷️  Topics: {stats['topics']['topic_count']}")
    print(f"  🔥 Activity Score: {stats['activity']['activity_score']}/100")
    print(f"  📈 Recent Activity: {stats['repositories']['recent_activity_30d']} repos (30d)")

    if stats['languages']['top_languages']:
        top_lang = list(stats['languages']['top_languages'].keys())[0]
        print(f"  🚀 Primary Language: {top_lang}")

if __name__ == "__main__":
    success = generate_advanced_stats()
    if not success:
        sys.exit(1)