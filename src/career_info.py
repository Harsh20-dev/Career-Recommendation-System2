# -*- coding: utf-8 -*-
"""
Career info database - fully offline / rule-based.
Maps each of the 125 career labels to a broad category, and gives that
category a roadmap, skills-to-learn list, and approximate India salary range.

Salary figures are ROUGH MARKET AVERAGES (2026, India) gathered from public
salary-guide sources; actual pay varies a lot by city, company, and skills.
"""

CATEGORY_INFO = {
    "engineering_core": {
        "exam": "JEE (Main/Advanced)",
        "degree": "B.Tech / B.E. (relevant branch)",
        "salary_fresher": "₹3–5 LPA",
        "salary_experienced": "₹12–25 LPA (5-10 yrs); ₹30+ LPA in aerospace/robotics/oil & gas niches",
        "roadmap": [
            "Keep your PCM (Physics, Chemistry, Maths) strong in grades 11-12 and prepare for JEE Main/Advanced.",
            "Clear JEE and get into a B.Tech/B.E. program (NIT/IIT/a good state college).",
            "Build a strong grip on CAD tools (AutoCAD, SolidWorks) and core subject fundamentals during college.",
            "Do internships at core companies (L&T, Tata, Mahindra, ISRO, DRDO) from your 2nd/3rd year onward.",
            "Build a solid final-year project/thesis; consider GATE for PSU jobs or higher studies.",
            "Get a job via placements or a PSU/govt exam; grow through specialization/M.Tech over 3-5 years.",
        ],
        "skills": ["Core subject fundamentals (mechanics/thermo/circuits etc.)", "CAD software (AutoCAD, SolidWorks, CATIA)",
                    "Problem-solving & analytical thinking", "Project management basics", "Industry certifications (Six Sigma later)"],
    },
    "tech_software": {
        "exam": "JEE (Main) / direct entry via BCA/BSc",
        "degree": "B.Tech CSE/IT, BCA, or BSc Computer Science",
        "salary_fresher": "₹3.5–8 LPA (₹15–25 LPA at top product companies)",
        "salary_experienced": "₹20–50+ LPA (5-8 yrs, product/FAANG-tier companies)",
        "roadmap": [
            "Build strong maths and logical reasoning; get into a CS/IT degree (B.Tech, BCA, or BSc) via JEE/CUET.",
            "Learn a programming language (Python/Java/C++) and build a solid grip on Data Structures & Algorithms.",
            "Build personal projects and put together a portfolio on GitHub.",
            "Do internships (startups/product companies) and contribute to open-source projects.",
            "Pick up skills/certifications relevant to your specialization (cloud, ML, cybersecurity, etc.).",
            "Land a job via campus placements or direct applications; keep practicing DSA + system design for fast growth.",
        ],
        "skills": ["Programming (Python/Java/C++)", "Data Structures & Algorithms", "Git/version control",
                    "Cloud basics (AWS/Azure/GCP)", "System design & problem-solving"],
    },
    "medical": {
        "exam": "NEET",
        "degree": "MBBS / BDS / BSc Nursing / B.Pharm (depending on the career)",
        "salary_fresher": "₹4–8 LPA (₹25k–70k/month)",
        "salary_experienced": "₹15–50+ LPA (with specialization/private practice)",
        "roadmap": [
            "Keep your PCB (Physics, Chemistry, Biology) strong in grades 11-12 and prepare for NEET.",
            "Clear NEET and get into an MBBS/BDS/related degree program.",
            "Focus on clinical/practical training during your degree, and complete your internship.",
            "If you want to specialize, prepare for exams like NEET-PG.",
            "Complete your residency/internship and get licensed (NMC registration).",
            "Start working at a govt/private hospital; grow into specialization/private practice with experience.",
        ],
        "skills": ["Biology & clinical knowledge", "Patient communication & empathy", "Attention to detail",
                    "Stress management", "Continuous medical education"],
    },
    "science_research": {
        "exam": "CUET (UG) / GATE-CSIR-NET (PG level)",
        "degree": "BSc → MSc → PhD in relevant science",
        "salary_fresher": "₹3–6 LPA",
        "salary_experienced": "₹10–25 LPA (ISRO/DRDO/CSIR scientists: ₹15-30 LPA)",
        "roadmap": [
            "Pick your favorite subject in the Science stream and prepare for CUET.",
            "Get into a BSc program (Physics/Chemistry/Biology/Environmental Science, whichever is relevant).",
            "Get hands-on research experience in labs, and complete your MSc.",
            "Clear exams like CSIR-NET/GATE for research/teaching positions.",
            "Do a PhD or research fellowship (ISRO, DRDO, CSIR labs, universities).",
            "Grow your career as a research scientist/professor through publications and projects.",
        ],
        "skills": ["Research methodology", "Data analysis & statistics", "Lab techniques",
                    "Scientific writing", "Critical thinking"],
    },
    "business_finance": {
        "exam": "CA-Foundation / CUET",
        "degree": "B.Com / BBA / CA / MBA",
        "salary_fresher": "₹4–9 LPA (qualified CA: ₹6-12 LPA)",
        "salary_experienced": "₹15–40+ LPA (senior manager/leadership roles)",
        "roadmap": [
            "Choose the Commerce stream and build a strong grip on Accountancy/Economics/Business Studies.",
            "Get into a B.Com/BBA program, or start preparing for CA Foundation.",
            "Learn Excel, financial modeling, and accounting software (Tally, SAP).",
            "Do internships (audit firms/banks/corporates); consider certifications like CA/CFA.",
            "Pick your specialization and complete the relevant exams/certifications.",
            "Start with an entry-level job and grow into a managerial role over 3-5 years.",
        ],
        "skills": ["Financial accounting & analysis", "Excel & financial modeling", "Business communication",
                    "Analytical & numerical skills", "Industry certifications (CA/CFA/MBA)"],
    },
    "law_governance": {
        "exam": "CLAT (law) / UPSC (civil services & police)",
        "degree": "LLB, or any graduation degree + UPSC preparation",
        "salary_fresher": "₹6–12 LPA (govt pay scale) / ₹4-8 LPA (law firms)",
        "salary_experienced": "₹20–40+ LPA (senior advocates / senior govt pay scale)",
        "roadmap": [
            "Choose CLAT for law, or any graduation + UPSC path for civil services/police.",
            "Law: clear CLAT and get into a 5-year LLB program. Civil services: complete your graduation.",
            "Practice current affairs, the constitution, and reasoning daily.",
            "Prepare through internships (law firms/courts) or UPSC coaching/mock tests.",
            "Clear the Bar exam/AIBE (lawyers) or UPSC Prelims-Mains-Interview (civil services).",
            "Start practicing/get your posting; seniority and pay grade grow with experience.",
        ],
        "skills": ["Constitutional/legal knowledge & current affairs", "Analytical reading & writing",
                    "Public speaking & argumentation", "Discipline & time management", "Ethics & integrity"],
    },
    "education": {
        "exam": "CUET",
        "degree": "B.Ed + relevant subject degree",
        "salary_fresher": "₹2.5–5 LPA",
        "salary_experienced": "₹8–20 LPA (private/international schools; ed-tech can be higher)",
        "roadmap": [
            "Choose your subject specialization and get into a relevant BA/BSc program via CUET.",
            "Complete a B.Ed or teaching-specific degree.",
            "Do teaching internships/practice classes, and polish your communication skills.",
            "Prepare for TET/CTET for govt jobs, or apply to private/international schools.",
            "You can also explore ed-tech platforms (Byju's, Unacademy, Physics Wallah).",
            "Grow into a senior teacher/HOD/principal role, or start your own coaching institute, with experience.",
        ],
        "skills": ["Subject-matter expertise", "Communication & patience", "Classroom management",
                    "Curriculum planning", "Digital teaching tools"],
    },
    "social_psych": {
        "exam": "CUET",
        "degree": "BA/MA Psychology, or MSW (Social Work)",
        "salary_fresher": "₹2.5–5 LPA",
        "salary_experienced": "₹8–15 LPA (leadership NGO/clinical roles)",
        "roadmap": [
            "Choose the Arts/Humanities stream and pick a subject like Psychology/Sociology.",
            "Get into a BA Psychology/Social Work program via CUET.",
            "Do counseling/NGO/fieldwork internships for practical experience.",
            "Do an MA/MSW for specialization (clinical psychology, counseling, etc.).",
            "Get licensed/registered if required (e.g. RCI registration for counselors).",
            "Start working at an NGO/hospital/school/private practice; grow into leadership roles with experience.",
        ],
        "skills": ["Empathy & active listening", "Counseling techniques", "Communication skills",
                    "Case documentation", "Community outreach"],
    },
    "media_creative": {
        "exam": "CUET",
        "degree": "BA Journalism/Mass Comm, or relevant creative degree",
        "salary_fresher": "₹2.5–5 LPA",
        "salary_experienced": "₹8–20 LPA (top agencies/media houses)",
        "roadmap": [
            "Develop your writing/creative skills and get into a Journalism/Mass Comm/relevant degree via CUET.",
            "Build a portfolio during college (blog, videos, designs, whichever is relevant).",
            "Do internships at media houses/agencies/production houses.",
            "Learn the relevant tools (editing software, camera, writing tools).",
            "Build experience through freelance projects or an entry-level job.",
            "Grow into a senior/specialist role, or build your own independent brand/channel, over 3-5 years.",
        ],
        "skills": ["Storytelling & writing", "Creativity", "Relevant software (editing/design tools)",
                    "Communication", "Social media savvy"],
    },
    "design": {
        "exam": "NATA (architecture) / CUET / design entrance",
        "degree": "B.Arch / B.Des",
        "salary_fresher": "₹2.5–5 LPA",
        "salary_experienced": "₹15–40 LPA (senior/freelance/firm partner)",
        "roadmap": [
            "Prepare for NATA/CUET/design entrance exams and develop your sketching and creativity.",
            "Get into a B.Arch/B.Des program.",
            "Learn design software (AutoCAD, SketchUp, Adobe Suite - whichever is relevant).",
            "Do internships at firms/studios, and build a portfolio.",
            "Get registered/licensed if required (e.g. COA registration for architects).",
            "Start with a job or freelance work, and grow into your own studio/firm over time.",
        ],
        "skills": ["Sketching & visualization", "Design software (AutoCAD/SketchUp/Adobe)",
                    "Creativity & spatial thinking", "Client communication", "Project management"],
    },
    "sports_fitness": {
        "exam": "CUET / trade-specific certification",
        "degree": "BPEd / Sports Science, or specialized certification",
        "salary_fresher": "₹2–4 LPA",
        "salary_experienced": "₹8–20 LPA (top athletes/coaches can earn much more)",
        "roadmap": [
            "Build practice and fitness in your sport/fitness area.",
            "Do a BPEd/Sports Science degree or a specialized certification course.",
            "Compete at state/national level (for athletes) or get a coaching certification.",
            "Do an assistant role/internship with gyms/academies/sports bodies.",
            "Get a certification relevant to your specialization (e.g. NASM/ACE for fitness trainers).",
            "Build a professional/coaching career; grow your own academy/brand with experience.",
        ],
        "skills": ["Physical fitness & technique", "Sports/fitness certifications", "Discipline & motivation",
                    "Basic nutrition knowledge", "Communication & coaching skills"],
    },
    "trades_vocational": {
        "exam": "ITI-Entrance",
        "degree": "ITI Certificate / Diploma",
        "salary_fresher": "₹1.2–2.4 LPA (₹10k–20k/month)",
        "salary_experienced": "₹3–5 LPA (skilled/self-employed can earn more)",
        "roadmap": [
            "Choose your trade after 10th grade and clear the ITI-Entrance exam.",
            "Complete a 1-2 year ITI course, focusing on practical training.",
            "Do an apprenticeship at a company/workshop (via the NAPS scheme).",
            "Get a relevant certification/license if required.",
            "Start a job (private/govt) or work freelance/self-employed.",
            "Upgrade your skills with experience; you can also start your own business/workshop.",
        ],
        "skills": ["Hands-on technical skill (trade-specific)", "Tool handling & safety",
                    "Practical problem-solving", "Basic customer dealing", "Reliability & work ethic"],
    },
}

