# Pool Rankings

**Pool Rankings** is a web application that calculates and manages player rankings for pool games using an Elo-based rating system. It includes tools for tracking player stats, updating results, and generating a real-time leaderboard.

## Purpose

This project began in my senior year of college and has evolved over the past two years. It's been my long-term learning playground for exploring full-stack development, improving my architecture and naming practices, and deploying containerized applications to the cloud.

## Features

- Track player profiles and match outcomes
- Calculate and update Elo ratings dynamically
- Generate ranked leaderboards
- Cloud-hosted, accessible from any device

## Technologies Used

- **Flask** – Web framework for backend and routing
- **Firebase Firestore** – NoSQL database for storing player data
- **Docker** – Containerized local and cloud deployment
- **Shell scripts** – Dev and deployment tooling
- **GitHub Copilot** – Used to improve workflow efficiency

## Live Demo

The application is currently hosted online. You can check it out here:  
[https://poolrankings.onrender.com/](https://poolrankings.onrender.com/)


## Local Development

This project is now hosted in the cloud and uses a managed database service (Firebase Firestore), so running it fully offline is no longer supported out-of-the-box. Support for local development may be added in a future update.

However, if you're interested in testing locally, you can:
- Clone the repo and run the app locally using Docker
- Use your own Firebase credentials by storing them in the ./Secrets folder and updating the Docker ENV variables.
> Note: Local development requires access to a Firebase project. If you'd like to test locally, consider creating a free Firebase project and updating the environment variables accordingly.

> Note: The run.sh script takes a "dev" or "prod" variable. This will run the application locally by running the docker compose file. The application will run on either the built in flask wsgi server (dev) or a gunicorn server (dev)
 
## Learn More

Curious about the evolution of this project, and the lessons I’ve learned along the way?  
[Read the development story »](PROJECT_STORY.md) _(optional)_

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.