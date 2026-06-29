# RepoLens — GitHub Repository Intelligence Dashboard

RepoLens is a repository analysis dashboard that evaluates public GitHub repositories across **documentation quality, maintenance activity, community health, engineering practices, technology stack, and dependency signals**.

Instead of only showing stars or forks, RepoLens tries to answer a more useful question:

> **How healthy and well-engineered does this repository look?**

It uses the GitHub API plus recursive repository structure analysis to generate:
- an overall repository health score
- an engineering quality score
- detected technologies and libraries
- strengths, risks, and actionable recommendations

---

## Features

### Repository health analysis
RepoLens analyzes a public GitHub repository and produces:
- **overall repository score**
- **engineering quality score**
- **health verdict** (for example: Excellent / Good / Average / High Risk)
- **score breakdown** across multiple dimensions

### Engineering quality signals
The analyzer checks for signals such as:
- automated tests
- documentation resources
- CI/CD workflows
- Docker / dev-container support
- dependency management files

### Technology and dependency detection
RepoLens also infers:
- backend technologies
- frontend technologies
- infrastructure signals
- important libraries / frameworks from dependency files

### Dashboard visualization
The results are shown in a Streamlit dashboard with:
- score cards
- health summaries
- engineering review sections
- detected technologies and libraries
- radar and bar chart score breakdowns

---

## Example analysis dimensions

RepoLens scores repositories across several dimensions:

- **Documentation**
  - README quality
  - installation / usage / contributing signals

- **Activity**
  - recent maintenance
  - commit history
  - release activity

- **Community**
  - stars
  - forks
  - contributor count

- **Project hygiene**
  - description
  - topics
  - license
  - CI/CD presence

- **Issue health**
  - open issue load relative to project popularity

- **Engineering quality**
  - tests
  - docs
  - CI/CD
  - containerization
  - dependency management

---

## Project structure

```bash
RepoLens/
│
├── streamlit_app.py          
├── app.py                    
│
├── repository_structure.py   
├── engineering_signals.py    
├── engineering_review.py     
├── engineering_score.py      
├── technology_detector.py    
├── dependency_detector.py    
├── dependency_parser.py     
├── recommendations.py       
├── style.css                
├── requirements.txt
└── README.md