CAREER_TO_CATEGORY = {}

_GROUPS = {
    "engineering_core": [
        "Aerospace Engineer", "Automobile Engineer", "Biomedical Engineer", "Chemical Engineer",
        "Civil Engineer", "Electrical Engineer", "Electronics Engineer", "Environmental Engineer",
        "Industrial Engineer", "Mechanical Engineer", "Mining Engineer", "Robotics Engineer",
        "Structural Engineer", "Diploma Engineering Technician",
    ],
    "tech_software": [
        "AI Research Engineer", "Blockchain Developer", "Cloud Architect", "Cybersecurity Analyst",
        "Data Analyst (Research)", "Data Scientist", "Database Administrator", "DevOps Engineer",
        "Game Developer", "IT Support Specialist", "Machine Learning Engineer", "Mobile App Developer",
        "QA / Test Engineer", "Site Reliability Engineer", "Software Engineer", "UX/UI Designer",
    ],
    "medical": [
        "Dentist", "Doctor (MBBS)", "Medical Lab Technician", "Nurse", "Nutritionist / Dietitian",
        "Paramedic", "Pharmacist", "Physiotherapist", "Public Health Officer", "Radiologist",
        "Surgeon", "Sports Physiotherapist", "Veterinarian",
    ],
    "science_research": [
        "Agricultural Scientist", "Astronomer", "Biotechnologist", "Chemist", "Environmental Scientist",
        "Geologist", "Marine Biologist", "Physicist", "Research Scientist", "Wildlife Conservationist",
        "Horticulturist", "Forestry Officer",
    ],
    "business_finance": [
        "Actuary", "Auditor", "Business Analyst", "Chartered Accountant (CA)", "Financial Analyst",
        "HR Manager", "Insurance Underwriter", "Investment Banker", "Management Consultant",
        "Operations Manager", "Product Manager", "Project Manager", "Retail Manager",
        "Stockbroker / Trader", "Supply Chain Manager", "Tax Consultant", "General Manager",
        "Entrepreneur", "Sustainability Consultant", "Public Policy Analyst",
    ],
    "law_governance": [
        "Civil Servant (IAS/IPS/IFS)", "Defence Services Officer", "Diplomat", "Judge",
        "Lawyer / Advocate", "Legal Consultant", "Police Officer",
    ],
    "education": [
        "Corporate Trainer", "Curriculum Designer", "Ed-Tech Content Developer", "Education Counselor",
        "Special Educator", "Teacher / Professor", "Child Development Specialist",
    ],
    "social_psych": [
        "Counselor / Therapist", "NGO Program Manager", "Psychologist", "Rehabilitation Specialist",
        "Social Worker",
    ],
    "media_creative": [
        "Animator", "Broadcast/RJ Presenter", "Content Creator", "Copywriter", "Digital Marketer",
        "Film Director", "Film/Video Editor", "Graphic Designer", "Illustrator", "Journalist",
        "Photographer", "Public Relations Specialist", "Social Media Manager",
    ],
    "design": [
        "Architect", "Fashion Designer", "Industrial/Product Designer", "Interior Designer",
    ],
    "sports_fitness": [
        "Fitness Trainer", "Professional Athlete", "Sports Coach", "Sports Management Professional",
        "Yoga Instructor",
    ],
    "trades_vocational": [
        "Automobile Technician", "Beautician / Hairstylist", "Carpenter", "CNC Machine Operator",
        "Culinary Arts / Chef", "Electrician (ITI)", "Plumber (ITI)", "Tailor / Fashion Technician",
        "Welder / Fabricator",
    ],
}

for _cat, _careers in _GROUPS.items():
    for _c in _careers:
        CAREER_TO_CATEGORY[_c] = _cat


def get_career_info(career_name):
    """Return roadmap/skills/salary info dict for a given career label."""
    category = CAREER_TO_CATEGORY.get(career_name, "business_finance")  # sensible fallback
    info = dict(CATEGORY_INFO[category])
    info["category"] = category
    info["roadmap"] = [step.replace("{career}", career_name) for step in info["roadmap"]]
    return info
