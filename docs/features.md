# List of features
- add skills to an existing repo (first item to implement)
    - have a list of predefined curated skills
    - initial command is simply `devpack add-skills <repo_path>` (e.g. `devpack add-skills .`)
    - flow: 
        1. tool examines repo
        2. identifies stack 
        3. goes through the list of skills and sees which ones are applicable
        4. presents list to user (all selected by default)
        5. user confirms which ones they want to add
        6. tool asks which IDE/agent to generate for (cursor, vscode, claude code)
        7. Tool automatically adds all the skills in the proper format for the chosen coding tool


- initialize (scaffold a new project)
    - choose type of project (Django, fastapi, express, fastify, hono, koa, next.js, react-vite, vue-vite)
    - ask framework specific questions: 
        - frontend specific: 
            - which router, which css library, component library, data fetching helpers, add theme, linter
        - backend specific: 
            - which DB if any, which ORM if applicable, rest vs something else, auth setup?, add dockerfile, dependency managemeng?
    - general questions:
        - add pre-commits, add linting tools, add agent skills?

 