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
    "PR Lead",
    "Communications Manager",
    "Communications Director",
    "Communications Lead",
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
    "Chief Communications Officer",
    "Publicist"
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
    # Junior / Generic
    "Intern", "Internship", "Assistant", "Coordinator", "Entry Level", "Junior",
    
    # Sales
    "Sales", "SDR", "BDR", "Account Executive", "Business Development",
    
    # Tech / Product
    "Software", "Engineer", "Developer", "Full Stack", "Designer", "Product Manager", "Project Manager",
    
    # The "Wrong" Kind of Marketing (Tech/Growth/Performance)
    "Product Marketing",
    "Growth",
    "Performance Marketing",
    "Demand Generation",
    "User Acquisition",
    "Paid Media",
    "PPC",
    "SEO",
    "SEM",
    "Email Marketing",
    "Content Marketing", # Usually SEO-focused, not PR
    "Social Media Manager",
    "Community Manager",
    "Digital Marketing"
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
    # PRSA - Browse Page (Direct list, no search params needed)
    "PRSA_Browse": "https://jobs.prsa.org/",

    # The Muse - Simplified Query
    "TheMuse": "https://www.themuse.com/api/public/jobs?category=Public%20Relations&page=1",

    # EntertainmentCareers.net - The Hollywood Standard
    # Hard to scrape. We will try the main listing page.
    "EntertainmentCareers": "https://www.entertainmentcareers.net/jcat.asp?jcat=100", # PR Category

    # O'Dwyer's PR Jobs - Niche, high-quality PR board
    # "ODwyers": "https://www.odwyerpr.com/pr_jobs/index.htm", # Temporarily disabled due to 404

    # Keep the best of the rest (but filtered strictly)
    "WeWorkRemotely_Management": "https://weworkremotely.com/categories/management-and-finance/jobs.rss",
    "RemoteOK": "https://remoteok.com/remote-communications-jobs.rss",
}

# -----------------------------------------------------------------------------
# DIRECT AGENCY / STUDIO BOARDS (ATS)
# -----------------------------------------------------------------------------
# These are the "Hidden Gems". We go directly to the source.
# We support 'greenhouse' and 'lever' board types automatically.
ATS_SOURCES = [
    # ENTERTAINMENT / STUDIOS
    {"name": "A24", "url": "https://boards.greenhouse.io/a24", "type": "greenhouse"},
    {"name": "Vox Media", "url": "https://boards.greenhouse.io/voxmedia", "type": "greenhouse"},
    {"name": "Axios", "url": "https://boards.greenhouse.io/axios", "type": "greenhouse"},
    {"name": "Sony Music", "url": "https://boards.greenhouse.io/sonymusic", "type": "greenhouse"},
    {"name": "Roku", "url": "https://boards.greenhouse.io/roku", "type": "greenhouse"},
    {"name": "BuzzFeed", "url": "https://boards.greenhouse.io/buzzfeed", "type": "greenhouse"},
    {"name": "Vimeo", "url": "https://boards.greenhouse.io/vimeo", "type": "greenhouse"},
    {"name": "Discord", "url": "https://boards.greenhouse.io/discord", "type": "greenhouse"},
    {"name": "Twitch", "url": "https://boards.greenhouse.io/twitch", "type": "greenhouse"},
    
    # LEVER BOARDS
    {"name": "Spotify", "url": "https://jobs.lever.co/spotify", "type": "lever"},
    {"name": "Skillshare", "url": "https://jobs.lever.co/skillshare", "type": "lever"},
    
    # REMOVED BROKEN SOURCES
    # Patreon (Lever 404), Substack (Greenhouse 404)
]

# RSS Feed for Working Nomads specifically
WORKING_NOMADS_RSS = "https://www.workingnomads.com/jobs.rss?category=marketing"

# -----------------------------------------------------------------------------
# SYSTEM SETTINGS
# -----------------------------------------------------------------------------
MIN_SCORE_THRESHOLD = 40  # Lowered from 60 to catch description-matches
