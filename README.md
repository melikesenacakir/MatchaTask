# MatchaTask

MatchaTask is a data-driven task assignment and project management platform designed to optimize team productivity by matching tasks with the most suitable team members using AI-powered analysis.

---

## Table of Contents

- [Purpose](#purpose)
- [Features](#features)
  - [Skill Pool](#skill-pool)
  - [Project Management](#project-management)
  - [Task Assignment](#task-assignment)
  - [User Contribution Analytics](#user-contribution-analytics)
- [Tech Stack](#tech-stack)
- [Roles & Permissions](#roles--permissions)
  - [Manager](#manager)
  - [Team Member](#team-member)
  - [Team Lead](#team-lead)
- [Installation & Usage](#installation--usage)
- [Contributors](#contributors)
- [Collaboration & Tools](#collaboration--tools)
- [License](#license)

---

## Purpose

MatchaTask was developed to **standardize task assignment processes** within teams through a **data-driven approach**, minimizing subjective evaluation errors caused by human factors.

The system evaluates team members’ technical competencies and professional experience extracted from their CVs using **AI-powered analysis**, providing a **dynamic task management ecosystem** that matches each task with the most suitable team member.

The primary objective is to automatically align **project requirements and technology stacks** with team members’ technical skills, accelerating task assignment processes and ensuring **maximum operational efficiency**.

---

## Features

MatchaTask’s interface is designed to transform complex data analysis into a **simple, scalable, and manageable user experience**. The system consists of the following core modules.

---

### 💎 Skill Pool

The module where team members’ skill profiles are stored either manually or via **AI-powered CV upload**.

- **CV-to-Skill Mapping:** Uploaded CVs are automatically parsed and converted into structured *Skill Cards*.
- **Expertise Visualizations:** Visual competency matrices display experience levels across different technologies.
- **Niche Skill Discovery:** Identifies secondary or hidden skills that may add value to projects (e.g., a Data Engineer with UI design skills).

---

### 🏗 Project Management

The module where projects are created, structured, and initial tasks are defined. Tasks can be assigned manually or through **AI-based automatic recommendations**.

- **Technology Stack Definition:** Configuration of programming languages, frameworks, and tools (Frontend, Backend, AI, etc.).
- **Flexible Workflow Design:** Hierarchical structuring of project phases and their associated sub-tasks.
- **Resource Planning:** Correlation of project timelines with team member availability.

---

### 📋 Task Assignment

The operational module responsible for managing tasks and analyzing **skill-to-task compatibility**.

- **Intelligent Match Score:** Real-time calculation of suitability percentages for each candidate based on technical skills.
- **AI-Assisted Assignment:** Semantic similarity analysis between task requirements and skill sets to provide optimal assignment recommendations.
- **Real-Time Progress Tracking:** Interactive dashboard for tracking task statuses (To Do, In Progress, Done).

---

### 📈 User Contribution Analytics

A reporting module that provides **transparent and measurable insights** into individual and team contributions.

- **Performance Metrics:** Visualizations based on completed tasks, task complexity, and delivery times.
- **Skill Development Tracking:** Reports newly acquired skills and areas of active contribution throughout the project lifecycle.
- **Contribution Heatmap:** Dynamic heatmaps illustrating contribution intensity across the project.

---

## Tech Stack

- **Frontend:** React, Material UI  
- **Backend:** .NET Core  
- **Database:** PostgreSQL  
- **AI & Data Analysis:** Python, NLP-based skill matching  
- **Containerization:** Docker, Docker Compose  

---

## Roles & Permissions

MatchaTask employs a role-based authorization model to ensure clear separation of responsibilities. The system is structured around three primary roles: **Manager**, **Team Lead**, and **Team Member**.

---

### Manager

Responsible for high-level project oversight without direct involvement in operational processes.

**Permissions**
- Create new projects
- Assign or change team leads
- View all projects created by their team
- View project details (team leads, members, statistics)

**Restrictions**
- Cannot create tasks
- Cannot assign tasks to members
- Cannot modify projects, tasks, or team members
- Read-only access

---

### Team Member

Responsible for executing assigned tasks and contributing to the project.

**Permissions**
- View and update assigned tasks (To Do, In Progress, Done)
- View all tasks within the project
- View skill–task compatibility scores (Match Score) for tasks not assigned to them
- Request tasks
- Submit completed tasks for review
- Edit profile information
- View previously completed tasks filtered by project
- View personal contribution metrics
- Review skill compatibility of completed tasks; successfully completed tasks with low initial compatibility are added as new skills
- Access a personal dashboard displaying:
  - Active tasks
  - Upcoming deadlines
  - Daily scrum activities

---

### Team Lead

The role closest to daily operations, responsible for project and task management.

**Permissions**
- Create new projects (automatically assigned as team lead)
- Add or remove team members
- Create tasks
- Assign tasks:
  - Manually
  - Automatically (AI-assisted)
- Accept, reject, or reassign task requests
- Review completed tasks and forward approved ones to testing
- Monitor scrum timelines
- View team progress and contribution analytics

**Shared Visibility**
- Task and progress boards are visible to managers, team leads, and team members.

---

This role-based structure enables MatchaTask to provide both **transparent tracking** and **controlled task orchestration**.

---

## Installation & Usage

```bash
git clone https://github.com/melikesenacakir/MatchaTask.git
cd MatchaTask
docker compose up
```
---
## Contributors

| Name | Primary Focus | Shared Responsibilities |
|------|---------------|-------------------------|
| **Melike Sena Çakır** | Full-Stack Development, System Architecture | Data Analysis, AI Matching Logic, Documentation, System Design, Task Assignment Logic |
| **Betül Güner** | Data Analysis, Skill–Task Matching Models | Full-Stack Development, Documentation, System Design, UI/UX Decisions |

---

## Collaboration & Tools

- Analysis, design, and documentation processes were conducted **collaboratively** by the team.
- **Stitch AI** was used as a supporting tool during UI design and visual component creation.

---

## License

This project is licensed under the  
**Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

Commercial use is strictly prohibited.  
Attribution to the MatchaTask team is mandatory.

For more details, see the [LICENSE](LICENSE) file.
