#!/usr/bin/env python3
"""
Advanced GitHub Profile Project Updater
File: scripts/update_projects.py
"""

import os
import json
import requests
from github import Github
from datetime import datetime
import sys

def load_config():
    """Load configuration from config file"""
    try:
        with open('config/profile_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Config file not found, using defaults")
        return {
            "projects": {
                "max_display": 3,
                "exclude_repos": ["dotfiles", "config"],
                "show_if_empty": False
            }
        }

def get_top_repositories(username, token, max_repos=3):
    """Get top repositories with intelligent scoring"""
    try:
        g = Github(token)
        user = g.get_user(username)

        repos = []
        config = load_config()
        excluded = config['projects']['exclude_repos'] + [username]

        print(f"🔍 Scanning repositories for {username}...")

        for repo in user.get_repos(sort='updated', direction='desc'):
            # Skip excluded repositories
            if repo.name in excluded or repo.fork or repo.private:
                print(f"⏭️  Skipping {repo.name} (excluded/fork/private)")
                continue

            # Skip repositories without meaningful description
            if not repo.description or len(repo.description.strip()) < 10:
                print(f"⏭️  Skipping {repo.name} (no description)")
                continue

            # Calculate repository score
            score = calculate_repo_score(repo)

            repo_data = {
                'name': repo.name,
                'description': repo.description,
                'url': repo.html_url,
                'language': repo.language or 'Markdown',
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'updated': repo.updated_at,
                'score': score
            }

            repos.append(repo_data)
            print(f"✅ Added {repo.name} (⭐{repo['stars']}, score: {score})")

        # Sort by score and return top repos
        repos.sort(key=lambda x: x['score'], reverse=True)
        top_repos = repos[:max_repos]

        print(f"🏆 Selected top {len(top_repos)} repositories")
        return top_repos

    except Exception as e:
        print(f"❌ Error fetching repositories: {e}")
        return []

def calculate_repo_score(repo):
    """Calculate repository score based on multiple factors"""
    score = 0

    # Base score from stars and forks
    score += repo.stargazers_count * 10
    score += repo.forks_count * 5

    # Recent activity bonus
    days_since_update = (datetime.now() - repo.updated_at.replace(tzinfo=None)).days
    if days_since_update < 7:
        score += 100
    elif days_since_update < 30:
        score += 50
    elif days_since_update < 90:
        score += 25

    # Language popularity bonus
    popular_languages = {
        'JavaScript': 20, 'TypeScript': 25, 'Python': 20,
        'React': 30, 'Vue': 20, 'Go': 20, 'Rust': 25,
        'Java': 15, 'Swift': 15, 'Kotlin': 15
    }
    score += popular_languages.get(repo.language, 5)

    # Description quality bonus
    if repo.description and 20 <= len(repo.description) <= 150:
        score += 15

    return max(score, 0)

def get_language_emoji(language):
    """Get emoji for programming language"""
    emojis = {
        'JavaScript': '⚡', 'TypeScript': '🔷', 'Python': '🐍',
        'Java': '☕', 'Go': '🚀', 'Rust': '⚙️', 'C++': '🔧',
        'HTML': '🌐', 'CSS': '🎨', 'Vue': '💚', 'React': '⚛️',
        'PHP': '🐘', 'Ruby': '💎', 'Swift': '🍎', 'Kotlin': '🎯'
    }
    return emojis.get(language, '📦')

def get_language_color(language):
    """Get color for programming language"""
    colors = {
        'JavaScript': '00ff41', 'TypeScript': '00ffff', 'Python': 'ff0080',
        'Java': 'ff6b35', 'Go': '00ff41', 'Rust': 'ff0080', 'C++': '00ffff',
        'HTML': '00ffff', 'CSS': 'ff6b35', 'Vue': '00ff41', 'React': '00ffff',
        'PHP': 'ff0080', 'Ruby': 'ff6b35', 'Swift': '00ffff', 'Kotlin': '00ff41'
    }
    return colors.get(language, '00ff41')

def truncate_description(desc, max_length=55):
    """Intelligently truncate description"""
    if len(desc) <= max_length:
        return desc

    truncated = desc[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.7:
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

def generate_project_cards(repos, username):
    """Generate HTML for project cards"""
    if not repos:
        print("📝 No repositories to display")
        return ""

    cards_html = []

    # Header section
    project_count = len(repos)
    title_text = f"TOP {project_count} PROJECT{'S' if project_count != 1 else ''}"

    cards_html.append(f'''
<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/219923823-bf1ce878-c6b8-4faa-be07-93e6b1006521.gif" width="100">
  <h2>🚀 {title_text}</h2>
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=40&section=header&text=FEATURED_BUILDS&fontSize=16&fontColor=00ff41&animation=blinking" />
</div>
''')

    # Project cards in a row
    cards_html.append('<div align="center">')

    for repo in repos:
        emoji = get_language_emoji(repo['language'])
        color = get_language_color(repo['language'])
        clean_name = repo['name'].upper().replace('-', '_').replace('.', '_')
        desc = truncate_description(repo['description'])

        # Calculate update info
        days_ago = (datetime.now() - repo['updated'].replace(tzinfo=None)).days
        if days_ago == 0:
            update_text = "Updated today"
        elif days_ago == 1:
            update_text = "Updated yesterday"
        elif days_ago < 7:
            update_text = f"Updated {days_ago} days ago"
        else:
            update_text = f"Updated {repo['updated'].strftime('%b %Y')}"

        card = f'''
  <div style="display: inline-block; margin: 15px; vertical-align: top; min-width: 280px;">
    <a href="{repo['url']}" target="_blank">
      <img src="https://img.shields.io/badge/{emoji}_{clean_name}-{color}?style=for-the-badge&logoColor=white&labelColor=000000" alt="{repo['name']}" />
    </a>
    <br><br>
    <sub><b>{desc}</b></sub>
    <br>
    <sub>
      <code>{repo['language']}</code> •
      <code>⭐ {repo['stars']}</code> •
      <code>🍴 {repo['forks']}</code>
    </sub>
    <br>
    <sub><i>{update_text}</i></sub>
  </div>'''

        cards_html.append(card)

    cards_html.append('</div>')

    # Add stats summary
    total_stars = sum(repo['stars'] for repo in repos)
    total_forks = sum(repo['forks'] for repo in repos)
    languages = set(repo['language'] for repo in repos if repo['language'])

    stats_text = f"STATS:_{total_stars}_STARS_•_{total_forks}_FORKS_•_{len(languages)}_LANGUAGES"

    cards_html.append(f'''
<br>
<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=30&section=header&text={stats_text}&fontSize=12&fontColor=00ff41" />
</div>

<div align="center">
  <a href="https://github.com/{username}?tab=repositories&sort=stargazers">
    <img src="https://img.shields.io/badge/VIEW_ALL_PROJECTS-00ff41?style=for-the-badge&logo=github&logoColor=black&labelColor=000000" />
  </a>
</div>
''')

    return '\n'.join(cards_html)

def update_readme():
    """Update README with new project section"""
    username = os.getenv('USERNAME')
    token = os.getenv('GITHUB_TOKEN')
    has_repos = os.getenv('HAS_REPOS') == 'true'

    if not username or not token:
        print("❌ Missing environment variables USERNAME or GITHUB_TOKEN")
        return False

    print(f"🔍 Updating profile for {username}")
    print(f"📊 Has repositories: {has_repos}")

    if not has_repos:
        print("🚫 No repositories found, hiding projects section")
        project_section = ""
    else:
        # Get top repositories
        repos = get_top_repositories(username, token)
        print(f"✅ Processing {len(repos)} top repositories")

        if not repos:
            project_section = ""
        else:
            project_section = generate_project_cards(repos, username)

    # Read current README
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ README.md not found!")
        return False

    # Define markers for project section
    start_marker = '<!-- DYNAMIC_PROJECTS_START -->'
    end_marker = '<!-- DYNAMIC_PROJECTS_END -->'

    # Find and replace the section
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)

    if start_pos == -1 or end_pos == -1:
        print("❌ Project section markers not found in README!")
        print("Add these markers to your README:")
        print(f"  {start_marker}")
        print(f"  {end_marker}")
        return False

    # Calculate positions
    end_pos += len(end_marker)

    # Create new content
    if project_section:
        new_section = f"{start_marker}\n{project_section}\n{end_marker}"
    else:
        new_section = f"{start_marker}\n{end_marker}"

    # Replace the section
    new_content = content[:start_pos] + new_section + content[end_pos:]

    # Write updated README
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("✅ README updated successfully!")
        print(f"📅 Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        return True

    except Exception as e:
        print(f"❌ Error writing README: {e}")
        return False

if __name__ == "__main__":
    success = update_readme()
    if not success:
        sys.exit(1)