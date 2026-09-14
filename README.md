A Python desktop application with a PyQt5 GUI for exploring and analyzing Yelp business data, backed by a PostgreSQL database of 11,481 businesses.

Features:
- Location search: Filter businesses by state, city, and ZIP code
- Category filtering: Narrow results by business category (e.g. Restaurants, Nail Salons, Beauty & Spas)
- ZIP code statistics: View aggregate stats for a selected ZIP code, including number of businesses, average income, and total population
- Top categories: See the most common business categories in a given area, ranked by count
- Business details table: Browse name, address, city, star rating, review count, and average rating for matching businesses
- Popular businesses: Ranks businesses by check-in activity
- Successful businesses: Ranks businesses by a combination of average rating, review count, and check-ins

 <img width="700" height="600" alt="Screenshot 2026-09-14 145119" src="https://github.com/user-attachments/assets/0aabd18c-938c-493e-9cf3-f3706599ff2d" />
The app’s main view lets users narrow down from state -> city -> ZIP code, filter by category, and see results update across four linked panels (ZIP code stats, top categories, business listings, and popularity/success rankings).


Tech stack:
- Language: Python
- GUI framework: PyQt5
- Database: PostgreSQL
- Entry point: Milestone3App.py

Running the project:
1.	Clone the repository.

2.	Install dependencies (PyQt5, psycopg2 or equivalent PostgreSQL driver).

3.	Set up a PostgreSQL database with the Yelp business dataset and update the connection details in the project’s config/connection file.

4.	Run Milestone3App.py (e.g. via Visual Studio’s Run button, or python Milestone3App.py from the terminal.
