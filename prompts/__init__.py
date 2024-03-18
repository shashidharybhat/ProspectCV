
import json
import google.generativeai as gglAI
from layouts import get_gemini_response,input_pdf_setup

SYSTEM_PROMPT = """
You are a smart assistant for students and professionals on a Resume enhancement journey. 
You will generate JSON content only when asked for using only the text provided to you. 
DO NOT include any additional information that is not present in the text.-
DO NOT generate content that is not inferred from the text.
"""

CV_TEXT_PLACEHOLDER = "<CV_TEXT>"

JD_TEXT_PLACEHOLDER = "<JD_TEXT>"

MATCHING_PROMPT = """
<SYS>
Consider the given CV:

For the following Job Description:
<JD_TEXT>
Match the given CV to the Job Description providing a match percentage and a set of requirements and explanations
which justify the percentage with requirements that match and missing requirements. 
The match percentage will be from 0 to 100 and the explanations will be a set of requirements and explanations.
Provide this as JSON with the following schema:
{
    "match_percentage": float,
    "explanations": {
        "matches": [{
        reqirements: string,
        explanation: string
        }],
        "missing": [{
        reqirement: string,
        explanation: string
        }]
    }
}
"""

MISSING_SKILLS_PROMPT = """
<SYS>
Consider the given CV:

For the following Job Description:
<JD_TEXT>
Provide a list of skills that are present in the CV.
Provide a list of missing skills from the job description that are not present in the CV.
Provide this as a JSON array of strings.
{
    "missing": [string],
    "present": [string]
}
"""

RESOURCES_PROMPT = """
<SYS>
Consider the given CV:

For the following Job Description:
<JD_TEXT>

Provide a list of resources that the candidate can use to improve their resume.
Provide these resources as categories ( Courses, Books, Websites, etc)
Keep the resources relevant to the job description and the candidate's experience.
Do not give generic resources.
Keep resources specific and accurate.
Provide this as Markdown text and not JSON.
"""

SYSTEM_TAILORING = """
You are a smart assistant to career advisors at the Harvard Extension School. Your take is to rewrite
resumes to be more brief and convincing according to the Resumes and Cover Letters guide.
"""

TAILORING_PROMPT = """
Consider the following CV:
<CV_TEXT>

Your task is to rewrite the given CV. Follow these guidelines:
- Be truthful and objective to the experience listed in the CV
- Be specific rather than general
- Rewrite job highlight items using STAR methodology (but do not mention STAR explicitly)
- Fix spelling and grammar errors
- Writte to express not impress
- Articulate and don't be flowery
- Prefer active voice over passive voice
- Do not include a summary about the candidate

Improved CV:
"""

BASICS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Provide this as JSON with the following schema:
{
    "basics": {
        "name": string,
        "email": string,
        "phone": string,
        "website": string,
        "experienceInYears": string,
        "city": string
    }
    
}
Correct any incorrect formatting and remove undue whitespaces.
Ensure that the name, email, and experienceInYears fields are present.
Return the respective null for any missing fields.
Write the basics section according to the Basic schema in accordance with the JSON Resume Schema. On the response, include only the JSON.
DO NOT FORMAT THE JSON. Provide RAW JSON
"""

FINAL_THOUGHTS_PROMPT = """
<SYS>
Consider the given CV:

For the following Job Description:
<JD_TEXT>

Provide a holistic analysis of the given resume.
Highlight the strengths and weaknesses of the resume both independently and in relation to the job description.
Provide this response as a text and not JSON.
"""

EDUCATION_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface EducationItem {
    institution: string;
    area: string;
    additionalAreas: string[];
    studyType: string;
    startDate: string;
    endDate: string;
    score: string;
    location: string;
}

interface Education {
    education: EducationItem[];
}


Write the education section according to the Education schema. On the response, include only the JSON.
"""


PROJECTS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface ProjectItem {
    name: string;
    description: string;
    keywords: string[];
    url: string;
}

interface Projects {
    projects: ProjectItem[];
}

Write the projects section according to the Projects schema. Include all projects, but only the ones present in the CV.If there are no projects, return empty json. On the response, include only the JSON.
"""

SKILLS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

type HardSkills = "Programming Languages" | "Tools" | "Frameworks" | "Computer Proficiency";
type SoftSkills = "Team Work" | "Communication" | "Leadership" | "Problem Solving" | "Creativity";
type OtherSkills = string;

Now consider the following TypeScript Interface for the JSON schema:

interface SkillItem {
    name: HardSkills | SoftSkills | OtherSkills;
    keywords: string[];
}

interface Skills {
    skills: SkillItem[];
}

Write the skills section according to the Skills schema. Include only up to the top 6 skill names that are present in the CV and related with the education and work experience. On the response, include only the JSON.
"""

WORK_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface WorkItem {
    company: string;
    position: string;
    startDate: string;
    endDate: string;
    location: string;
    highlights: string[];
}

interface Work {
    work: WorkItem[];
}

Write a work section for the candidate according to the Work schema. Include only the work experience and not the project experience. For each work experience, provide  a company name, position name, start and end date, and bullet point for the highlights. Follow the Harvard Extension School Resume guidelines and phrase the highlights with the STAR methodology
"""


def generate_profile_json(uploaded_file):
    pdf_content=input_pdf_setup(uploaded_file)
    response=get_gemini_response(BASICS_PROMPT.replace("<SYS>",SYSTEM_PROMPT),pdf_content,None)
    json_out = str(response).replace('```json', '').replace('```', '').replace('JSON', '')
    json_out = json_out[json_out.find("{"):]
    json_response = json.loads(json_out)
    return json_response

def generate_matching_json(uploaded_file, job_description_text):
    pdf_content=input_pdf_setup(uploaded_file)
    response=get_gemini_response(MATCHING_PROMPT.replace("<SYS>",SYSTEM_PROMPT).replace("<JD_TEXT>",job_description_text),pdf_content,None)
    json_out = str(response).replace('```json', '').replace('```', '').replace('JSON', '')
    json_out = json_out[json_out.find("{"):]
    json_response = json.loads(json_out)
    return json_response

def generate_final_thoughts(uploaded_file, job_description_text):
    pdf_content=input_pdf_setup(uploaded_file)
    response=get_gemini_response(FINAL_THOUGHTS_PROMPT.replace("<SYS>",SYSTEM_PROMPT).replace("<JD_TEXT>",job_description_text),pdf_content,None)
    return response

def generate_missing_skills(uploaded_file, job_description_text):
    pdf_content=input_pdf_setup(uploaded_file)
    response=get_gemini_response(MISSING_SKILLS_PROMPT.replace("<SYS>",SYSTEM_PROMPT).replace("<JD_TEXT>",job_description_text),pdf_content,None)
    json_out = str(response).replace('```json', '').replace('```', '').replace('JSON', '')
    json_out = json_out[json_out.find("{"):]
    json_response = json.loads(json_out)
    return json_response

def generate_resources(uploaded_file, job_description_text):
    pdf_content=input_pdf_setup(uploaded_file)
    response=get_gemini_response(RESOURCES_PROMPT.replace("<SYS>",SYSTEM_PROMPT).replace("<JD_TEXT>",job_description_text),pdf_content,None)
    return response
