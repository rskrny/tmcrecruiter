# config.py

# -----------------------------------------------------------------------------
# KEYWORD STRATEGY: TIFFANY CHAO (Senior PR & Communications)
# -----------------------------------------------------------------------------

# TIER 1: THE "SNIPER" SHOTS (100 Points)
# These match her specific expertise in PR, Entertainment, and Media.
TIER_1_KEYWORDS = [
    "Public Relations",
    "PR Manager",
    "PR Director",
    "Director of Communications",
    "Head of Communications",
    "Head of PR",
    "Senior Publicist",
    "Media Relations",
    "Publicity Manager",
    "VP of Communications",
    "Director of Public Relations",
    "External Affairs",
    "Corporate Affairs",
    "Chief Communications Officer"
]

# TIER 2: THE "BROAD" NET (50 Points)
# Adjacent roles she is qualified for but might be less "perfect".
TIER_2_KEYWORDS = [
    "Strategic Communications",
    "Press Relations",
    "Crisis Communications",
    "Internal Communications",
    "Reputation Management",
    "Talent Relations",
    "Studio Relations",
    "Entertainment",
    "Media Strategy"
]

# NEGATIVE KEYWORDS: THE "NOISE" FILTER (Immediate Discard)
# Roles that are too junior, irrelevant, or technical.
NEGATIVE_KEYWORDS = [
    "Intern",
    "Internship",
    "Assistant", 
    "Coordinator", 
    "Entry Level",
    "Junior",
    "Sales",
    "SDR",
    "BDR",
    "Account Executive", 
    "Customer Support",
    "Customer Service",
    "Software",
    "Engineer",
    "Developer",
    "Full Stack",
    "Designer",
    "SEO",
    "PPC",
    "Growth Hacker",
    "Content Writer", # Too junior usually
    "Social Media Manager" # She partners with them, doesn't do it
]

# -----------------------------------------------------------------------------
# LOCATION STRATEGY: LOS ANGELES (Hybrid/Remote)
# -----------------------------------------------------------------------------
# We prioritize jobs in these areas for Hybrid/On-site potential.
LOCATIONS = [
    "Los Angeles",
    "Santa Monica",
    "Culver City",
    "Burbank",
    "Hollywood",
    "Glendale",
    "Beverly Hills",
    "El Segundo",
    "Pasadena",
    "Sherman Oaks"
]

# -----------------------------------------------------------------------------
# DATA SOURCES
# -----------------------------------------------------------------------------
# We broaden the search to capture PR roles that might be miscategorized.

URLS = {
    # WWR: "Management" often holds Director/VP level Comms roles. "Marketing" holds the rest.
    "WeWorkRemotely_Marketing": "https://weworkremotely.com/categories/sales-and-marketing/jobs.rss",
    "WeWorkRemotely_Management": "https://weworkremotely.com/categories/management-and-finance/jobs.rss",
    
    # Remotive: We will fetch the full list or broader categories if possible, but 'marketing' is the main bucket.
    "Remotive": "https://remotive.com/api/remote-jobs?category=marketing",
    
    # RemoteOK: We can search by tag.
    "RemoteOK": "https://remoteok.com/remote-communications-jobs.rss",
    
    # WorkingNomads:
    "WorkingNomads": "https://www.workingnomads.com/jobs.rss?category=management&category=marketing"
}

# RSS Feed for Working Nomads specifically
WORKING_NOMADS_RSS = "https://www.workingnomads.com/jobs.rss?category=marketing"

# -----------------------------------------------------------------------------
# SYSTEM SETTINGS
# -----------------------------------------------------------------------------
MIN_SCORE_THRESHOLD = 60  # Only show jobs with at least one Tier 1 or multiple Tier 2 matches
