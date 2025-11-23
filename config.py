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
    "ODwyers": "https://www.odwyerpr.com/pr_jobs/",

    # Keep the best of the rest (but filtered strictly)
    "WeWorkRemotely_Management": "https://weworkremotely.com/categories/management-and-finance/jobs.rss",
    "RemoteOK": "https://remoteok.com/remote-communications-jobs.rss",
}

# RSS Feed for Working Nomads specifically
WORKING_NOMADS_RSS = "https://www.workingnomads.com/jobs.rss?category=marketing"

# -----------------------------------------------------------------------------
# SYSTEM SETTINGS
# -----------------------------------------------------------------------------
MIN_SCORE_THRESHOLD = 40  # Lowered from 60 to catch description-matches
