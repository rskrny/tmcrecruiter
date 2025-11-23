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
    # PRSA (Public Relations Society of America) - The Gold Standard
    # We use their RSS feed if available, or we will scrape their search results page.
    # Note: PRSA uses Web Scribble, which often has an RSS feed at /jobs/rss
    "PRSA_Remote": "https://jobs.prsa.org/jobs/rss?keywords=Public+Relations&location=Remote",
    "PRSA_LA": "https://jobs.prsa.org/jobs/rss?keywords=Public+Relations&location=Los+Angeles%2C+CA",

    # The Muse - Good for Agency/Media culture
    # They have a hidden RSS feed for searches usually, or we scrape the JSON API.
    # For simplicity in this version, we will use their internal API endpoint if possible, 
    # or fall back to a standard feed if we can find one. 
    # Actually, The Muse has a public API: https://www.themuse.com/api/public/jobs
    "TheMuse": "https://www.themuse.com/api/public/jobs?category=Public%20Relations&category=Creative%20%26%20Design&category=Marketing&location=Los%20Angeles%2C%20CA&location=Flexible%20%2F%20Remote&page=1",

    # EntertainmentCareers.net - The Hollywood Standard
    # Hard to scrape. We will try the main listing page.
    "EntertainmentCareers": "https://www.entertainmentcareers.net/jcat.asp?jcat=100", # PR Category

    # Keep the best of the rest (but filtered strictly)
    "WeWorkRemotely_Management": "https://weworkremotely.com/categories/management-and-finance/jobs.rss",
    "RemoteOK": "https://remoteok.com/remote-communications-jobs.rss",
}

# RSS Feed for Working Nomads specifically
WORKING_NOMADS_RSS = "https://www.workingnomads.com/jobs.rss?category=marketing"

# -----------------------------------------------------------------------------
# SYSTEM SETTINGS
# -----------------------------------------------------------------------------
MIN_SCORE_THRESHOLD = 60  # Only show jobs with at least one Tier 1 or multiple Tier 2 matches
