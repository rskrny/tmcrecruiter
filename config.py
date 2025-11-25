# config.py

# -----------------------------------------------------------------------------
# KEYWORD STRATEGY: TIFFANY CHAO (Senior PR & Communications)
# Profile: 8+ years Entertainment PR at Paramount/Nickelodeon
# Target: Manager to Director level roles in Entertainment/Media PR
# -----------------------------------------------------------------------------

# TIER 1: THE "SNIPER" SHOTS (100 Points)
# These match her specific expertise in Entertainment PR and Media Communications.
TIER_1_KEYWORDS = [
    # Core PR Titles
    "Public Relations",
    "PR Manager",
    "PR Director",
    "PR Lead",
    "Head of PR",
    "VP of PR",
    "Senior Publicist",
    "Publicist",
    "Publicity Manager",
    "Publicity Director",
    "Director of Public Relations",
    
    # Communications Titles
    "Communications Manager",
    "Communications Director",
    "Communications Lead",
    "Director of Communications",
    "Head of Communications",
    "VP of Communications",
    "Corporate Communications",
    "Brand Communications",
    "Chief Communications Officer",
    
    # Entertainment-Specific (Her Niche)
    "Entertainment PR",
    "Entertainment Publicity",
    "Studio Publicity",
    "Talent Publicity",
    "Brand Publicity",
    "Press Manager",
    "Press Director",
    
    # Senior/Strategic
    "Media Relations",
    "External Affairs",
    "Corporate Affairs",
]

# TIER 2: THE "BROAD" NET (50 Points)
# Adjacent roles she is qualified for but might be less "perfect".
TIER_2_KEYWORDS = [
    # Strategy & Planning
    "Strategic Communications",
    "Media Strategy",
    "Press Relations",
    "Press Campaign",
    
    # Crisis & Reputation
    "Crisis Communications",
    "Reputation Management",
    
    # Entertainment Industry Terms
    "Talent Relations",
    "Studio Relations",
    "Unit Publicity",
    "Event Publicity",
    "Awards Campaign",
    "Tentpole",
    
    # Internal Comms (Backup)
    "Internal Communications",
    
    # Industry Context (Helps with description matching)
    "Entertainment",
    "Media Company",
    "Streaming",
    "Film",
    "Television",
]

# NEGATIVE KEYWORDS: THE "NOISE" FILTER (Immediate Discard)
# Roles that are too junior, irrelevant, or technical.
# NOTE: Be careful not to over-filter entertainment roles
NEGATIVE_KEYWORDS = [
    # Junior / Entry Level (Too junior for 8+ years experience)
    "Intern", "Internship", "Entry Level", "Junior",
    
    # Support Roles (Too junior - but see exceptions below)
    "Assistant",  # Blocks "Executive Assistant", "Admin Assistant" etc.
    
    # Sales / BD (Wrong track entirely)
    "Sales", "SDR", "BDR", "Account Executive", "Business Development",
    
    # Tech / Product (Wrong industry)
    "Software", "Engineer", "Developer", "Full Stack", "Designer", 
    "Product Manager", "Project Manager",
    
    # The "Wrong" Kind of Marketing (Tech/Growth/Performance)
    "Product Marketing",
    "Growth Marketing",
    "Growth",
    "Performance Marketing",
    "Demand Generation",
    "User Acquisition",
    "Paid Media",
    "PPC",
    "SEO",
    "SEM",
    "Email Marketing",
    "Digital Marketing",
    
    # Social/Community (Execution-level, not strategic)
    "Social Media Manager",
    "Community Manager",
]

# NOTE ON COORDINATOR: 
# Removed "Coordinator" from negatives. In entertainment, "Publicity Coordinator"
# can be a mid-level role at smaller studios. We'll catch bad ones with low scores.

# NOTE ON CONTENT MARKETING:
# Removed "Content Marketing" from negatives. In entertainment/media companies,
# this often means editorial storytelling, which aligns with Tiffany's brand work.

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
# We support 'greenhouse', 'lever', 'workday', and 'netflix' board types.
# OPTIMIZED FOR: Entertainment, Media, Music, Streaming, Gaming
ATS_SOURCES = [
    # MAJOR ENTERTAINMENT / STUDIOS
    {"name": "A24", "url": "https://boards.greenhouse.io/a24", "type": "greenhouse"},
    
    # STREAMING / DIGITAL MEDIA
    {"name": "Netflix", "url": "https://explore.jobs.netflix.net/api/apply/v2/jobs", "type": "netflix"},
    {"name": "Disney", "url": "https://disney.wd5.myworkdayjobs.com/wday/cxs/disney/disneycareer/jobs", "type": "workday", "base_url": "https://disney.wd5.myworkdayjobs.com/en-US/disneycareer"},
    {"name": "Roku", "url": "https://boards.greenhouse.io/roku", "type": "greenhouse"},
    {"name": "Vimeo", "url": "https://boards.greenhouse.io/vimeo", "type": "greenhouse"},
    {"name": "Twitch", "url": "https://boards.greenhouse.io/twitch", "type": "greenhouse"},
    {"name": "Discord", "url": "https://boards.greenhouse.io/discord", "type": "greenhouse"},
    
    # MUSIC / AUDIO
    {"name": "Sony Music", "url": "https://boards.greenhouse.io/sonymusic", "type": "greenhouse"},
    {"name": "Spotify", "url": "https://jobs.lever.co/spotify", "type": "lever"},
    
    # PUBLISHING / MEDIA
    {"name": "Condé Nast", "url": "https://condenast.wd5.myworkdayjobs.com/wday/cxs/condenast/CondeCareers/jobs", "type": "workday", "base_url": "https://condenast.wd5.myworkdayjobs.com/en-US/CondeCareers"},
    {"name": "Vox Media", "url": "https://boards.greenhouse.io/voxmedia", "type": "greenhouse"},
    {"name": "Axios", "url": "https://boards.greenhouse.io/axios", "type": "greenhouse"},
    {"name": "BuzzFeed", "url": "https://boards.greenhouse.io/buzzfeed", "type": "greenhouse"},
    {"name": "The New York Times", "url": "https://boards.greenhouse.io/thenewyorktimes", "type": "greenhouse"},
    
    # GAMING / INTERACTIVE (Strong PR Depts)
    {"name": "Epic Games", "url": "https://boards.greenhouse.io/epicgames", "type": "greenhouse"},
    
    # CREATIVE / TECH with strong comms depts
    {"name": "Skillshare", "url": "https://jobs.lever.co/skillshare", "type": "lever"},
]

# RSS Feed for Working Nomads specifically
WORKING_NOMADS_RSS = "https://www.workingnomads.com/jobs.rss?category=marketing"

# -----------------------------------------------------------------------------
# SYSTEM SETTINGS
# -----------------------------------------------------------------------------
MIN_SCORE_THRESHOLD = 40  # Lowered from 60 to catch description-matches
