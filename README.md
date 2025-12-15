# Local Lobe Chat

## Introduction
This is a small project that uses docker to host a local instance of LobeChat, enabling the additional power a wrapper like LobeChat provides (role configuration, file context, etc.) around the user's existing AI models (such as Gemini or Claude, linked with API keys).

In addition to the LobeChat container, 3 other containers are created to handle data storage and auth (postgres, minio, and logto). 

## Infrastructure Setup

### CLI
The following commands are used to deploy and remove the lobe chat service:
```
./cli up
./cli down
```

### Data Persistence
The settings, documents, and conversation history for Lobe Chat are stored in the two docker volumes specified in docker-compose. If these volumes are deleted then all persistent data will be wiped.

### Foundational Setup
Before getting into Lobe Chat and setting up the AI assistants themselves, two things must be done if the docker volumes are newly created. 

First, the minio instance must be accessed at http://localhost:9001 and a bucket named `lobechat` created. Then it must be set to public using the following command:
```
docker run --rm -it --network host --entrypoint=/bin/sh minio/mc -c "
  mc alias set myminio http://127.0.0.1:9000 minioadmin miniopass;
  mc anonymous set public myminio/lobechat
"
```

Next, the logto instance must be accessed and a user created, using the following steps:

1. Access the Admin Console: Open the browser and go to http://localhost:3002 (the Logto Admin UI).
2. Initial Setup: Follow the on-screen prompts to create the Administrator account for Logto itself.
3. Create the Application: * Navigate to Applications > Create Application.
    - Select Next.js (App Router) as the framework.
    - Name it "LobeChat".
4. Configure Redirects: In the Application settings, set the Redirect URI to http://localhost:3210/api/auth/callback/logto.
5. Get Credentials: Copy the App ID and App Secret and paste them into the .env
6. Add a User: Go to the User Management section in the Logto sidebar and click Add User. This is the account used to log into LobeChat.
7. run `./cli down` and `./cli up` so that lobe-chat reads the logto app id and secret

### Accessing LobeChat
Now that everything is set up, simply access LobeChat at http://localhost:3210 and sign in using the created user credentials. From here, LobeChat can also be installed as a PWA.

## LobeChat Settings