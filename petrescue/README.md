# Pet Adoption and Rescue Management Portal

## Project Statement and Outcomes
The "PetRescue" project aims to develop an interactive web platform that bridges the gap between individuals who find lost pets and their owners. The website will provide functionalities for users to raise requests regarding found pets, while admins can view and manage these requests to facilitate reunions. The platform will also allow users to check whether their lost pets have been reported on the website, thereby enhancing the chances of a reunion. The intuitive interface and structured data management will ensure a seamless experience for both users and admins.

The outcomes include a fully functional website built with HTML, CSS, Django, and MySQL, designed to support users and administrators. This platform will enhance pet recovery efforts, making it easier for pet owners to locate their pets and for finders to report them.

## Modules to be Implemented
- Database Design & User Management Module
- Pet Registration & Admin Management Module
- Pet Status Inquiry & Notification Module
- Testing, Review, and Documentation
wa
## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Django 4.0 or higher
- MySQL  database
- Git

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/petrescue.git
   cd petrescue
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   - For SQLite (default): No additional setup required.
   - For MySQL: Update settings.py with your database credentials and run migrations.

5. Run migrations:
   ```
   python manage.py migrate
   ```

### Running the Application
1. Start the development server:
   ```
   python manage.py runserver
   ```

2. Open your browser and navigate to `http://127.0.0.1:8000/`

### Additional Commands
- Create superuser: `python manage.py createsuperuser`
- Run tests: `python manage.py test`

## Week-wise Module Implementation and High-Level Requirements
### Weeks 1-2: Database Design & User Management Module
- Design appropriate relational databases needed to fulfill the requirement.
- Set up a database to store Users, Pets, etc.
- Develop APIs and Pages for User Registration & Login functionalities.

## Weeks 3-4: Pet Registration &amp; Admin Management Module
- Develop APIs for users to raise a request for found pets or lost pets.
- Include input fields for pet details such as type, breed, color, location found, and
contact information.
- Allow admins to update request statuses (e.g., &quot;Accepted&quot; , “Rejected”).

## Weeks 5-6: Pet Status Inquiry &amp; Notification Module
- Implement a search feature for users to check if their lost pet has been reported.
- Create a functional back-end using Django to handle requests and responses.
- Enable admin notifications to streamline communication with users who raised
requests.