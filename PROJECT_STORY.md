# Project Story: Pool Rankings

## Why I Started

I began building **Pool Rankings** during my senior year of college. At the time, I was a part of my universities billiards club and I wanted to build an application that we could use to keep track of our matches and our relative skill levels. My first iteration was a CLI application that only ran on my laptop. I quickly realized that we would need something more robust and thus I started this project. 

## Early Goals

Originally, the goal was to:
- Learn how to build a full-stack application from scratch
- Explore concepts like Elo rating systems and real-time updates
- Create a hands off experience that would allow members to compete with each other

## Iteration and Evolution

Over the past two years, I’ve returned to the project whenever life allowed—sometimes after long breaks. Each return brought new skills and a new perspective. As a result, **the project has been refactored multiple times** as my understanding of scalable code, clean naming, and maintainable architecture improved.

Key turning points:

- Dockerizing the application to support consistent environments across systems
- Transitioning to hosting locally
- Moving back to cloud service to ensure a live demo would be available
- Replacing the local database with a managed **Firebase Firestore** backend for cloud accessibility
- Learning to use GitHub Copilot to accelerate development while maintaining readability
- Refactoring code with better separation of concerns and cleaner routing logic

## The Start

In the beginning I had very limited experience, and none with production level code of any kind. In school I had undertaken projects that were hosted on AWS EC2 servers however, the environment was almost always defined for us ahead of time. This was the first time I would have to not only create a working application, but also ensure that the architecture that it sat on would work. This is what drew me to utilizing Docker. The idea of creating environments that could run either locally or on a cloud server was very appealing. I thought that it would let me quickly move past spending days configuring the server. To an extent it did but at the same time I just traded in learning one concept for another.

## First Attempt in the Cloud

I felt confident going into hosting the application on AWS. I started exploring all of the different services they offered, compute options, SQL and non-SQL databases, secret and environment configurations. In the past I had run tiny web servers for cents a month and I knew this application would be in the 10s of users if that. I believed that I would be able to spin something up and not think twice about it. This turned out to be a hard lesson learned once the first bill hit. After this I wanted to transition to a new hosting method. I needed a break from the cloud.

## Local Hosting

Once I had decided to host the application locally I had to dive back into the architecture set up. Because I was working in with Docker I knew I could spin up a few more containers to assist so that is where I started. I decided that in addition to my flask container I would also create a mongodb container and a nginx container so both host the database and the web server respectively. I spent a lot of time at this stage learning how to configure network settings to effectively pass data between thsese containers as well as mounting volumes so that each would have what it needed to work appropriately. At this stage I had my head down and was only focused on making it work. So much so that I could not see the forest from the trees. I was doing all this to be able to host a website that would be visible but if I host it locally then what? I did not have a static IP, nor did my ISP offer that. I did not have a certificate. If I continued down this path, I would have an insecure website hosting out of my apartment that no one would dare connect to. These issues could of course be solved but I found myself asking if this really was the best way.

## Going Back into the Cloud

Thus I found myself again searching for cloud options. The solution I landed on was using Google's Firebase Firestore for the database and using Render as the compute environment. Render has a free tier but having learned my lesson I ensured that billing limits were properly set this time. And so now with everything in place I can now run the live version of my application with minimum downtime


## Lessons Learned

- **Consistency > Perfection**: Long breaks can feel like lost time, but revisiting your own code months later is a powerful learning experience.
- **Start simple, evolve smart**: The original version was overly complex. Over time, I learned to value simplicity, readability, and modularity.
- **Deployment matters**: Building something is great—but making it accessible online made it feel real.
- **Documentation counts**: Clear README files and scripts saved me hours when returning after time away.
- **Progress is non-linear**: Every return brought fresh eyes and better practices—this project is a personal reminder that growth stacks slowly but surely.

## Current Status

The application is hosted online, with real-time data stored in Firestore and an interface built using Flask. It’s stable, and while there’s more I’d like to do with it (such as reintroducing local development support and enhancing UI), it’s in a place I’m proud of.

## Whats Next

I still have many ideas for the project. Some involve new functionality such as allowing for more types of matches or email notifications. Others are more Devops focused such as including testing in the deployment phase. I cannot guarentee when I will get to these changes however. I would like to work on other projects that are not full stack development and I also have found out that I have a kid on the way so it'll all be a balance of finding time to work on what projects. 

---

Thanks for reading, and feel free to explore the repo. If you’re a fellow developer, I’d love feedback—or just to connect.